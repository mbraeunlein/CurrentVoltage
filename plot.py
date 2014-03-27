import numpy as np
import matplotlib.pyplot as plt

foo = np.load('data.npy')
bla = np.concatenate(np.array(foo)[:,1].flatten())
plt.plot(bla,'-')
plt.show()
