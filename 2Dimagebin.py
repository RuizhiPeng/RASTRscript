#! /usr/bin/env python

#### Ruizhi's personal script
#### used for 2D image shrink(bin)
#### usage: ./2Dimagebin.py inputfile binfactor processnumber
####    eg: ./2Dimagebin.py input.mrcs 2 4
#### bin by 2, using 4 process
#### bin factor has to be 2's powerful number 2 4 8 16

import numpy as np
from pyami import mrc
import sys
import copy
from multiprocessing import Pool, Process
import time
import threading
import os
time1=time.time()
inv=sys.argv[1]
binnumber=int(sys.argv[2])
repeat=int(np.log2(binnumber))
outputname=inv.split('.')[0]+'bin'+str(binnumber)+'.'+inv.split('.')[1]

### default process number 1
try:
	processnumber=int(sys.argv[3])
except:
	processnumber=1

### 2D image bin by 2, input image single slice 2D matrix.
def slicebin2(vol):
	xodd=np.arange(vol.shape[0]/2)*2+1
	xeven=np.arange(vol.shape[0]/2)*2
	yodd=np.arange(vol.shape[1]/2)*2+1
	yeven=np.arange(vol.shape[1]/2)*2
	### position 1 1 for all 2x2 bin box
        vol11=np.delete(vol,xeven,axis=0)
        vol11=np.delete(vol11,yeven,axis=1)
	### position 1 2 for all 2x2 binbox
        vol12=np.delete(vol,xeven,axis=0)
        vol12=np.delete(vol12,yodd,axis=1)
	### position 2 1 for all 2x2 binbox
        vol21=np.delete(vol,xodd,axis=0)
        vol21=np.delete(vol21,yeven,axis=1)
	### position 2 2 for all 2x2 binbox
        vol22=np.delete(vol,xodd,axis=0)
        vol22=np.delete(vol22,yodd,axis=1)
        nvol=(vol11+vol12+vol21+vol22)/4
        return nvol

### bin a list of slices in tempinput file object, write to tempfile output object
### repeat = log2(binfactor)
def slicesbin(imagelis,repeat,tempinput,tempfile):
	for i in imagelis:
		singleslice=mrc.readDataFromFile(tempinput,headerdict,zslice=i)
		for j in range(repeat):
			singleslice=slicebin2(singleslice)
		mrc.appendArray(singleslice,tempfile)
if __name__ == '__main__':
	### initialize headers
	inputobj=open(inv,'rb')
	headerbytes=inputobj.read(1024)
	inputobj.close()

	headerdict=mrc.parseHeader(headerbytes)
	totalshape=headerdict['shape']
	boxsize=totalshape[1]
	### check if image stacks can be binned
	if boxsize%binnumber!=0:
		print "binnumber not doable"
		sys.exit()
	### this is the final output file
	output=open(outputname,'wb')
	###deepcopy so that headerdict is not influenced
	newheaderdict=copy.deepcopy(headerdict)
	newheaderdict['ny']=headerdict['ny']/binnumber
	newheaderdict['nx']=headerdict['nx']/binnumber
	outputheader=mrc.makeHeaderData(newheaderdict)
	output.write(outputheader)

	start=0
	step=totalshape[0]/processnumber +1
	processes=[]
	inobjs={}

	### dividing whole dataset into processnumber parts
	for i in range(processnumber):
		end=start+step
		if end > totalshape[0]:
			end=totalshape[0]
		### mrc readDataFromFile use file.seek(), multiprocesses will affect each other
		### so open multiple input file to avoid
		inobjs[i]=open(inv,'rb')
		tempoutputobj=open('tempfile'+str(i),'wb')
		p=Process(target=slicesbin,args=(range(totalshape[0])[start:end],repeat,inobjs[i],tempoutputobj))
		p.start()
		processes.append(p)
		start+=step
	### wait until all processes finish
	for p in processes:
		p.join()
	### append temp output files 
	for i in range(processnumber):
		tempfile=open('tempfile'+str(i),'rb')
		output.write(tempfile.read())
		os.remove('tempfile'+str(i))
time2=time.time()
print "spend: ", time2-time1, " seconds"
print "output file as: ", outputname
