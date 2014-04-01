import numpy as np
import matplotlib.pyplot as plt
import sys

filename  = sys.argv[1]
threshold = int(sys.argv[2])

rawData = np.load( filename )
data = np.concatenate(np.array(rawData)[:,1].flatten())

abovethr = np.where( data >= threshold )[0]
belowthr = np.where( data <  threshold )[0]

b1 = np.where( np.diff(abovethr)>1 )[0]
b2 = np.where( np.diff(belowthr)>1 )[0]

indices = np.column_stack(( belowthr[b2[:-1]], abovethr[b1] ))

plt.plot(data,'-',label='no. 127')
for i,j in indices:
	plt.axvspan(i, j, facecolor='r', alpha=0.15)

plt.show()
