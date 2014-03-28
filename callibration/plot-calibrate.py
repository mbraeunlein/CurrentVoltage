import numpy as np
import matplotlib.pyplot as plt
import glob

lst = sorted(glob.glob('cal-*.npy'))

x=[]
hndl = []
for l in lst:
    foo = np.load(l)
    hndl.append(plt.plot(foo,'-',label=l[4:-4]))
    x.append(np.mean(foo))
    

plt.show()
