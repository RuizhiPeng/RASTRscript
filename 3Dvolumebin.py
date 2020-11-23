#! /usr/bin/env python
import numpy as np
from pyami import mrc
import sys

inv=sys.argv[1]
outv=sys.argv[2]

volume=mrc.read(inv)
boxsize=volume.shape[0]
if boxsize%2 !=0:
	print 'boxsize odd'
	sys.exit()
newboxsize=boxsize/2
newvolume=np.zeros((newboxsize,newboxsize,newboxsize))

for z in range(newboxsize):
	for y in range(newboxsize):
		for x in range(newboxsize):
			newvolume[z][y][x]+=volume[2*z][2*y][2*x]
			newvolume[z][y][x]+=volume[2*z][2*y][2*x+1]
			newvolume[z][y][x]+=volume[2*z][2*y+1][2*x]
			newvolume[z][y][x]+=volume[2*z][2*y+1][2*x+1]
			newvolume[z][y][x]+=volume[2*z+1][2*y][2*x]
			newvolume[z][y][x]+=volume[2*z+1][2*y][2*x+1]
			newvolume[z][y][x]+=volume[2*z+1][2*y+1][2*x]
			newvolume[z][y][x]+=volume[2*z+1][2*y+1][2*x+1]
			newvolume[z][y][x]=newvolume[z][y][x]/8

mrc.write(newvolume,outv)
