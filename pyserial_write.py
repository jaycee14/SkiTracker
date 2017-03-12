import serial

port = '/dev/cu.usbmodem411'

ser = serial.Serial(port,115200)

with open('dataOut.csv', 'a') as the_file:
	while True:
		message = ser.readline()
		message = message.rstrip()
		print(message)
		the_file.write(message+'\n')