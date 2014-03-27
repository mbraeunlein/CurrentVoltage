import sys
import serial
import time
import datetime
import struct
import numpy as np

baudrate = 115200
seconds = sys.argv[1]
start = time.time()
last  = 0
dta = []
interval = 2000
ydata = np.zeros(interval)

port = serial.Serial('/dev/ttyACM0', baudrate, timeout=1)

while (float(time.time() - start)) < float(seconds):
	if int(time.time() - int(start)) > last:
		print int(seconds) - last
		last = last + 10

	t = datetime.datetime.now()
	x = port.read(interval)
	buf = struct.unpack('2000B',x)
	dta.append((t,buf))
				
	try:
		ydata = np.concatenate( (ydata, buf) )[len(buf):]
	except:
		print "error"
	
port.close()
print("finished reading")
np.save('data.npy',dta)
