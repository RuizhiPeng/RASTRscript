#! /usr/bin/env python

### this is a test script to test if my understanding of angle rotation is correct, the following script is consistent with relion for projections


from pyami import mrc
import sys
import copy
from scipy.ndimage import rotate,shift
import numpy as np

### for rotate volume
def volumerotation(volume,rot=0,tilt=0,psi=0,order=1):
	newvolume=copy.deepcopy(volume)
	if rot!=0:
		newvolume=rotate(newvolume,rot,axes=[1,2],order=order,reshape=False)
	if tilt!=0:
		newvolume=rotate(newvolume,-tilt,axes=[0,2],order=order,reshape=False)
	if psi!=0:
		newvolume=rotate(newvolume,psi,axes=[1,2],order=order,reshape=False)
	return newvolume

### projection of a volume, psi is done on a 2d array to accelerate
def volumeprojection(volume,rot=0,tilt=0,psi=0,x=0,y=0,order=0):
	volume_rotated=volumerotation(volume,rot,tilt,0,order=order)
	slice_prj=np.sum(volume_rotated,axis=0)
	slice_prj=rotate(slice_prj,psi,axes=(0,1),reshape=False,order=order)
	slice_prj=shift(slice_prj,(-y,-x),mode='wrap')
	return slice_prj

### get angles
def get_angles(starfile):
	fileobj=open(starfile,'r')
	lines=fileobj.readlines()
	fileobj.close()

	para_tilt=None
	para_psi=None
	para_rot=None

	psis=[]
	tilts=[]
	rots=[]
	xs=[]
	ys=[]
	for line in lines:
		words=line.split()
		if line[0]=='#':
			continue
		if len(words)==2:
			if words[0]=='_rlnAngleRot':
				para_rot=int(words[1][1:])-1
			if words[0]=='_rlnAngleTilt':
				para_tilt=int(words[1][1:])-1
			if words[0]=='_rlnAnglePsi':
				para_psi=int(words[1][1:])-1
			if words[0]=='_rlnOriginX':
				para_x=int(words[1][1:])-1
			if words[0]=='_rlnOriginY':
				para_y=int(words[1][1:])-1

		if len(words)>2 and para_tilt!=None and para_psi!=None and para_rot!=None:
			tilts.append(float(words[para_tilt]))
			psis.append(float(words[para_psi]))
			rots.append(float(words[para_rot]))
			xs.append(float(words[para_x]))
			ys.append(float(words[para_y]))

	return psis,tilts,rots,xs,ys


def projection(mapfile,psis,tilts,rots,xs,ys,filename):
	volume=mrc.read(mapfile)
	newfile=open(filename,'wb')
	newfile.write(mrc.makeHeaderData(headerdict))

	avg=(len(psis)+len(tilts)+len(rots))/3
	if avg!=len(psis) or avg!=len(tilts) or avg!=len(rots):
		print ('none consistent angle numbers, exiting')
		sys.exit()
	print len(psis)
	### append each slice
	for i in range(20):
		singleproj=volumeprojection(volume,rots[i],tilts[i],psis[i],xs[i],ys[i],order=0)
		mrc.appendArray(singleproj,newfile)

	

### headerdict, using this one just for testing
inputobj=open('drp1selectJ99_960_drp1selectJ99_960bin4_20211229174040.mrcs','rb')
headerdict=mrc.parseHeader(inputobj.read(1024))
### just project 20 to accelerate
headerdict['nz']=20
inputobj.close()



starfile=raw_input('starfile: ')
psis,tilts,rots,xs,ys=get_angles(starfile)
outputfile=raw_input('output: ')
mapfile=raw_input('map: ')
projection(mapfile,psis,tilts,rots,xs,ys,outputfile)















