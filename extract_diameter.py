#! /usr/bin/env python

### for extracting particles based on diameter
### usage ./extract_diameter.py  diameter.txt origninalstar.star  output.star

import sys

diameterfile=sys.argv[1]
starfile=sys.argv[2]
outputfile=sys.argv[3]

left=198.0
right=208.0


fileobj=open(diameterfile,'r')
lines=fileobj.readlines()
fileobj.close()

diameters=[]

for line in lines:
	diameters.append(float(line))


fileobj=open(starfile,'r')
lines=fileobj.readlines()
fileobj.close()


imagecolumn=None
newlines=[]
for line in lines:
	words=line.split()
	if len(words)==2:
		if words[0]=='_rlnImageName':
			imagecolumn=int(words[1][1:])-1
	

	if imagecolumn==None or len(words)<=2:
		newlines.append(line)
	if imagecolumn!=None and len(words)>2:
		if diameters[int(words[imagecolumn].split('@')[0])-1]>left and diameters[int(words[imagecolumn].split('@')[0])-1]<right:
			newlines.append(line)


fileobj=open(outputfile,'w')
fileobj.writelines(newlines)
fileobj.close()

