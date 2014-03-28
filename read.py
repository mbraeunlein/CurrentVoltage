import sys
import serial
import time
import datetime
import struct
import numpy as np
import pdb

baudrate = 115200
seconds = sys.argv[1]
start = time.time()
last  = 0
dta = []
dtamn = []
interval = 2000
ydata = np.zeros(interval)

port = serial.Serial('/dev/ttyACM0', baudrate, timeout=1)

while (float(time.time() - start)) < float(seconds):
	if int(time.time() - int(start)) > last:
		print int(seconds) - last
		last = last + 10

	t = datetime.datetime.now()
	buf = np.int_([port.readline().strip() for i in range(interval)])
	
	#~ x = port.read(interval)
	#~ buf = struct.unpack('2000B',x)
	
	dta.append((t,buf))
	dtamn.append(np.mean(buf))
	try:
		ydata = np.concatenate( (ydata, buf) )[len(buf):]
	except:
		print "error"
	
port.close()
print("finished reading")
np.save('data-132.npy',dta)
np.save(sys.argv[2],dtamn)
