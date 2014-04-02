import numpy as np
import matplotlib.pyplot as plt
import sys

plt.ion()

filename = sys.argv[1]
threshold = int(sys.argv[2])

dist = 20
minPeekLength = 19

rawData = np.load(filename)
data = np.concatenate(np.array(rawData)[:,1].flatten())

start = 0
indices = []
count = 0
running = False

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

plt.figure(figsize=(10,6),dpi=85,facecolor='w',edgecolor='k')
plt.plot(data,'-',label='no. 127')

for i in indices:
	if max(data[i[0]:i[1]]) > 700:
		plt.axvspan(i[0], i[1], facecolor='r', alpha=0.2)
	else:
		plt.axvspan(i[0], i[1], facecolor='g', alpha=0.2)

plt.show()
