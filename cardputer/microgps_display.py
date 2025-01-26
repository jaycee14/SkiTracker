# micropyGPS Sentence Test
# When properly connected to working GPS module,
# will print the names of the sentences it receives
# If you are having issues receiving sentences, use UART_test.py to ensure
# your UART is hooked up and configured correctly

import time
from machine import UART, Pin
from micropyGPS import MicropyGPS

from lib.display import Display
from lib.hydra.config import Config
from lib.userinput import UserInput
from font import vga2_16x32 as font


display=Display(use_tiny_buf=True)
config = Config()
display.fill(config.palette[2])
WAIT_TIME_SECS = 1

uart=UART(1,baudrate=115200,bits=8,parity=None,stop=1,tx=Pin(2),rx=Pin(1))

# Instatntiate the micropyGPS object
my_gps = MicropyGPS()

# Continuous Tests for characters available in the UART buffer, any characters are feed into the GPS
# object. When enough char are feed to represent a whole, valid sentence, stat is set as the name of the
# sentence and printed
while True:
    if uart.any():
        line_bytes = uart.readline()
        for x in line_bytes.decode('utf-8'):
            stat = my_gps.update(x) # Note the conversion to to chr, UART outputs ints normally
            #if stat:
            #    print(stat)
            #    stat = None
                
        print(my_gps.latitude,my_gps.longitude)
        print(my_gps.satellites_in_use)
        print('fix type: ',my_gps.fix_type)
        print('hdop',my_gps.hdop)
        print('vdop',my_gps.vdop)
        print('pdop',my_gps.pdop)
        
        lat_text = 'Lat: {}'.format(my_gps.latitude_string())
        lon_text = 'Lon: {}'.format(my_gps.longitude_string())
        fix_text =  'Fix: {}'.format(my_gps.fix_type)
        sats_text =  'Num sats: {}'.format(my_gps.satellites_in_use)
        
        display.fill(config.palette[2])
        display.text(
				lat_text,
				0, #X
				font.HEIGHT * 0, # Y
				config.palette[10],
				font=font
                )
        display.text(
				lon_text,
				0, #X
				font.HEIGHT * 1, # Y
				config.palette[10],
				font=font
                )
        display.text(
				fix_text,
				0, #X
				font.HEIGHT * 2, # Y
				config.palette[10],
				font=font
                )
        display.text(
				sats_text,
				0, #X
				font.HEIGHT * 3, # Y
				config.palette[10],
				font=font
                )
        
        display.show()
        time.sleep(WAIT_TIME_SECS)

