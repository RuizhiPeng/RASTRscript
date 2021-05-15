#! /usr/bin/env python
from pyami import mrc
import numpy as np
import math
size=300
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
