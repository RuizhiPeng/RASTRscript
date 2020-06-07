#! /usr/bin/env python
import numpy as np
from pyami import mrc
import sys
### for image binning of mrc micrographs
inv=sys.argv[1]
outv=sys.argv[2]

binnumber=2

#vol=mrc.read(inv)

## how to read partial mrc file instead of all  not finished. using pyami.mrc
'tempvol=mrc.read(inv,zslice=i)
vol=np.append(vol,tempvol)
vol.reshape(z,y,x)

mrc.appendArray(a,f)
'
### file input output module
fobj=open(inv,'rb')
headerbytes=fobj.read(1024)
#headerdict=parseHeader(headerbytes)
#bytes_per_pixel=headerdict['dtype'].itemsize
totalshape=headerdict['shape']
headerend=1024+headerdict['nsymbt']

### prod: x*y*z
start=headerend
datalen=np.prod((50,totalshape[1],totalshape[2]))
output=open(outv,'wb')
for i in range(totalshape[0]/50):
	fobj.seek(start)
	tmparray=np.fromfile(fobj,dtype='float32',count=datalen)
	output.seek(0,2)
	b=tmparray.ravel()
	b.tofile(output)
	start=start+datalen*bytes_per_pixel


### method 1
#secaxis=len(vol[0])/binnumber
#thirdaxis=len(vol[0][0])/binnumber
#outvol=np.zeors((len(vol),secaxis,thirdaxis))
#for i in range(len(vol)):
#	for j in range(secaxis):
#		for h in range(thirdaxis):
#			outvol[i][j][h]=vol[i][2*j-1][2*h-1]+vol[i][2*j-1][2*h-1]+vol[i][2*j][2*h-1]+vol[i][2*j][2*h]
#	print "finished %d" %i

#mrc.write(outvol,outv)
		

### method 2
print vol.shape

halfarray=np.arange(len(vol[0])/2)

odddelarray=halfarray*2+1
evendelarray=halfarray*2

vol11=np.delete(vol,evendelarray,axis=1)
vol11=np.delete(vol11,evendelarray,axis=2)
#print vol11.shape
vol12=np.delete(vol,evendelarray,axis=1)
vol12=np.delete(vol12,odddelarray,axis=2)
#print vol12.shape
vol21=np.delete(vol,odddelarray,axis=1)
vol21=np.delete(vol21,evendelarray,axis=2)
#print vol21.shape
vol22=np.delete(vol,odddelarray,axis=1)
vol22=np.delete(vol22,odddelarray,axis=2)
#print vol22.shape
nvol=vol11+vol12+vol21+vol22

#print nvol.shape
mrc.write(nvol,outv)
