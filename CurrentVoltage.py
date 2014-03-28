import serial
import time
import sys
import threading
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import mlab as mlab
import matplotlib.dates as mld
import datetime
import struct
import pdb

# global
ydata = np.zeros(int(sys.argv[2]))
line = plt.plot(ydata)
baudrate = 115200

# class for thread with arguments
class FuncThread(threading.Thread):
	def __init__(self, target, *args):
		self._target = target
		self._args = args
		threading.Thread.__init__(self)

	def run(self):
		self._target(*self._args)
        
# plot one value
def plot():
	try:
		line.set_xdata(np.arange(len(ydata)))
		line.set_ydata(ydata)
		plt.draw()
	except:
		sys.exc_info()[0]
            
# read from serial port
def read(seconds, ydata):
	port = serial.Serial('/dev/ttyACM0', baudrate, timeout=1)
	#~ abc  = open('data.vtg', 'w+')  
	start = time.time()
	last  = 0
	dta = []
    
	while (float(time.time() - start)) < float(seconds):
		if int(time.time() - int(start)) > last:
			print int(seconds) - last
			last = last + 10

		t = datetime.datetime.now()
		x = port.read(2000)
		buf = struct.unpack('2000B',x)
		dta.append((t,buf))
				
		print np.max(ydata)
		try:
			ydata = np.concatenate( (ydata, buf) )[len(buf):]
			#~ abc.write(str(mpStamp) + "," + x + "\n")
		except:
			print "error"
	
	#~ abc.close()
	port.close()
	print("finished reading")
	np.save('data.npy',dta)
	

t1 = FuncThread(read, sys.argv[1], ydata)
t1.start()
time.sleep(1)

plt.ion()
ax1=plt.axes()
line, = plt.plot(ydata)
plt.ylim([0,40])

while t1.isAlive():
	plot()



f = open('data.vtg', 'r')
lastValue = 0.0

# reference voltage
refVol = 1.5
# accuracy is 10bit, 0 to 1023
maxVal = 4096
# resistance
res = 10.0
# compute the scale multiplikator for the data 
# (in words this is what a 1 on the serial port would stand for)
multiplikator = (refVol / maxVal) / res
# at the start the area is 0
area = 0
# for now aequidistant steps of one second

count = 0
for line in f:
	value = line.split(",")[1]
	try:
		# scale the data
		value = multiplikator * float(value)
		# compute the area
		area = area + (((lastValue + value) / 2))
		lastValue = value
		count = count + 1
	except:
		pass

if count > 0:
	secondsPerValue = float(sys.argv[1]) / count
	area = area * secondsPerValue
	print area
else:
	print("no values")
