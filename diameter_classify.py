#! /usr/bin/env python
### usage ./diameter_classify.py starfile.star


import mrcfile
from datetime import datetime
import numpy as np
import math
import cupy as cp
from cupyx.scipy.ndimage import rotate as cprotate
from cupyx.scipy.ndimage import gaussian_filter
from scipy.ndimage import rotate
import sys
from matplotlib import pyplot
from matplotlib.gridspec import GridSpec
import re
import os
from scipy.signal import find_peaks


### rotate 2d particles with psi angle
def rotation(image_array,psi):
	if psi!=0:
		image_array=cprotate(image_array,-psi,axes=(0,1),order=3, mode='constant', reshape=False)
	### as sicpy rotate will still do calculation even if angle is 0, this will save some time.
	return image_array
	

### find the highest two peaks. 
def find_peak(array_1d, min_gap=200):
	localhighs = find_peaks(array_1d)[0]
	peak_1 = max(localhighs, key=lambda x: array_1d[x])
	peak_2_candidates = [i for i in localhighs if abs(peak_1 - i) > min_gap]

	if peak_2_candidates:
		peak_2 = max(peak_2_candidates, key=lambda x: array_1d[x])
	else:
		peak_2 = 0

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


### get a list of tuples. Definition of imagepaths, imagepaths[x][0] refer zslice, imagepaths[x][1] refer stack file. In most cases, stack file is the same
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




### get pixel size from star file, relion3 style.
def get_pixelsize(starfile):
	fileobj=open(starfile,'r')
	lines=fileobj.readlines()
	fileobj.close()

	pixel_size_column=None
	pixel_size=-1

	for line in lines:
		words=line.split()
		if len(words)>0 and line[0]!='#':
			if words[0]=='_rlnImagePixelSize':
				pixel_size_column=int(words[1][1:])-1
			if pixel_size_column!=None and len(words)>2:
				if pixel_size==-1:
					pixel_size=float(words[pixel_size_column])
				### once get value, break the loop	
				elif pixel_size!=-1:
					break
	return pixel_size

### plot diameters in histogram
def plot_diameter(diameter_file):
	diameters=[]
	with open(diameter_file, 'r') as fileobj:
		lines=fileobj.readlines()
		for line in lines:
			diameters.append(float(line))
	diameters=np.array(diameters)
	pyplot.hist(diameters,bins=200)
	pyplot.xlabel('diameter(A)')
	pyplot.ylabel('number of particles')
	pyplot.show()


### raw input range, then output the star file with particles between that range.
def choose_threshold(starfile,diameter_file):
	diameters=[]
	left=float(input("smallest diameter: "))
	right=float(input("biggest diameter: "))
	with open(diameter_file, 'r') as fileobj:
		lines=fileobj.readlines()
		for line in lines:
			diameters.append(float(line))
	newlines=[]
	with open(starfile,'r') as fileobj:
		lines=fileobj.readlines()
		imagecolumn=None
		particledataline=-1
		for line in lines:
			words=line.split()
			if len(words)==2:
				if words[0]=='_rlnImageName':
					imagecolumn=int(words[1][1:])-1
			if imagecolumn==None or len(words)<=2:
				newlines.append(line)
			### assumes when entering particle date, it's all particle data
			if imagecolumn!=None and len(words)>2:
				particledataline+=1
				if diameters[particledataline] >=left and diameters[particledataline]<=right:
					newlines.append(line)

	with open(starfile.split('.')[0]+'_'+str(left)+'2'+str(right)+'.star','w') as fileobj:
		fileobj.writelines(newlines)



def main():

	starfile=sys.argv[1]

	filelists=os.listdir('.')
	input_continue=None
	show = True
	### find previous output diameter files. If exist, ask if use that file directly. 
	for file in filelists:
		if re.match( r'%s_(.*)_diameters.txt' %starfile.split('.')[0], file, re.M|re.I):
			print ('found diameter file: %s' %file)

			### python2 and python3 input function are different.
			if sys.version_info[0]==2:
				input_continue=raw_input("type y to use this file, n to continue: ")
			elif sys.version_info[0]==3:
				input_continue=input("type y to use this file, n to continue: ")
			diameter_file=file

	if input_continue=='y' or input_continue=='Y':
		if diameter_file:
			plot_diameter(diameter_file)
			choose_threshold(starfile,diameter_file)
			sys.exit()

	if input_continue=='' or input_continue=='n':
		pass

	pixelvalue=get_pixelsize(starfile)
	if pixelvalue==-1:
		pixelvalue=float(input('pixel size?: '))

	psiangles=get_psi(starfile)
	imagepaths=get_image(starfile)
	if len(psiangles) != len(imagepaths):
		print('star file has inconsistent data lines')
		sys.exit()

	diameters=[]
	for i in range(len(imagepaths)):
		### read particle array from file imagepaths[i][1], at zslice imagepaths[i][0]
		with mrcfile.mmap(imagepaths[i][1], mode='r') as imagestack:
			zslice = int( imagepaths[i][0] ) - 1
			image_array = imagestack.data[zslice]
			image_array = cp.asarray(image_array)
			#image_array = gaussian_filter(image_array, 5)
			image_array = rotation(image_array, psi=psiangles[i])

#		print (image_array.shape)
		image_1d=cp.sum(image_array,axis=1)
		image_array_vertical = rotation(image_array, psi=-90)
		peak_one,peak_two=find_peak(image_1d.get())
		#print ('peaks: ', peak_one,  peak_two)
		diameter=abs((peak_one-peak_two)*pixelvalue)
		diameters.append(diameter)

		#print( 'diameter: ', diameter)
		if show:		
			fig, (ax1, ax2) = pyplot.subplots(2, 1, figsize=(4,6), gridspec_kw={'height_ratios':[2,1]}, layout="constrained")
			ax1.imshow(image_array_vertical.get(), aspect='equal')
			ax1.set_box_aspect(1)

			ax2.plot(image_1d.get())
			ax2.set_xlim(0,image_1d.shape[0]-1)
			ax2.set_box_aspect(0.5)

			pyplot.show()

	timepoint=datetime.now().strftime('%Y%m%d%H%M%S')
	diameter_file=starfile.split('.')[0]+'_'+timepoint+'_diameters.txt'
	with open(diameter_file,'w') as fileobj:
		for i in diameters:
			fileobj.writelines(str(i)+'\n')
	plot_diameter(diameter_file)
	choose_threshold(starfile,diameter_file)
	

if __name__=='__main__':
	main()

