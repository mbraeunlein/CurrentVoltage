import numpy as np
import matplotlib.pyplot as plt
import sys

filename = sys.argv[1]
threshold = int(sys.argv[2])
running = False
start = 0
indices = []
dist = 100
count = 0

rawData = np.load(filename)
data = np.concatenate(np.array(rawData)[:,1].flatten())

for idx, val in enumerate(data):
	if val > threshold:
		if not running:
			running = True
			start = idx
	if val < threshold:
		if running:
			if dist > count:
				count = count + 1
			else:
				count = 0
				running = False
				indices.append((start, idx - dist))

for i in indices:
	if max(data[i[0]:i[1]]) > 700:
		plt.axvspan(i[0], i[1], facecolor='r', alpha=0.2)
	else:
		plt.axvspan(i[0], i[1], facecolor='g', alpha=0.2)

plt.plot(data,'-',label='no. 127')
plt.show()
