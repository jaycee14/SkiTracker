import asyncio
import as_GPS
from machine import UART, Pin

def callback(gps, *_):  # Runs for each valid fix
    print(gps.latitude(), gps.longitude(), gps.altitude, gps.speed())

uart=UART(1,baudrate=115200,bits=8,parity=None,stop=1,tx=Pin(2),rx=Pin(1))

sreader = asyncio.StreamReader(uart)  # Create a StreamReader
gps = as_GPS.AS_GPS(sreader, fix_cb=callback)  # Instantiate GPS

async def test():
    print('waiting for GPS data')
    await gps.data_received(position=True, altitude=True)
    await asyncio.sleep(60)  # Run for one minute

asyncio.run(test())