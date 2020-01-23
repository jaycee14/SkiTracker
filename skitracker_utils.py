from datetime import datetime
import json
import os
from math import degrees, atan, sin, cos, atan2, sqrt
from math import radians

import gpxpy.gpx
import luigi
import numpy as np
import pandas as pd

CLIP_LEVEL = 1.0e-06


class ProcessTask(luigi.Task):
    file_name = luigi.Parameter()
    inputDir = luigi.Parameter()
    outputDir = luigi.Parameter()

    def requires(self):
        path = self.inputDir + self.file_name
        return RawFile(path)

    def get_new_file_name(self):
        return self.file_name.split('.')[0]

    def output(self):
        new_file_name = self.get_new_file_name() + '.pkl'
        return luigi.LocalTarget(self.outputDir + new_file_name)

    def run(self):
        # transformation step
        raw = pd.read_pickle(self.input().path)
        df = prepare_data(raw)
        runs = find_routes(df)

        new_file = self.get_new_file_name()
        save_gpx_run(runs, new_file)
        save_json_run(runs, new_file)

        df.to_pickle(self.output().path)


class RawFile(luigi.ExternalTask):
    path = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.path)


class ProcessDirectory(luigi.WrapperTask):
    inputDir = luigi.Parameter()
    outputDir = luigi.Parameter()

    def requires(self):
        tasks = []
        for file_name in os.listdir(self.inputDir):
            if file_name.endswith('pkl'):
                tasks.append(ProcessTask(file_name=file_name, inputDir=self.inputDir, outputDir=self.outputDir))

        return tasks


def remove_zeros(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[~(df.GPS_Alt == 0)].copy()


def prepare_data(raw):
    # raw = raw[1:]

    raw = remove_zeros(raw)

    raw['Lat_Rad'] = raw.Lat.apply(lambda x: radians(x))
    raw['Lon_Rad'] = raw.Lon.apply(lambda x: radians(x))

    raw['Lat_Delta'] = raw.Lat[:-1] - raw.Lat[1:].values  # current value minus next value
    raw['Lon_Delta'] = raw.Lon[:-1] - raw.Lon[1:].values
    raw['Lat_Rad_Delta'] = raw.Lat_Rad[:-1] - raw.Lat_Rad[1:].values
    raw['Lon_Rad_Delta'] = raw.Lon_Rad[:-1] - raw.Lon_Rad[1:].values

    data = raw[(abs(raw.Lat_Delta) > CLIP_LEVEL) | (abs(raw.Lon_Delta) > CLIP_LEVEL)].copy()

    data['GPS_Alt_Delta'] = data.GPS_Alt[1:] - data.GPS_Alt[:-1].values  # next value minus current
    data['Pres_Alt_Delta'] = data.Pres_Alt[1:] - data.Pres_Alt[:-1].values  # next value minus current

    data['datetime'] = data.apply(make_datetime, axis=1)
    data['time_delta'] = data.datetime[1:] - data.datetime[:-1].values

    data['distance'] = data.apply(calc_distance, axis=1)
    data['distance_cum'] = data.distance.cumsum()

    data['speed'] = data.distance / (data.time_delta.values.astype(float) / 1000000000)

    data['gradient'] = data.apply(calc_gradient, axis=1, vert_field='GPS_Alt_Delta')
    data['pres_gradient'] = data.apply(calc_gradient, axis=1, vert_field='Pres_Alt_Delta')

    data['grad_roll'] = data.gradient.rolling(5).mean()

    data['grad_colour'] = data.apply(calc_grad_roll_colour, axis=1, grad_field='grad_roll')

    return data


def find_routes(data):
    data.reset_index(drop=True, inplace=True)

    data['gps_alt_roll'] = data.GPS_Alt.rolling(400).mean()
    data['pres_alt_roll'] = data.Pres_Alt.rolling(400).mean()

    # data['gps_alt_roll_delta'] = data.gps_alt_roll[:-1] - data.gps_alt_roll[1:].values
    data['gps_alt_raw_delta'] = data.GPS_Alt[:-1] - data.GPS_Alt[1:].values

    # data['pres_alt_roll_delta'] = data.pres_alt_roll[:-1] - data.pres_alt_roll[1:].values
    data['pres_alt_raw_delta'] = data.Pres_Alt[:-1] - data.Pres_Alt[1:].values

    data['gps_alt_raw_delta_roll'] = data.gps_alt_raw_delta.rolling(180).mean()
    # data['gps_alt_roll_delta_roll'] = data.gps_alt_roll_delta.rolling(180).mean()

    data['pres_alt_raw_delta_roll'] = data.pres_alt_raw_delta.rolling(180).mean()
    # data['pres_alt_roll_delta_roll'] = data.pres_alt_roll_delta.rolling(180).mean()

    signs = np.sign(data.gps_alt_raw_delta_roll.fillna(0))
    signchange = ((np.roll(signs, 1) - signs) != 0).astype(int)

    sign_changes_idx = signchange.index[signchange == 1].tolist()

    routes_list = []
    for i in range(len(sign_changes_idx) - 1):
        # print(sign_changes_idx[i],sign_changes_idx[i+1]-1, signs[sign_changes_idx[i]])
        start = sign_changes_idx[i]
        end = sign_changes_idx[i + 1] - 1
        sign = signs[sign_changes_idx[i]]
        max_val = np.max(data.loc[start:end, ('gps_alt_raw_delta_roll')])
        routes_list.append((start, end, sign, max_val))

    routes = pd.DataFrame(routes_list, columns=['start_idx', 'end_idx', 'sign', 'peak'])

    peak_filter = 0.5
    runs = routes[(routes.sign == 1) & (routes.peak >= peak_filter)].copy()
    runs.reset_index(inplace=True)

    num_runs = runs.shape[0]
    runs_data = []
    for i in range(num_runs):
        run = {}
        start = np.int(runs.loc[i].start_idx)
        end = np.int(runs.loc[i].end_idx)
        run_data = data.loc[start:end].copy()
        run['run_data'] = run_data

        total_height = run_data.GPS_Alt.max() - run_data.GPS_Alt.min()
        total_distance = run_data.distance.sum()
        run['scale'] = total_distance / total_height

        runs_data.append(run)

    return runs_data


def make_datetime(row):
    date_time_str = row.Date + row.Time
    return datetime.strptime(date_time_str, "%m/%d/%Y %H:%M:%S ")


def save_gpx_run(runs, file_name):
    gpx = gpxpy.gpx.GPX()
    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    for run in runs:
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        run_data = run['run_data']

        points = run_data[['Lat', 'Lon', 'GPS_Alt']].values
        # create points
        for point in points:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(point[0], point[1], elevation=point[2]))

    xml = gpx.to_xml()

    out_filename = file_name + '_gpx.xml'
    with open('gpx_files/' + out_filename, 'w') as f:
        f.write(xml)


def normalise_run(values):
    diff = values.max() - values.min()
    values = (values - values.min()) / diff
    return values


def save_json_run(runs, file_name):
    for i, run in enumerate(runs):
        run_data = run['run_data']

        # values = run_data[['Lat', 'Lon', 'GPS_Alt', 'grad_colour']].copy()
        run_data.rename(columns={'Lat': 'x', 'Lon': 'y', 'GPS_Alt': 'z', 'grad_colour': 'c'}, inplace=True)

        colours = run_data['c'].copy()

        values = normalise_run(run_data[['x', 'y', 'z']])

        out_data = pd.concat((values, colours), axis=1)

        json_values = out_data.to_dict(orient='records')

        json_data = {}
        json_data['scale'] = run['scale']
        json_data['values'] = json_values

        out_filename = '{}_{}.json'.format(file_name, i)
        with open('json_files/' + out_filename, 'w') as f:
            json.dump(json_data, f)


def calc_distance(row):
    dlat = row['Lat_Rad_Delta']
    dlon = row['Lon_Rad_Delta']
    lat1 = row['Lat_Rad']
    lat2 = row['Lat_Rad'] + dlat
    # calc haversine distance
    R = 6373000.0

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def clip(x):
    if x == 0.0 or x is None:
        return 0.00001
    else:
        return x


def calc_gradient(row, vert_field):
    dist = clip(row['distance'])
    height = clip(row[vert_field])

    return degrees(atan(dist / height))


def calc_grad_colour(row, grad_field):
    grad = row[grad_field]

    if grad >= 3.0:
        return 0  # '#FF0000' #red
    elif grad >= -5.0:
        return 1  # '#00FF00' #green
    else:
        return 2  # '#0000FF' #blue


def calc_grad_roll_colour(row, grad_field):
    grad = row[grad_field]

    if grad >= -25.0:
        return 1  # green
    elif grad >= -75.0:
        return 0  # red
    else:
        return 2  # blue


class InFile(object):
    """class to do pre-processing for a inout file

        https://stackoverflow.com/questions/52153414/how-to-pre-process-data-before-pandas-read-csv
    """

    def __init__(self, infile):
        self.infile = open(infile)

    def __next__(self):
        return self.next()

    def __iter__(self):
        return self

    def read(self, *args, **kwargs):
        return self.__next__()

    def next(self):
        try:
            line: str = self.infile.readline()
            line = line[1:-1] # do some fixing
            return line
        except:
            self.infile.close()
            raise StopIteration
