from machine import RTC

def make_filename():
	
	rtc = RTC()
	dt = rtc.datetime()
	
	return f'ski_{dt[0]}_{dt[1]:02}_{dt[2]:02}_{dt[4]:02}{dt[5]:02}.csv'

def gps_string(data):
	return f'{data[0]}{data[1]}'

def utc_string(data):
	return f'{data[0]:02}:{data[1]:02}.{data[2]:02}'

def float_string(data):
	return f'{data}'

def csv_string(data_list):
	return ','.join(data_list)
