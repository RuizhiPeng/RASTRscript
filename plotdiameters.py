#! /usr/bin/env python
### this scrip is to plot diameter distributions
import sys

fileobj=sys.argv[1]

a=open(fileobj,'r')
lines=a.readlines()
a.close()

diameters=[]
for line in lines:
	words=line.split()
	diameters.append(float(words[0]))
import numpy as np
diameters=np.array(diameters)

### delete too large and too small diameters
diameters=np.delete(diameters,np.where(diameters>400))
#diameters=np.delete(diameters,np.where(diameters<100))

freqs,edges=np.histogram(diameters,bins=50)

medians=[]
for i in range(len(edges)-1):
	medians.append((edges[i]+edges[i+1])/2)


from matplotlib import pyplot

### bins is changable
pyplot.hist(diameters,bins=200,normed=0)
pyplot.xlabel('diameter(A)')
pyplot.ylabel('number of particles')
#pyplot.plot(medians,freqs)
pyplot.show()

