import os
import machine
import time
from machine import SDCard, UART, Pin, RTC

import asyncio
import as_GPS

try:
    from SkiTracker_utils import make_filename, gps_string, csv_string, utc_string, float_string
except ImportError:
    from apps.Skitracker.SkiTracker_utils import make_filename, gps_string, csv_string, utc_string, float_string

sd = SDCard(slot=2, sck=Pin(40), miso=Pin(39), mosi=Pin(14), cs=Pin(12))
uart=UART(1,baudrate=115200,bits=8,parity=None,stop=1,tx=Pin(2),rx=Pin(1))

class SkiData():
	
	numRecords=10
	records=[]
	path = '/sd/ski_data/'
	
	def __init__(self,filename):
		self.filename=self.path + filename
		print(self.filename)
		
	def add_data(self,data):
		self.records.append(data)
		
		if len(self.records) > self.numRecords:
			self.save_data()
		
	def save_data(self):
		
		print('saving data')
		output = '\n'.join(self.records) + '\n'
		self.records=[]
		
		with open(self.filename,'a') as fp:
			fp.write(output)
			#fp.flush()
			
		


def callback(gps, *_):  # Runs for each valid fix
	items=[gps_string(gps.latitude(coord_format=as_GPS.DD)),
		   gps_string(gps.longitude(coord_format=as_GPS.DD)),
		   float_string(gps.altitude),utc_string(gps.utc)]
	
	print(csv_string(items))
	data.add_data(csv_string(items))



sreader = asyncio.StreamReader(uart)  # Create a StreamReader
gps = as_GPS.AS_GPS(sreader, fix_cb=callback)  # Instantiate GPS

fname = make_filename()

data = SkiData(filename=fname)

os.mount(sd, '/sd')

async def test():
    print('waiting for GPS data')
    await gps.data_received(position=True, altitude=True)
    await asyncio.sleep(30)  # Run for one minute

asyncio.run(test())

os.umount('/sd')

#from machine import SDCard, UART, Pin,
#sd = SDCard(slot=2, sck=Pin(40), miso=Pin(39), mosi=Pin(14), cs=Pin(12))
#import os; os.mount(sd, '/sd')
#os.umount('/sd')
