#! /usr/bin/env python
import sys


### this is script for cut a whole big star file to a small one with part of it's particles

originstar=sys.argv[1]
outputstar=sys.argv[2]

f=open(originstar,'r')
lines=f.readlines()
f.close()
nlines=lines[0:128]

g=open(outputstar,'w')
g.writelines(nlines)
g.close() 
	
