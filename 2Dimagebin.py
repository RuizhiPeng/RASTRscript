#! /usr/bin/env python
import numpy as np
from pyami import mrc
import sys
import copy
### for image binning of mrc micrographs
inv=sys.argv[1]
outv=sys.argv[2]

binnumber=2


### 2D image bin by 2, input image stack matrix.
def slicebin(vol):
        halfarray=np.arange(boxsize/2)

        odddelarray=halfarray*2+1
        evendelarray=halfarray*2

        vol11=np.delete(vol,evendelarray,axis=0)
        vol11=np.delete(vol11,evendelarray,axis=1)
        #print vol11.shape
        vol12=np.delete(vol,evendelarray,axis=0)
        vol12=np.delete(vol12,odddelarray,axis=1)
        #print vol12.shape
        vol21=np.delete(vol,odddelarray,axis=0)
        vol21=np.delete(vol21,evendelarray,axis=1)
        #print vol21.shape
        vol22=np.delete(vol,odddelarray,axis=0)
        vol22=np.delete(vol22,odddelarray,axis=1)
        #print vol22.shape
        nvol=(vol11+vol12+vol21+vol22)/4

        return nvol
#vol=mrc.read(inv)

## how to read partial mrc file instead of all  not finished. using pyami.mrc
'''tempvol=mrc.read(inv,zslice=i)
vol=np.append(vol,tempvol)
vol.reshape(z,y,x)

mrc.appendArray(a,f)
'''
### file input output module
fobj=open(inv,'rb')
headerbytes=fobj.read(1024)
headerdict=mrc.parseHeader(headerbytes)
#print headerdict
#sys.exit()
bytes_per_pixel=headerdict['dtype'].itemsize
totalshape=headerdict['shape']
boxsize=totalshape[1]
headerend=1024+headerdict['nsymbt']

### prod: x*y*z
output=open(outv,'wb')
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
###main loop slice by slice
for i in range(totalshape[0]):
	singleslice=mrc.readDataFromFile(fobj,headerdict,zslice=i)
	binslice=slicebin(singleslice)
	mrc.appendArray(binslice,output)	


