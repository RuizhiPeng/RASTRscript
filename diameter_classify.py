#! /usr/bin/env python
### usage ./diameter_classify.py starfile.star


from datetime import datetime
import numpy as np
import math
import cupy as cp
from cupy.scipy.ndimage import rotate as cprotate
from scipy.ndimage import rotate
import sys
from pyami import mrc
from matplotlib import pyplot
import re
import os



### rotate 2d particles with psi angle
def rotation(image_array,psi):
	if psi!=0:
		image_array=cprotate(image_array,-psi,axes=(0,1),order=3, mode='constant', reshape=False)
	### as sicpy rotate will still do calculation even if angle is 0, this will save some time.
	return image_array


### find the highest two peaks. 
def find_peak(array_1d):
	from scipy.signal import find_peaks
	localhighs=find_peaks(array_1d)[0]
	peak_1=0
	peak_2=0
	for i in localhighs:
		if array_1d[i]>array_1d[peak_1]:
			peak_1=i
	for i in localhighs:
		### I define two peaks should be separated by at least 20 pixels.
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
	pyplot.hist(diameters,bins=200,normed=0)
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
		pixelvalue=float(raw_input('pixel size?: '))

	psiangles=get_psi(starfile)
	imagepaths=get_image(starfile)
	if len(psiangles) != len(imagepaths):
		print('star file has inconsistent data lines')
		sys.exit()

	diameters=[]
	for i in range(len(imagepaths)):
		### read particle array from file imagepaths[i][1], at zslice imagepaths[i][0]
		image_array=mrc.read(imagepaths[i][1],zslice=imagepaths[i][0])
		image_array=rotation(image_array,psi=psiangles[i])
#		print (image_array.shape)
		image_1d=cp.sum(image_array,axis=1)
		image_array_vertical = rotation(image_array.get(), psi=90)
		peak_one,peak_two=find_peak(image_1d.get())
#		print ('peaks: ', peak_one,  peak_two)
		diameter=abs((peak_one-peak_two)*pixelvalue)
		diameters.append(diameter)

		#print( 'diameter: ', diameter)
		#f, img = pyplot.subplots(2)
		#img[0].imshow(image_array_vertical, aspect='auto')
		#pyplot.show()
		#img[1].plot(image_1d)
		#img[1].set_xlim(0, image_array.shape[1])
		#pyplot.show()

	timepoint=datetime.now().strftime('%Y%m%d%H%M%S')
	diameter_file=starfile.split('.')[0]+'_'+timepoint+'_diameters.txt'
	with open(diameter_file,'w') as fileobj:
		for i in diameters:
			fileobj.writelines(str(i)+'\n')
	plot_diameter(diameter_file)
	choose_threshold(starfile,diameter_file)
	

if __name__=='__main__':
	main()

