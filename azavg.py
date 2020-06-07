#!/usr/bin/env python

import numpy
from pyami import mrc
from pyami import imagefun
import sys


def radial_profile(data, center):
	y, x = numpy.indices((data.shape))
	r = numpy.sqrt((x - center[0])**2 + (y - center[1])**2)
	r = r.astype(numpy.int)
	print r.shape
	tbin = numpy.bincount(r.ravel(), data.ravel())
	print tbin.shape
	sys.exit()
	nr = numpy.bincount(r.ravel())
	print nr
	radialprofile = tbin / nr
	print radialprofile
	print radialprofile.shape
	return radialprofile 

def radialAverage(data,center):
	radavg=numpy.zeros(center)
	nvals=numpy.zeros(center)
	for x in range(0,data.shape[0]):
		print x
		for y in range(0,data.shape[1]):
			dx=x-center
			dy=y-center
			d=math.sqrt(dx*dx+dy*dy)
			d=round(d)
			d=int(d)
			radavg[d]=radavg[d]+val
			nvals[d]=nvals[d]+1
	radavg=radavg/nvals
 

invol=sys.argv[1]
outvol=sys.argv[2]

vol=mrc.read(invol)
zavg=numpy.average(vol,axis=0)
#rotavg=imagefun.radialAverageImage(zavg)
cylavg=numpy.zeros(vol.shape)
for n in range(vol.shape[0]):
	cylavg[n]=zavg
mrc.write(cylavg,outvol)
