#! /usr/bin/env python
### Ruizhi's script for 3d volume binning
### usage: ./3Dvolumebin.py inputvolume outputname binfactor
### eg   : ./3Dvolumebin.py model.mrc modelbin4.mrc 4

import numpy as np
from pyami import mrc
import sys

inv=sys.argv[1]
outv=sys.argv[2]
scale=int(sys.argv[3])
repeat=int(np.log2(scale))
volume=mrc.read(inv)
def _3dbin(volume):
	boxsize=volume.shape[0]
	if boxsize%2 !=0:
		print 'boxsize odd'
		sys.exit()
	newboxsize=boxsize/2
	volume=volume.reshape(boxsize/2,2,boxsize/2,2,boxsize/2,2)
	newvolume=np.mean(volume,axis=5)
	newvolume=np.mean(newvolume,axis=3)
	newvolume=np.mean(newvolume,axis=1)
	return newvolume

for i in range(repeat):
	volume=_3dbin(volume)
mrc.write(volume,outv)
