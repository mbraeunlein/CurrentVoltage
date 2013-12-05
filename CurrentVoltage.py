import serial
import time
import sys
import threading
import numpy as np
from matplotlib import pyplot as plt

ydata = [0] * int(sys.argv[2])


class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
 
    def run(self):
        self._target(*self._args)
 
 
def plot():
    plt.ion()
    ax1=plt.axes()
    line, = plt.plot(ydata)
    plt.ylim([0,40])
    
    while True:
        try:
            line.set_xdata(np.arange(len(ydata)))
            line.set_ydata(ydata)
            plt.draw()
        except:
            pass
            

def read(seconds):
    port = serial.Serial('/dev/ttyUSB0', 115200)
    abc=open('data.txt', 'w+')  
    start = time.time()
    last = 0
    
    while (float(time.time() - start)) < float(seconds):
        if int(time.time() - int(start)) > last:
            print int(seconds) - last
            last = last + 10
        x = port.readline()
        x.strip()
        if (x != ""):
            try:
                ydata.append(float(x))
                del ydata[0]
                abc.write(x)
            except:
                pass

    abc.close()
    port.close()
    
    print("finished reading")
    

t1 = FuncThread(read, sys.argv[1])
t2 = FuncThread(plot, )
t1.start()
time.sleep(3)
t2.start()
t1.join()

f = open('data.txt', 'r')
lastValue = 0.0
# reference voltage
refVol = 0.45
# accuracy is 10bit, 0 to 1023
maxVal = 1023
# compute the scale multiplikator for the data (in words this is what a 1 on the serial port would stand for)
multiplikator = (refVol / maxVal) / 10
# at the start the area is 0
area = 0
# for now aequidistant steps of one second
# TODO: put a timestamp on the data

count = 0
for line in f:
    try:
        # scale the data
        line = multiplikator * float(line)
        # compute the area
        area = area + (((lastValue + line) / 2))
        lastValue = line
        count = count + 1
    except:
        pass

if count > 0:
    secondsPerValue = float(sys.argv[1]) / count
    area = area * secondsPerValue
    print area
    
else:
    print("no values")
