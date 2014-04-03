import numpy as np
import matplotlib.pyplot as plt
import glob

lst = sorted(glob.glob('cal-*.npy'))

x=[]
hndl = []
for l in lst:
    rawData = np.load(l)
    data = np.concatenate(np.array(rawData)[:,1].flatten())
    x.append(np.mean(data))

plt.plot(x,'-',label="mean")
plt.show()
