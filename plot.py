import numpy as np
import matplotlib.pyplot as plt

foo1 = np.load('data-127.npy')
foo2 = np.load('data-132.npy')


bla1 = np.concatenate(np.array(foo1)[:,1].flatten())
bla2 = np.concatenate(np.array(foo2)[:,1].flatten())

plt.plot(bla1,'-',label='no. 127')
plt.plot(bla2,'-',label='no. 132')
#~ plt.legend()

plt.show()
