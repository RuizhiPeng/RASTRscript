#!/usr/bin/env python

### usage: ./azavg.py inputfile

import numpy
from pyami import mrc
from pyami import imagefun
import sys
import argparse
### mask means do averaging along z axis within the mask.
### keep means keep the voxels outside the mask
def parse(args):
	parser=argparse.ArgumentParser(description='full box average or within mask')
	parser.add_argument('-m','--mask',action='store',default=None,dest='mask')
	parser.add_argument('-k','--keep',action='store_true',default=False,dest='keep')
	return parser.parse_args(args)
 

invol=sys.argv[1]
outvol=invol[:-4]+'azavg.mrc'
parse=parse(sys.argv[2:])


vol=mrc.read(invol)
if parse.mask:
	maskvol=mrc.read(parse.mask)
	if maskvol.shape!=vol.shape:
		sys.exit('mask shape not consistent')
	elif maskvol.any()>1 or maskvol.any()<0:
		sys.exit('mask volume value beyond 0-1')
	else:
		nvol=vol*maskvol
		average=nvol.mean(axis=0)
		maskavg=maskvol.mean(axis=0)
		maskavg[maskavg==0]=1
		average=average/maskavg
		nvol[:]=average
		nvol=nvol*maskvol
		### if voxel outside mask need to be kept
		if parse.keep:
			opmask=mask
			opmask=1-opmask
			nvol=nvol+(vol*opmask)
		mrc.write(nvol,outvol)		
else:
	zavg=numpy.average(vol,axis=0)
	#rotavg=imagefun.radialAverageImage(zavg)
	cylavg=numpy.zeros(vol.shape)
	for n in range(vol.shape[0]):
		cylavg[n]=zavg
	mrc.write(cylavg,outvol)

