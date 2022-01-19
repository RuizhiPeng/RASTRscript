#! /usr/bin/env python
### usage ./diameter_classify.py starfile.star


from datetime import datetime
import numpy as np
import math
from scipy.ndimage import rotate
import sys
from pyami import mrc
from matplotlib import pyplot
def rotation(image_array,psi):
	if psi!=0:
		#print psi
		newarray=rotate(image_array,-psi,axes=(0,1),order=1,reshape=False)
	else:
		newarray=image_array
	return newarray


def find_peak(array_1d):
	from scipy.signal import find_peaks
	localhighs=find_peaks(array_1d)[0]
	peak_1=0
	peak_2=0
	for i in localhighs:
		if array_1d[i]>array_1d[peak_1]:
			peak_1=i
	for i in localhighs:
		if abs(peak_1-i)>20:
			if array_1d[i]>array_1d[peak_2]:
				peak_2=i


	return peak_1,peak_2

### get a list of psi angles
def get_psi(starfile):
	fileobj=open(starfile,'r')
	lines=fileobj.readlines()
	fileobj.close()

	psiangles=[]
	psicolumn=None
	for line in lines:
		words=line.split()
		if len(words)>0:
			if words[0]=='_rlnAnglePsi':
				psicolumn=int(words[1][1:])-1
		if psicolumn!=None and len(words)>2:
			psiangles.append(float(words[psicolumn]))

	return psiangles

### get a list of tuples, imagepaths[x][0] refer zslice, imagepaths[x][1] refer stack file. In most cases, stack file is the same
def get_image(starfile):
	fileobj=open(starfile,'r')
	lines=fileobj.readlines()
	fileobj.close()

	imagepaths=[]
	imagecolumn=None
	for line in lines:
		words=line.split()
		if len(words)>0:
			if words[0]=='_rlnImageName':
				imagecolumn=int(words[1][1:])-1
		if imagecolumn!=None and len(words)>2:
			imagepaths.append((int(words[imagecolumn].split('@')[0])-1,words[imagecolumn].split('@')[1]))
	return imagepaths

def main():
	starfile=sys.argv[1]
	pixelvalue=float(raw_input('pixelvalue?: '))

	psiangles=get_psi(starfile)
	imagepaths=get_image(starfile)
	if len(psiangles) != len(imagepaths):
		print('star file has inconsistent data lines')
		sys.exit()

	diameters=[]
	for i in range(len(imagepaths)):
		image_array=mrc.read(imagepaths[i][1],zslice=imagepaths[i][0])
		image_array=rotation(image_array,psi=psiangles[i])
		pyplot.imshow(image_array)
		pyplot.show()
		image_1d=np.sum(image_array,axis=0)
		pyplot.plot(image_1d)
		pyplot.show()

		diameter=abs((find_peak(image_1d)[0]-find_peak(image_1d)[1])*pixelvalue)
		diameters.append(diameter)
	timepoint=datetime.now().strftime('%Y%m%d%H%M%S')
	with open(timepoint+'diameters.txt','w') as fileobj:
		for i in diameters:
			fileobj.writelines(str(i)+'\n')
	freqs,edges=np.histogram(diameters,bins=5)
#	pyplot.plot(freqs,edges)
#	pyplot.show()

	

if __name__=='__main__':
	main()

