from machine import UART, Pin

uart=UART(1,baudrate=115200,bits=8,parity=None,stop=1,tx=Pin(2),rx=Pin(1))

while True:
    if uart.any():
        print(uart.readline())