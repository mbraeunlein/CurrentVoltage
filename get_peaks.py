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
### plot all data and highlight peaks
def plot_data_peaks(data,threshold_2,threshold_3,indices,peak_max_value):
	fig = plt.figure(figsize=(15,8),dpi=85,facecolor='w',edgecolor='k')
	plt.plot(data,'-')
	plt.axis('tight')
	plt.ylim(( 0, np.int(np.ceil(np.max(data))/10+2)*10 ))
	
	for (i,j),pmv in zip(indices, peak_max_value):
		if (pmv > threshold_2) & (pmv < threshold_3) :
			plt.axvspan(i, j, facecolor='r', alpha=0.15)
		elif (pmv > threshold_3):
			plt.axvspan(i, j, facecolor='g', alpha=0.15)
	
	plt.subplots_adjust(left=0.05,right=0.97,bottom=0.05,top=0.97,wspace=0.1,hspace=0.1)
	plt.show()

########################################################################
### plotting pic communication and SD writes
def plot_data_subset_range(data, tdm, step=5, ymn=0, ymx=115):
	fig, ax = plt.subplots(figsize=(6,4),dpi=85,facecolor='w',edgecolor='k')
	ax.plot(data,'-')
	
	new_labels = np.arange(0,int(np.round(tdm*len(data),0)), step)
	new_label_pos = np.arange(0,int(np.round(tdm*len(data),0)), step)/tdm
	ax.xaxis.set_ticks(new_label_pos)
	ax.xaxis.set_ticklabels(new_labels)
	ax.set_xlabel('milliseconds')
	ax.set_ylabel(r'$mA$', fontsize='16')
	ax.yaxis.labelpad = 0.7
	plt.axis('tight'); plt.ylim(( ymn, ymx )); plt.grid(axis='y');
	plt.subplots_adjust(left=0.09,right=0.98,bottom=0.13,top=0.96,wspace=0.1,hspace=0.1)
	plt.show()

########################################################################
### plotting SD-card-peaks
def plot_data_subset(data, tdm, step=5, ymn=0, ymx=115):
	fig, ax = plt.subplots(figsize=(4,5),dpi=85,facecolor='w',edgecolor='k')
	ax.plot(data,'-')
	
	new_labels = np.arange(0,int(np.round(tdm*len(data),0)), step)
	new_label_pos = np.arange(0,int(np.round(tdm*len(data),0)), step)/tdm
	ax.xaxis.set_ticks(new_label_pos)
	ax.xaxis.set_ticklabels(new_labels)
	ax.set_xlabel('milliseconds')
	ax.set_ylabel(r'$mA$', fontsize='16')
	ax.yaxis.labelpad = 0.7
	plt.axis('tight'); plt.ylim(( ymn, ymx )); plt.grid(axis='y');
	plt.subplots_adjust(left=0.15,right=0.96,bottom=0.11,top=0.97,wspace=0.1,hspace=0.1)
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
	plt.subplots_adjust(left=0.15,right=0.96,bottom=0.11,top=0.97,wspace=0.1,hspace=0.1)

########################################################################
def plot_sdcard_peaks_boxplots(filenamelist):
	
	pa = []
	#~ pdb.set_trace()
	for filename,thr_3 in filenamelist:
		pth = 'measurements/paper2/' + filename + '/voltage.npy'
		thr_1 = 0.8; thr_2 = 20.0
		pa_tmp = plot_data_and_extract_peaks(pth, thr_1, thr_2, False)
		pa.append( pa_tmp[pa_tmp > thr_3])
	plot_boxplot(pa)
	return pa

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
def plot_data_and_extract_peaks(filename,threshold_1,threshold_2, threshold_3, pltstf=False):
	# load data; extract timestamps, raw sensor values
	rawData = np.load( filename )
	tme  = rawData[:,0]
	dta  = np.concatenate(np.array(rawData)[:,1].flatten())
	
	refvolt = 1.0
	
	if int(filename[-13:-12]) in [3,4]:
		tme  = tme[:-1]
		dta  = dta[:-2000]
	elif int(filename[-13:-12]) == 7:
		refvolt = 2.1		# magic number
	
	tmedelta = np.array([t.total_seconds() for t in np.diff(tme)])*1000
	tmedeltamean = np.mean(tmedelta)/3300	# factor found by callibrating over oscilloscope

	# get callibration range
	resistor = 10.0		# 10 Ohm resistor
	if int(filename[-13:-12]) == 7:
		clbr_min = np.mean(np.concatenate(np.array(np.load('cal-0.0V-for-oled.npy'))[:,1].flatten()))
		clbr_max = np.mean(np.concatenate(np.array(np.load('cal-2.0V-for-oled.npy'))[:,1].flatten()))
	else:
		clbr_min = np.mean(np.concatenate(np.array(np.load('cal-0.0V-new.npy'))[:,1].flatten()))
		clbr_max = np.mean(np.concatenate(np.array(np.load('cal-1.0V-new.npy'))[:,1].flatten()))
	
	# smooth data
	data = smooth(dta, 5)
	if int(filename[-13:-12]) == 7:
		data_scaled_mA = refvolt * 1000.0/resistor*(data)/(clbr_max)
	else:
		data_scaled_mA = refvolt * 1000.0/resistor*(data - clbr_min)/(clbr_max - clbr_min)

	# extract peaks peaks
	indices = get_peaks(data_scaled_mA,threshold_1,10)

	# extract peak max and mean values
	peak_max_value  = np.array([max(data_scaled_mA[i:j])     for i,j in indices], 'int')
	#~ peak_mean_value = np.array([np.mean(data_scaled_mA[i:j]) for i,j in indices], 'int')

	# compute area-under-curve for each peak
	peak_area = np.array([np.trapz(data_scaled_mA[i:j]) for i,j in indices])
	
	# scale area-under-curve to milliseconds
	peak_area_mAs = peak_area * tmedeltamean / 1000 

	# plot data, highlight peaks
	if pltstf:
		plot_data_peaks(data_scaled_mA,threshold_2,threshold_3,indices,peak_max_value)
	
	
	bigPeaksN  = len( peak_area_mAs[peak_max_value >= threshold_3] )
	smallPeaksN= len( peak_area_mAs[peak_max_value <  threshold_3] )
	totalArea  = np.trapz(data_scaled_mA * tmedeltamean / 1000 )
	bigArea    = sum(peak_area_mAs[peak_max_value >= threshold_3])
	smallArea  = sum(peak_area_mAs[peak_max_value <  threshold_3])
	
	if int(filename[-13:-12]) == 7:
		OLEDPeakN  = len( peak_area_mAs[(peak_max_value >= threshold_3)] )
		OLEDArea   = sum( peak_area_mAs[(peak_max_value >= threshold_3)] )

		bigPeaksN  = len( peak_area_mAs[(peak_max_value >= threshold_2) & (peak_max_value < threshold_3)] )
		bigArea    = sum( peak_area_mAs[(peak_max_value >= threshold_2) & (peak_max_value < threshold_3)] )

		smallPeaksN= len( peak_area_mAs[(peak_max_value >  threshold_1) & (peak_max_value < threshold_2)] )
		smallArea  = sum( peak_area_mAs[(peak_max_value >  threshold_1) & (peak_max_value < threshold_2)] )

		totalArea  = np.trapz(data_scaled_mA * tmedeltamean / 1000 )

		print "number of OLED peaks   :\t", OLEDPeakN
		print "area under OLED peaks  :\t", round(OLEDArea,2),   "\t( ", round(OLEDArea   / (totalArea / 100.0), 1) ,"% )"

	# print statistics of the data
	print "number of big peaks   :\t", bigPeaksN
	print "number of small peaks :\t", smallPeaksN
	print "area under curve      :\t", round(totalArea,2)
	print "area under big peaks  :\t", round(bigArea,2),   "\t( ", round(bigArea   / (totalArea / 100.0), 1) ,"% )"
	print "area under small peaks:\t", round(smallArea,2), "\t( ", round(smallArea / (totalArea / 100.0), 1) ,"% )"
	print "area without peaks    :\t", round((totalArea - (bigArea + smallArea)),2), \
								 "\t( ", round((totalArea - (bigArea + smallArea)) / (totalArea / 100), 1) ,"% )"

	
	print 'total consumption & SD writes & sampling'
	print round(totalArea,2) , round(bigArea,2), round(100*bigArea/totalArea,1),"%", round(smallArea,2), round(100*smallArea/totalArea,1),"%"
	
	### plotting introduction figure ( PIC sampling and SD write)
	#~ plot_data_subset_range(data_scaled_mA[734600:737850],tmedeltamean,step=10,ymn=0,ymx=37)		# test 1
	#~ plot_data_subset_range(data_scaled_mA[734600:736600],tmedeltamean,step=10,ymn=0,ymx=7)		# test 1
	#~ plot_data_subset_range(data_scaled_mA[766600:768100],tmedeltamean,step=10,ymn=0,ymx=5.5)			# paper2/test1
	#~ plot_data_subset_range(np.concatenate([data_scaled_mA[1106500:1107500],data_scaled_mA[1114500:1117000]]),tmedeltamean,step=10,ymn=0,ymx=37)		# test 2
	#~ plot_data_subset_range(data_scaled_mA[1106000:1108000],tmedeltamean,step=10,ymn=0,ymx=7)		# test 2
	#~ plot_data_subset_range(data_scaled_mA[571500:573000],tmedeltamean,step=10,ymn=0,ymx=5.5)		# paper2/test2
	#~ plot_data_subset_range(data_scaled_mA[911000:915000],tmedeltamean,step=10,ymn=0,ymx=150)		# paper2/test7
	
	### plotting SD write peaks for differend SD cards:
	#~ plot_data_subset(data_scaled_mA[960000:961200],tmedeltamean)	# test 3
	#~ plot_data_subset(data_scaled_mA[598900:600100],tmedeltamean)	# test 5
	#~ plot_data_subset(data_scaled_mA[363300:364500],tmedeltamean)	# test 6
	
		
	#~ return peak_area_mAs
########################################################################
########################################################################




########################################################################
### MAIN SCRIPT

filename  = sys.argv[1]
threshold_1 = float(sys.argv[2])
threshold_2 = float(sys.argv[3])
threshold_3 = float(sys.argv[4])
plot_data_and_extract_peaks(filename,threshold_1, threshold_2, threshold_3, True)

#~ acc  = np.load(filename[:-11] + 'log' + filename[-4:]).view(np.recarray)
#~ fig = plt.figure(figsize=(15,8),dpi=85,facecolor='w',edgecolor='k')
#~ plt.plot_date(acc.t, np.array((acc.x,acc.y,acc.z)).T, '-')
#~ plt.subplots_adjust(left=0.05,right=0.97,bottom=0.05,top=0.97,wspace=0.1,hspace=0.1)
#~ plt.ylim((0,255))

#~ peak_area_mAs = plot_sdcard_peaks_boxplots([('test3',0.16),('test5',0.16),('test6',0.25)])
