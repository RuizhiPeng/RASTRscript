#! /usr/bin/env python
from pyami import mrc
import sys
import argparse
import time
import numpy as np

a=np.zeros((100,100,100))
b=a+3
c=a+2
print a.shape
starttime=time.time()
d=b*c






endtime=time.time()
print "total time spent: ", endtime-starttime




starttime=time.time()
d=np.multiply(b,c)

                                                                                                                     



endtime=time.time()
print "total time spent: ", endtime-starttime
