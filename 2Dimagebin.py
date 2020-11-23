#! /usr/bin/env python




#### Ruizhi's personal script
#### used for 2D image shrink(bin)
#### usage: ./2Dimagebin.py inputfile binfactor
####    eg: ./2Dimagebin.py input.mrcs 2
#### bin factor has to be 2's powerful number 2 4 8 16

import numpy as np
from pyami import mrc
import sys
import copy
from multiprocessing import Pool
import time
import threading
### for image binning of mrc micrographs
time1=time.time()
inv=sys.argv[1]
binnumber=int(sys.argv[2])
repeat=int(np.log2(binnumber))
outputname=inv.split('.')[0]+'bin'+str(binnumber)+'.'+inv.split('.')[1]
try:
	threadnumber=int(sys.argv[3])
except:
	threadnumber=2

### 2D image bin by 2, input image stack matrix.
def slicebin2(vol):
	xodd=np.arange(vol.shape[0]/2)*2+1
	xeven=np.arange(vol.shape[0]/2)*2
	yodd=np.arange(vol.shape[1]/2)*2+1
	yeven=np.arange(vol.shape[1]/2)*2

        vol11=np.delete(vol,xeven,axis=0)
        vol11=np.delete(vol11,yeven,axis=1)
        #print vol11.shape
        vol12=np.delete(vol,xeven,axis=0)
        vol12=np.delete(vol12,yodd,axis=1)
        #print vol12.shape
        vol21=np.delete(vol,xodd,axis=0)
        vol21=np.delete(vol21,yeven,axis=1)
        #print vol21.shape
        vol22=np.delete(vol,xodd,axis=0)
        vol22=np.delete(vol22,yodd,axis=1)
        #print vol22.shape
        nvol=(vol11+vol12+vol21+vol22)/4
        return nvol
def slicebin(singleslice,repeat):
	for i in range(repeat):
		singleslice=slicebin2(singleslice)
	return singleslice
if __name__ == '__main__':
	fobj=open(inv,'rb')
	headerbytes=fobj.read(1024)
	headerdict=mrc.parseHeader(headerbytes)
	bytes_per_pixel=headerdict['dtype'].itemsize
	totalshape=headerdict['shape']
	boxsize=totalshape[1]
	headerend=1024+headerdict['nsymbt']
	if boxsize%binnumber!=0:
		print "binnumber not doable"
		sys.exit()
	### prod: x*y*z
	output=open(outputname,'wb')
	###deepcopy so that headerdict is not influenced
	newheaderdict=copy.deepcopy(headerdict)
	#newheaderdict['shape'][1]=headerdict['shape'][1]/2
	#newheaderdict['shape'][2]=headerdict['shape'][2]/2
	newheaderdict['ny']=headerdict['ny']/2
	newheaderdict['nx']=headerdict['nx']/2
	#print headerdict
	#print newheaderdict

	outputheader=mrc.makeHeaderData(newheaderdict)
	output.write(outputheader)
	for i in range(totalshape[0]):
		singleslice=mrc.readDataFromFile(fobj,headerdict,zslice=i)
		singleslice=slicebin(singleslice,repeat)
		#print singleslice.shape
		mrc.appendArray(singleslice,output)	


time2=time.time()
print time2-time1
