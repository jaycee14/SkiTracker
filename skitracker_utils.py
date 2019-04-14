from math import degrees, atan, sin, cos, atan2, sqrt

import gpxpy.gpx
import numpy as np
import json
import pandas as pd


def save_gpx_run(data, runs, name, date):
    gpx = gpxpy.gpx.GPX()
    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    num_runs = runs.shape[0]

    for i in range(num_runs):
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        start = np.int(runs.loc[i].start_idx)
        end = np.int(runs.loc[i].end_idx)
        # print(start, end)
        run_data = data.loc[start:end].copy()

        points = run_data[['Lat', 'Lon', 'GPS_Alt']].values

        # create points
        for point in points:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(point[0], point[1], elevation=point[2]))

    xml = gpx.to_xml()

    # filename = '{}_{}_{}.xml'.format(name,date.strftime('%d%b%y'),i)
    filename = '{}_{}_runs.xml'.format(name, date.strftime('%d%b%y'))
    print(filename)
    with open('gpx_files/' + filename, 'w') as f:
        f.write(xml)


def normalise_run(values):
    diff = values.max() - values.min()
    values = (values - values.min()) / diff
    return values


def save_json_run(data, runs, name, date):
    num_runs = runs.shape[0]

    for i in range(num_runs):
        start = np.int(runs.loc[i].start_idx)
        end = np.int(runs.loc[i].end_idx)
        run_data = data.loc[start:end].copy()


        values = run_data[['Lat', 'Lon', 'GPS_Alt', 'grad_colour']].copy()
        values.rename(columns={'Lat': 'x', 'Lon': 'y', 'GPS_Alt': 'z', 'grad_colour': 'c'}, inplace=True)

        colours = values['c'].copy()

        values = normalise_run(values[['x','y','z']])

        out_data = pd.concat((values,colours), axis=1)

        json_values = out_data.to_dict(orient='records')

        filename = '{}_{}_{}.json'.format(name, date.strftime('%d%b%y'), i)
        print(filename)
        with open('json_files/' + filename, 'w') as f:
            json.dump(json_values, f)


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


def calc_gradient(row):
    dist = clip(row['distance'])
    height = clip(row['GPS_Alt_Delta'])

    return degrees(atan(dist / height))


def calc_grad_colour(row):
    grad = row['gradient']

    if grad >= 3.0:
        return 0  # '#FF0000' #red
    elif grad >= -5.0:
        return 1  # '#00FF00' #green
    else:
        return 2  # '#0000FF' #blue
