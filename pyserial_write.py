import serial

#Have this code ready to go, upload script to feather and then run this script

#port = '/dev/cu.usbmodem411'
port = '/dev/ttyACM0'

ser = serial.Serial(port,115200)

with open('dataOut.csv', 'a') as the_file:
	while True:
		message = ser.readline()
		message = message.rstrip()
		print(message)
		the_file.write(message.decode('ascii')+'\n')