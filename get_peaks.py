import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.mathtext
import sys, glob
import datetime
import pdb

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
def plot_data_peaks(data,threshold_2,indices,peak_max_value):
	fig = plt.figure(figsize=(15,8),dpi=85,facecolor='w',edgecolor='k')
	plt.plot(data,'-')
	plt.axis('tight')
	plt.ylim(( 0, np.int(np.ceil(np.max(data))/10+2)*10 ))
	
	for (i,j),pmv in zip(indices, peak_max_value):
		if pmv > threshold_2:
			plt.axvspan(i, j, facecolor='r', alpha=0.15)
		#~ else:
			#~ plt.axvspan(i, j, facecolor='g', alpha=0.15)
	
	plt.subplots_adjust(left=0.05,right=0.97,bottom=0.05,top=0.97,wspace=0.1,hspace=0.1)
	plt.show()

########################################################################
def plot_data_subset(data, tdm, ymn=0, ymx=115):
	fig, ax = plt.subplots(figsize=(4,5),dpi=85,facecolor='w',edgecolor='k')
	ax.plot(data,'-')
	
	#~ ticks = ax.get_xticks()
	#~ labels = [item.get_text() for item in ax.get_xticklabels()]
	new_labels = np.arange(0,int(np.round(tdm*len(data),0)), 5)
	new_label_pos = np.arange(0,int(np.round(tdm*len(data),0)), 5)/tdm
	ax.xaxis.set_ticks(new_label_pos)
	ax.xaxis.set_ticklabels(new_labels)
	ax.set_xlabel('milliseconds')
	ax.set_ylabel(r'$mA$', fontsize='16')
	ax.yaxis.labelpad = 0.7
	plt.axis('tight'); plt.ylim(( ymn, ymx )); plt.grid(axis='y');
	plt.subplots_adjust(left=0.15,right=0.96,bottom=0.11,top=0.97,wspace=0.1,hspace=0.1)
	plt.show()


########################################################################
def plot_data_subset_boxplot(data, peaks, tdm, thr_3, ymn=0, ymx=115):
	fig = plt.figure(figsize=(5,5),dpi=85,facecolor='w',edgecolor='k')
	gs = gridspec.GridSpec(1, 2, width_ratios=[5,1] )
	
	ax1 = plt.subplot(gs[0])
	ax1.plot(data,'-')
	#~ plt.grid(axis='y')
	new_labels = np.arange(0,int(np.round(tdm*len(data),0)), 5)
	new_label_pos = np.arange(0,int(np.round(tdm*len(data),0)), 5)/tdm
	ax1.xaxis.set_ticks(new_label_pos)
	ax1.xaxis.set_ticklabels(new_labels)
	ax1.set_xlabel('milliseconds')
	ax1.set_ylabel(r'$mA$', fontsize='16')
	ax1.yaxis.labelpad = 0.7
	ax1.axis('tight')
	ax1.set_ylim(( ymn, ymx ))
	
	ax2 = plt.subplot(gs[1])
	ax2.boxplot( peaks[peaks/1000 > thr_3]/1000, widths=0.5)
	#~ plt.grid(axis='y')
	ax2.tick_params(axis='both', which='major')#, labelsize=9)
	#~ ax2.set_xlabel('1GB TS')		# '1GB TS','2GB SD','2GB TS'
	ax2.set_xticklabels([])
	ax2.set_ylabel(r'$mA \cdot s$', fontsize='16')
	ax2.yaxis.labelpad = 0.7
	
	plt.subplots_adjust(left=0.12,right=0.96,bottom=0.11,top=0.97,wspace=0.4,hspace=0.3)
	plt.show()

########################################################################
def plot_boxplot(data, ypad = 0.7):
	fig = plt.figure(figsize=(4,5),dpi=85,facecolor='w',edgecolor='k')
	plt.boxplot(data, widths=0.7)
	plt.grid(axis='y')
	ax = plt.gca()
	ax.tick_params(axis='both', which='major')#, labelsize=9)
	ax.set_xticklabels(['1GB TS','2GB SD','2GB TS'])#, fontsize='9')#, rotation=45)
	ax.set_xlabel(' ')
	ax.set_ylabel(r'$mA \cdot s$', fontsize='16')
	ax.yaxis.labelpad = ypad
	#~ plt.subplots_adjust(left=0.12,right=0.97,bottom=0.06,top=0.96,wspace=0.5,hspace=0.1)
	#~ plt.subplots_adjust(left=0.14,right=0.97,bottom=0.06,top=0.96,wspace=0.5,hspace=0.1)
	plt.subplots_adjust(left=0.15,right=0.96,bottom=0.11,top=0.97,wspace=0.1,hspace=0.1)

########################################################################
def plot_sdcard_peaks_boxplots(filenamelist):
	
	pa = []
	#~ pdb.set_trace()
	for filename,thr_3 in filenamelist:
		pth = 'measurements/paper/' + filename + '/voltage.npy'
		thr_1 = 0.8; thr_2 = 20.0
		pa_tmp = plot_data_and_extract_peaks(pth, thr_1, thr_2, False)
		pa_tmp = pa_tmp / 1000.0		# convert from mA*ms to mA*s !
		pa.append( pa_tmp[pa_tmp > thr_3])
	plot_boxplot(pa)


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
########################################################################
def plot_data_and_extract_peaks(filename,threshold_1,threshold_2, pltstf=False):
	# load data; extract timestamps, raw sensor values
	rawData = np.load( filename )
	tme  = rawData[:,0]
	dta  = np.concatenate(np.array(rawData)[:,1].flatten())

	tmedelta = np.array([t.total_seconds() for t in np.diff(tme)])*1000
	tmedeltamean = np.mean(tmedelta)/len(rawData[0][1])

	# get callibration range
	resistor = 10.0		# 10 Ohm resistor
	clbr_min = np.mean(np.concatenate(np.array(np.load('cal-0.0V.npy'))[:,1].flatten()))
	clbr_max = np.mean(np.concatenate(np.array(np.load('cal-1.0V.npy'))[:,1].flatten()))

	# smooth data
	data = smooth(dta, 5)
	data_scaled_mA = 1000.0/resistor*(data - clbr_min)/(clbr_max - clbr_min)

	# extract peaks peaks
	indices = get_peaks(data_scaled_mA,threshold_1,10)

	# extract peak max and mean values
	peak_max_value  = np.array([max(data_scaled_mA[i:j]) for i,j in indices], 'int')
	peak_mean_value = np.array([np.mean(data_scaled_mA[i:j]) for i,j in indices], 'int')

	# compute area-under-curve for each peak
	peak_area = np.array([np.trapz(data_scaled_mA[i:j]) for i,j in indices])

	# plot data, highlight peaks
	if pltstf:
		plot_data_peaks(data_scaled_mA,6,indices,peak_area/1000)
		
	
	#~ plot_data_subset(data_scaled_mA[960000:961200],tmedeltamean)	# test 3
	#~ plot_data_subset(data_scaled_mA[598900:600100],tmedeltamean)	# test 5
	#~ plot_data_subset(data_scaled_mA[363300:364500],tmedeltamean)	# test 6
	
	#~ plot_data_subset_boxplot(data_scaled_mA[960000:961200],peak_area,tmedeltamean,7.5)	# test 3
	#~ plot_data_subset_boxplot(data_scaled_mA[598900:600100],peak_area,tmedeltamean,7.5)	# test 5
	#~ plot_data_subset_boxplot(data_scaled_mA[363300:364500],peak_area,tmedeltamean,11)	# test 6
	
	return peak_area
########################################################################
########################################################################




########################################################################
### MAIN SCRIPT

#~ filename  = sys.argv[1]
#~ threshold_1 = float(sys.argv[2])
#~ threshold_2 = float(sys.argv[3])
#~ plot_data_and_extract_peaks(filename,0.8, 6, False)

plot_sdcard_peaks_boxplots([('test3',7.5),('test5',7.5),('test6',12)])
