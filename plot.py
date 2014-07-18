########################################################################
#
# Script to plot voltage meassurement data from Hedgehog
# 
########################################################################
import numpy as np
import matplotlib.pyplot as plt
import sys
import os.path
from scipy import misc


########################################################################
#
# arguments
#		filename of the data file
#		threshold for small peaks
#		threshold for big peaks
#
########################################################################
filename = sys.argv[1]
threshold = int(sys.argv[2])
tresholdBig = int(sys.argv[3])

# minimum distance betwenn two peaks, else they will be merged
dist = 20
# minimum peak length, peaks smaller than that will not be marked as peaks
minpeakLength = 19
# resistor characteristics
resistor = 10.0	
# calibration filenames
fileMin = os.path.abspath(os.path.join(os.path.join(filename, os.pardir), os.pardir)) + '/cal-0.0V.npy'
fileMax = os.path.abspath(os.path.join(os.path.join(filename, os.pardir), os.pardir)) + '/cal-1.0V.npy'


########################################################################
#
# filter function to smooth the data
#
# arguments
# 	data to filter
#
########################################################################
def smooth(data, window_len=11, window='hanning'):
	if data.ndim != 1:
		raise ValueError, "smooth only accepts 1 dimension arrays."
	if data.size < window_len:
		raise ValueError, "Input vector needs to be bigger than window size."
	if window_len<3:
		return data
	if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
		raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

	s = np.r_[data[window_len-1:0:-1],data,data[-1:-window_len:-1]]

	if window == 'flat':
		w = np.ones(window_len,'d')
	else:
		w = eval('np.'+window+'(window_len)')

	y = np.convolve(w/w.sum(),s,mode='valid')
	return y


########################################################################
#
# load and preprocess the data
#
# arguments
# 	filename of the data file
#
########################################################################
def load(filename):
	rawData = np.load(filename)
	data = np.concatenate(np.array(rawData)[:,1].flatten())
	return data


########################################################################
#
# callibrate the data
#
# arguments
# 	data to callibrate
#	resistance in ohm
# 	calibration filename meassured with 0.0V
# 	calibration filename meassured with voltage equal 
#		to arduino reference voltage
#
########################################################################
def callibrate(data, resistor, fileMin, fileMax):
	# scale the data according to callibration
	clbr_min = np.mean(np.concatenate(np.array(np.load(fileMin))[:,1].flatten()))
	clbr_max = np.mean(np.concatenate(np.array(np.load(fileMax))[:,1].flatten()))
	print clbr_min
	print clbr_max
	data = 1000.0/resistor*(data - clbr_min)/(clbr_max - clbr_min)
	return data


########################################################################
#
# extract the peaks
#
# arguments
# 	data to extract peaks
#	threshold for peak detection
# 	minimum length of a peak
# 	minimum distance between two peaks
#
# returns
# 	
########################################################################
def get_peaks(data,threshold,gap_threshold):
	# apply threshold, result is a boolean array
	abovethr = np.where( data >= threshold )[0]
	belowthr = np.where( data <  threshold )[0]

	#### extract peaks
	# first, find gaps in "above"/"below" labels (differences bigger than 1)
	b1 = np.where( np.diff(abovethr)>1 )[0]
	b2 = np.where( np.diff(belowthr)>1 )[0]

	# second, concatenate peak start and stop indices
	# note the +1 which fixes the diff-offset
	if belowthr[b2][0] > abovethr[b1][0]:
		b1 = b1[1:]
	indices = np.column_stack(( belowthr[b2], 
						np.concatenate((abovethr[b1],[abovethr[-1]])) )) + 1

	# third, merge peaks if they are very close to eachother
	indices_gaps = indices.flatten()[1:-1].reshape((-1,2))
	gaps_to_preserve = np.where(np.diff(indices_gaps).flatten() > gap_threshold )[0]

	indices_filtered = np.concatenate(( [indices[0,0]], 
											indices_gaps[gaps_to_preserve].flatten(), 
											[indices[-1,1]] )).reshape((-1,2))
										
	return indices_filtered

########################################################################
#
# MAIN
#
########################################################################
data = load(filename)
data = callibrate(data, resistor, fileMin, fileMax)
data = smooth(data, 5)
indices = get_peaks(data, threshold, dist)

# categorize peaks
smallpeaks = []
bigpeaks = []

for i in indices:
	if max(data[i[0]:i[1]]) > tresholdBig:
		bigpeaks.append(i)
	else:
		smallpeaks.append(i)

# plot function
def plot(smallpeaks, bigpeaks):
	# plot adjustments
	plt.figure(figsize=(10,6),dpi=85,facecolor='w',edgecolor='k')
	plt.plot(data,'-',label='no. 127')

	# mark peaks in plot
	for i in bigpeaks:
		plt.axvspan(i[0], i[1], facecolor='r', alpha=0.2)
	for i in smallpeaks:
		plt.axvspan(i[0], i[1], facecolor='g', alpha=0.2)

	# show plot
	plt.show()

# compute the area under the peaks
bigArea = 0
for peak in bigpeaks:
	bigArea += np.trapz(data[peak[0]:peak[1]])
smallArea = 0
for peak in smallpeaks:
	smallArea += np.trapz(data[peak[0]:peak[1]])
area = np.trapz(data)

# print statistics of the data
print "number of big peaks:\t", len(bigpeaks)
print "number of small peaks:\t", len(smallpeaks)
print "area under curve:\t", area
print "area under big peaks:\t", bigArea, "\t( ", round(bigArea / (area / 100), 1) ,"% )"
print "area under small peaks:\t", smallArea, "\t( ",  round(smallArea / (area / 100), 1) ,"% )"
print "area without peaks:\t", (area - (bigArea + smallArea)), "\t( ", round((area - (bigArea + smallArea)) / (area / 100), 1) ,"% )"

# plot data
plot(smallpeaks, bigpeaks)
