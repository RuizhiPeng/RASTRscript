#! /usr/bin/env python
from pyami import mrc
import numpy as np
import sys

### converting mask file data to have only 1 or 0 value

infile=sys.argv[1]
outfile=sys.argv[2]

vol=mrc.read(infile)
vol[vol<0.8]=0.5
vol[vol>=0.8]=0.
vol[vol==0.5]=1.


#vol[vol==1.]=1
#vol[vol==0.]=0

mrc.write(vol,outfile)
