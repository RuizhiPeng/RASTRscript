#! /usr/bin/env python
import numpy
from pyami import mrc
import sys

invol=sys.argv[1]
outvol=sys.argv[2]


vol=mrc.read(invol)
otvol=numpy.zeros((100,512,512))
for n in range(100):
	otvol[n]=vol[n]
mrc.write(otvol,outvol)
