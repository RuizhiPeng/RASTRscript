#! /usr/bin/env python
### for masking tube particles,instead of dealing the whole, just section the center part for further processing
### usage ./2dmask.py original.mrcs starfile.star  output.mrcs
import numpy as np
from scipy.ndimage import rotate,shift,gaussian_filter
import sys
from pyami import mrc
import copy
def rotate_psi(array_2d,psi,x,y,order=1):
	slice_prj=copy.deepcopy(array_2d)
	if psi!=0:
		slice_prj=rotate(slice_prj,psi,axes=(0,1),reshape=False,order=order)
	slice_prj=shift(slice_prj,shift=(-y,-x),mode='wrap')
	return slice_prj



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

	return psis,xs,ys

def create_2dmask():
	boxsize=240
	length=230
	height=192
	a=np.zeros((boxsize,boxsize))
	for y in range(boxsize):
		for x in range(boxsize):
			if y<boxsize/2-0.5+length/2 and y>boxsize/2-0.5-length/2 and x<boxsize/2-0.5+height/2 and x>boxsize/2-0.5-height/2:
				a[y][x]=1.0
	a=gaussian_filter(a,sigma=3)
	a[a>1]=1.0
	a[a<0]=0.0
	return a



def main():
	inputobj=open(sys.argv[1],'rb')
	headerbytes=inputobj.read(1024)
	inputobj.close()
	headerdict=mrc.parseHeader(headerbytes)

	psis,xs,ys=get_angles(sys.argv[2])

	mrcsobj=open(sys.argv[1],'rb')
	outputobj=open(sys.argv[3],'wb')

	outputobj.write(mrc.makeHeaderData(headerdict))

	maskarray=create_2dmask()

	if len(psis)!=len(xs):
		print('not consistent number of angles, exiting')
		sys.exit()
	for i in range(len(psis)):
		singleslice=mrc.readDataFromFile(mrcsobj,headerdict,zslice=i)
		maskarray_rotated=rotate_psi(maskarray,psis[i],xs[i],ys[i],order=3)
		maskedslice=singleslice*maskarray_rotated
		mrc.appendArray(maskedslice,outputobj)

	mrcsobj.close()
	outputobj.close()


main()












