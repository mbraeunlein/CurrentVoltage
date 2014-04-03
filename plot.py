import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy import misc

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



filename = sys.argv[1]
threshold = int(sys.argv[2])

dist = 20
minPeekLength = 19

rawData = np.load(filename)
data = np.concatenate(np.array(rawData)[:,1].flatten())
data = smooth(data, 5)
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
	if max(data[i[0]:i[1]]) > 700:
		bigPeeks.append(i)
	else:
		smallPeeks.append(i)

# plot data
plot(smallPeeks, bigPeeks)

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
