import serial
import time
import sys

def read(seconds):
    print("reading data for " + seconds + " seconds")
    
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
        	abc.write(x)

    abc.close()
    port.close()
    
    
read(sys.argv[1])

print("finished reading")

f = open('data.txt', 'r')
lastValue = 0.0
# reference voltage
refVol = 1.1
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
    except :
        pass

if count > 0:
    secondsPerValue = float(sys.argv[1]) / count
    area = area * secondsPerValue
    print area
    
else:
    print("no values")
