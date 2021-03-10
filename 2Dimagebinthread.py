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
	y=vol.shape[0]
	x=vol.shape[1]
	nvol=vol.reshape(y/2,2,x/2,2)
	nvol=np.mean(nvol,axis=3)
	nvol=np.mean(nvol,axis=1)
        return nvol

### bin a list of slices in tempinput file object, write to tempfile output object
### repeat = log2(binfactor)
def slicesbin(imagelis,tempinput,tempfile):
	for i in imagelis:
		singleslice=mrc.readDataFromFile(tempinput,headerdict,zslice=i)
		for j in range(repeat):
			newslice=slicebin2(singleslice)
			singleslice=copy.deepcopy(newslice)
		mrc.appendArray(newslice,tempfile)	
	tempfile.close()
	print "finish"
if __name__ == '__main__':
	### initialize headers
	headerdict=mrc.readHeaderFromFile(inv)

	print headerdict
	totalshape=headerdict['shape']
	boxsize=totalshape[1]
	### check if image stacks can be binned
	if boxsize%binnumber!=0:
		print "binnumber not doable"
		sys.exit()
	### this is the final output file
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
		p=Process(target=slicesbin,args=(range(totalshape[0])[start:end],inobjs[i],tempoutputobj))
		p.start()
		processes.append(p)

		print start, end
		start=end
	### wait until all processes finish
	for p in processes:
		p.join()
	print "all finish"
	for i in range(processnumber):
		inobjs[i].close()
	### append temp output files 
	mrcs=np.zeros(0)
	for i in range(processnumber):
		tempfile=open('tempfile'+str(i),'rb')
		tempfile.seek(0)
		tempmrcs=np.fromfile(tempfile,dtype=headerdict['dtype'],count=-1)
		mrcs=np.append(mrcs,tempmrcs)
		tempfile.close()
		os.remove('tempfile'+str(i))
	mrcs.shape=(headerdict['shape'][0],headerdict['shape'][1]/binnumber,headerdict['shape'][2]/binnumber)
	mrc.write(mrcs,outputname)
time2=time.time()
print "spend: ", time2-time1, " seconds"
print "output file as: ", outputname
