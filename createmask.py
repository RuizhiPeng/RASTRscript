#! /usr/bin/env python
import mrcfile
import numpy as np
from scipy.ndimage import gaussian_filter

def cylinder():
	size=608
	a=np.zeros((size,size,size))
	radius=91
	center=303.5

	x, y, z = np.indices((size, size, size))
	mask = ((x-center)**2 + (y-size/2+0.5)**2 < radius**2)
	a[mask] = 1.0

	a=gaussian_filter(a,sigma=3)
	a = np.clip(a, 0, 1)
	
	with mrcfile.new('cylindermask_radius{}_center{}_size{}.mrc'.format(radius, center, size)) as mrc:
		mrc.set_data(a)


def wedge():
	size=240
	angle=160
	a=np.zeros((size,size,size))
	center=size/2-0.5
	angle_radian=angle*np.pi/360
	height=168
	radius=83

	x, y, z = np.indices((size, size, size))
	mask1 = z < (size-1+height)/2
	mask2 = z > (size-1-height)/2
	mask3 = (x-center)**2 + (y-center)**2< radius**2
	mask4 = np.abs(y-center) < (x-center)*np.tan(angle_radian)
	mask5 = x > center
	a[mask1 & mask2 & mask3 & mask4 & mask5] = 1.0

	with mrcfile.new('wedgemask_angle{}_height{}_radius{}.mrc'.format(angle, height, radius)) as mrc:
		mrc.set_data(a)


def sphere():
	boxsize=480
	center=312
	radius=80
	a=np.zeros((boxsize,boxsize,boxsize))

	x, y, z = np.indices((boxsize, boxsize, boxsize))
	mask = ((x-center)**2 + (y-boxsize/2+0.5)**2 + (z-boxsize/2+0.5)**2 < radius**2)
	a[mask] = 1.0

	a=gaussian_filter(a,sigma=3)
	a = np.clip(a, 0, 1)

	with mrcfile.new('sphere_{}_x{}_r{}.mrc'.format(boxsize, center, radius)) as mrc:
		mrc.set_data(a)


def rectangular():
	boxsize=240
	length=200
	height=50
	a=np.zeros((boxsize,boxsize,boxsize))

	x, y, z = np.indices((boxsize, boxsize, boxsize))
	mask1 = x < boxsize/2-0.5 + length/2
	mask2 = x > boxsize/2-0.5 - length/2
	mask3 = y < boxsize/2-0.5 + length/2
	mask4 = y > boxsize/2-0.5 - length/2
	mask5 = z < boxsize/2-0.5 + height/2
	mask6 = z > boxsize/2-0.5 - height/2
	a[mask1 & mask2 & mask3 & mask4 & mask5 & mask6] = 1.0

	a=gaussian_filter(a,sigma=3)
	a = np.clip(a, 0, 1)

	with mrcfile.new('rectangular_{}_length{}_h{}.mrc'.format(boxsize, length, height)) as mrc:
		mrc.set_data(a)

sphere()

