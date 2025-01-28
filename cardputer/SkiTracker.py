import os
import machine
import time
from machine import SDCard, UART, Pin, RTC

import asyncio
import as_GPS

from lib.display import Display
from lib.hydra.config import Config
#from lib.userinput import UserInput
from font import vga2_16x32 as font


try:
    from SkiTracker_utils import make_filename, gps_string, csv_string, utc_string, float_string
except ImportError:
    from apps.Skitracker.SkiTracker_utils import make_filename, gps_string, csv_string, utc_string, float_string

config = Config()
BG_COLOUR = config.palette[2]
FG_COLOUR = config.palette[10]

class SkiData():
	
	numRecords=10
	totalRecords=0
	records=[]
	path = '/sd/ski_data/'
	
	def __init__(self,filename):
		self.filename=self.path + filename
		print(self.filename)
		
	def add_data(self,gps):
		lat_string = gps_string(gps.latitude(coord_format=as_GPS.DD))
		lon_string = gps_string(gps.longitude(coord_format=as_GPS.DD))
		items=[lat_string,
               lon_string,
               float_string(gps.altitude),utc_string(gps.utc)]
        
		self.records.append(csv_string(items))
		
		if len(self.records) > self.numRecords:
			self.save_data()
			
			self.totalRecords+=self.numRecords
			
			stats=[float_string(gps.pdop),
                   float_string(gps.hdop),
                   float_string(gps.vdop),
                   float_string(gps.satellites_in_use)]
			stats_string = csv_string(stats)
			#print(csv_string(items))
			display_values(lat_string,lon_string,stats_string,str(self.totalRecords))
		
	def save_data(self):
		
		#print('saving data')
		output = '\n'.join(self.records) + '\n'
		self.records=[]
		
		with open(self.filename,'a') as fp:
			fp.write(output)
			#fp.flush()
			
def callback(gps, *_):  # Runs for each valid fix
    data.add_data(gps)

def display_values(lat_string,lon_string,stats_string,records):
    
    display.fill(BG_COLOUR)
    display.text(
            lat_string,
            0, #X
            0, # Y
            FG_COLOUR,
            font=font
            )
    display.text(
            lon_string,
            0, #X
            font.HEIGHT * 1, # Y
            FG_COLOUR,
            font=font
            )
    display.text(
            stats_string,
            0, #X
            font.HEIGHT * 2, # Y
            FG_COLOUR,
            font=font
            )
    display.text(
            records,
            0, #X
            font.HEIGHT * 3, # Y
            FG_COLOUR,
            font=font
            )
    display.show()

sd = SDCard(slot=2, sck=Pin(40), miso=Pin(39), mosi=Pin(14), cs=Pin(12))
uart=UART(1,baudrate=115200,bits=8,parity=None,stop=1,tx=Pin(2),rx=Pin(1))

display=Display(use_tiny_buf=True)
display.fill(BG_COLOUR)

sreader = asyncio.StreamReader(uart)  # Create a StreamReader
gps = as_GPS.AS_GPS(sreader, fix_cb=callback)  # Instantiate GPS

fname = make_filename()

data = SkiData(filename=fname)

os.mount(sd, '/sd')

async def run_loop():
    
    display.text(
        'SkiTracker v3',
        0, #X
        0, # Y
        FG_COLOUR,
        font=font
        )
    display.text(
        'Awaiting GPS...',
        0, #X
        font.HEIGHT * 1, # Y
        FG_COLOUR,
        font=font
        )
    display.show()
    #print('waiting for GPS data')
    while True:
        await gps.data_received(position=True, altitude=True)

try:
	asyncio.run(run_loop())
except KeyboardInterrupt:
	print('Interupt')
finally:
	os.umount('/sd')

#from machine import SDCard, UART, Pin
#sd = SDCard(slot=2, sck=Pin(40), miso=Pin(39), mosi=Pin(14), cs=Pin(12))
#import os; os.mount(sd, '/sd')
#os.umount('/sd')

