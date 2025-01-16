# micropyGPS Sentence Test
# When properly connected to working GPS module,
# will print the names of the sentences it receives
# If you are having issues receiving sentences, use UART_test.py to ensure
# your UART is hooked up and configured correctly

from machine import UART, Pin
from micropyGPS import MicropyGPS

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
