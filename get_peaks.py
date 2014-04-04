import numpy as np
import matplotlib.pyplot as plt
import sys

plt.ion()

########################################################################
def smooth(x,window_len=11,window='hanning'):
	if x.ndim != 1:
		raise ValueError, "smooth only accepts 1 dimension arrays."
	if x.size < window_len:
		raise ValueError, "Input vector needs to be bigger than window size."
	if window_len<3:
		return x
	if not window in ['flat','hanning','hamming','bartlett','blackman']:
		raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

	s = np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]

	if window == 'flat':
		w = np.ones(window_len,'d')
	else:
		w = eval('np.'+window+'(window_len)')

	y = np.convolve(w/w.sum(),s,mode='valid')
	return y

########################################################################
def plot_data_peaks(data,indices,peak_max_value):
	fig = plt.figure(figsize=(15,8),dpi=85,facecolor='w',edgecolor='k')
	plt.plot(data,'-',label='no. 127')
	
	for (i,j),pmv in zip(indices, peak_max_value):
		if pmv > 700:
			plt.axvspan(i, j, facecolor='r', alpha=0.15)
		else:
			plt.axvspan(i, j, facecolor='g', alpha=0.15)
	
	plt.axis('tight')
	#~ plt.ylim((180,np.ceil(max(data)/100)*100))
	#~ plt.axis(v=[0,len(data),0,np.ceil(max(data)/100)*100])
	plt.subplots_adjust(left=0.05,right=0.97,bottom=0.05,top=0.97,wspace=0.1,hspace=0.1)
	plt.show()

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
### MAIN SCRIPT
filename  = sys.argv[1]
threshold = int(sys.argv[2])

# load data; extract timestamps, raw sensor values
rawData = np.load( filename )
tme  = rawData[:,0]
dta  = np.concatenate(np.array(rawData)[:,1].flatten())

clbr_min = np.mean(np.concatenate(np.array(np.load('cal-0.0V.npy'))[:,1].flatten()))
clbr_max = np.mean(np.concatenate(np.array(np.load('cal-1.0V.npy'))[:,1].flatten()))

# smooth data
data = smooth(dta, 5)
data_scaled = 1000.0 /10.0 * (data-clbr_min)/(clbr_max-clbr_min)

indices = get_peaks(data,threshold,10)

# extract peak max and mean values
peak_max_value  = np.array([max(data[i:j]) for i,j in indices], 'int')
peak_mean_value = np.array([np.mean(data[i:j]) for i,j in indices], 'int')

# compute area-under-curve for each peak
peak_area = np.array([np.trapz(data[i:j]) for i,j in indices])
	

# plot data, highlight peaks
plot_data_peaks(data_scaled,indices,peak_max_value)
