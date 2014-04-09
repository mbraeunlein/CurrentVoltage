import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy import misc

# filter function for the data
def smooth(x,window_len=11,window='hanning'):
	if x.ndim != 1:
		raise ValueError, "smooth only accepts 1 dimension arrays."
	if x.size < window_len:
		raise ValueError, "Input vector needs to be bigger than window size."
	if window_len<3:
		return x
	if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
		raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

	s = np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]

	if window == 'flat':
		w = np.ones(window_len,'d')
	else:
		w = eval('np.'+window+'(window_len)')

	y = np.convolve(w/w.sum(),s,mode='valid')
	return y


# parameters are the filename to plot, the threshold for peek detection
# and the treshold to differenciate between small and big peeks
filename = sys.argv[1]
threshold = int(sys.argv[2])
tresholdBig = int(sys.argv[3])

# minimum distance betwenn two peeks, else they will be merged
dist = 20
# minimum peek length, peeks smaller than that will not be marked as peeks
minPeekLength = 19

# load and preprocess the data
rawData = np.load(filename)
data = np.concatenate(np.array(rawData)[:,1].flatten())

# 10 Ohm resistor
resistor = 10.0	
# scale the data according to callibration
clbr_min = np.mean(np.concatenate(np.array(np.load('cal-0.0V.npy'))[:,1].flatten()))
clbr_max = np.mean(np.concatenate(np.array(np.load('cal-1.0V.npy'))[:,1].flatten()))
data = 1000.0/resistor*(data - clbr_min)/(clbr_max - clbr_min)

# filter the data
data = smooth(data, 5)

# variables needed for peek detection
start = 0
indices = []
count = 0
running = False


# detect peeks
for idx, val in enumerate(data):
	if val > threshold:
		if not running:
			running = True
			start = idx
		else:
			count = 0
	if val < threshold:
		if running:
			if dist > count:
				count = count + 1
			else:
				running = False
				if ((idx - count) - start) > minPeekLength:
					indices.append((start, idx - count))
				count = 0

# categorize peeks
smallPeeks = []
bigPeeks = []

for i in indices:
	if max(data[i[0]:i[1]]) > tresholdBig:
		bigPeeks.append(i)
	else:
		smallPeeks.append(i)

# plot function
def plot(smallPeeks, bigPeeks):
	# plot adjustments
	plt.figure(figsize=(10,6),dpi=85,facecolor='w',edgecolor='k')
	plt.plot(data,'-',label='no. 127')

	# mark peeks in plot
	for i in bigPeeks:
		plt.axvspan(i[0], i[1], facecolor='r', alpha=0.2)
	for i in smallPeeks:
		plt.axvspan(i[0], i[1], facecolor='g', alpha=0.2)

	# show plot
	plt.show()

# compute the area under the peeks
bigArea = 0
for peek in bigPeeks:
	bigArea += np.trapz(data[peek[0]:peek[1]])
smallArea = 0
for peek in smallPeeks:
	smallArea += np.trapz(data[peek[0]:peek[1]])
area = np.trapz(data)

# print statistics of the data
print "number of big peeks:\t", len(bigPeeks)
print "number of small peeks:\t", len(smallPeeks)
print "area under curve:\t", area
print "area under big peeks:\t", bigArea, "\t( ", round(bigArea / (area / 100), 1) ,"% )"
print "area under small peeks:\t", smallArea, "\t( ",  round(smallArea / (area / 100), 1) ,"% )"
print "area without peeks:\t", (area - (bigArea + smallArea)), "\t( ", round((area - (bigArea + smallArea)) / (area / 100), 1) ,"% )"

# plot data
plot(smallPeeks, bigPeeks)
