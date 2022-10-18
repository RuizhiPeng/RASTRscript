#! /usr/bin/env python
### this script is to extract micrograph names from star file.
### cryosparc didn't contain micrographs names in curate exposure output cs files. In particle picking output cs files, micrographs names exist.
### so this script is targeted to extract and delete repeating micrographs names in particle output cs2star files.

import os
import sys


starfile=sys.argv[1]
a=open(starfile,'r')
lines=a.readlines()
a.close()


micrographs=[]
micrograph_position=None
for line in lines:
	words=line.split()
	if len(words)<2:
		continue
	if words[0][0]=='#':
		continue
	if words[0]=='_rlnMicrographName':
		print ('here')
		micrograph_position=int(words[1][1:])-1
	if micrograph_position!=None:
		if len(words)>2:
			micrograph='_'.join(words[micrograph_position].split('/')[-1].split('_')[1:])+'\n'
			if micrograph in micrographs:
				continue
			else:
				micrographs.append(micrograph)

try:
	outputfile=sys.argv[2]
except:
	outputfile='extractmicrographs_output.txt'

a=open(outputfile,'w')
a.writelines(micrographs)
a.close()

