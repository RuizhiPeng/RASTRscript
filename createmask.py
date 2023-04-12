#! /usr/bin/env python
from pyami import mrc
import numpy as np
import math
from scipy.ndimage import gaussian_filter

def cylinder():
	size=608
	a=np.zeros((size,size,size))
	height=size
	radius=91
	center=303.5
	for z in range(size):
		for y in range(size):
			for x in range(size):
				if (x-center)**2+(y-size/2+0.5)**2 < radius**2:
					a[z][y][x]=1.0
	a=gaussian_filter(a,sigma=3)
	a[a>1]=1.0
	a[a<0]=0.0
	mrc.write(a,'cylindermask_radius'+str(radius)+'_center'+str(center)+'_size'+str(size)+'.mrc')
def wedge():
	size=240
	angle=160
	a=np.zeros((size,size,size))
	center=size/2-0.5
	angle_radian=angle*math.pi/360
	height=168
	radius=83
	for z in range(size):
		for y in range(size):
			for x in range(size):
				if z< (size-1+height)/2 and z>(size-1-height)/2  :
					if (x-center)**2 + (y-center)**2< radius**2:
						if abs(y-center)<(x-center)*math.tan(angle_radian) and x>center:
							a[z][y][x]=1.0


	mrc.write(a,'wedgemask_angle'+str(angle)+'_height'+str(height)+'_radius'+str(radius)+'.mrc')


def sphere():
	boxsize=480
	center=312
	radius=80
	a=np.zeros((boxsize,boxsize,boxsize))
	for z in range(boxsize):
		for y in range(boxsize):
			for x in range(boxsize):
				if (x-center)**2+(y-boxsize/2+0.5)**2+(z-boxsize/2+0.5)**2<radius**2:
					a[z][y][x]=1.0
	a=gaussian_filter(a,sigma=3)
	a[a>1]=1.0
	a[a<0]=0.0
	mrc.write(a,'sphere_'+str(boxsize)+'_x'+str(center)+'_r'+str(radius)+'.mrc')

def rectangular():
	boxsize=240
	length=200
	height=50
	a=np.zeros((boxsize,boxsize,boxsize))
	for z in range(boxsize):
		for y in range(boxsize):
			for x in range(boxsize):
				if x<boxsize/2-0.5+length/2 and x>boxsize/2-0.5-length/2 and y<boxsize/2-0.5+length/2 and y>boxsize/2-0.5-length/2 and z<boxsize/2-0.5+height/2 and z>boxsize/2-0.5-height/2:
					a[z][y][x]=1.0
	a=gaussian_filter(a,sigma=3)
	a[a>1]=1.0
	a[a<0]=0.0
	mrc.write(a,'rectangular_'+str(boxsize)+'_length'+str(length)+'_h'+str(height)+'.mrc')
sphere()
#sphere()
#rectangular()
