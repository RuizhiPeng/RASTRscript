#! /usr/bin/env python

### for extracting particles from cryosparc output star
### usage  ./exclude.py  cryosparc.star  originalstack.star  newname.star

import sys



a=sys.argv[1]
b=sys.argv[2]
fileobj=open(a,'r')
cryolines=fileobj.readlines()
fileobj.close()
fileobj=open(b,'r')
lines=fileobj.readlines()
fileobj.close()


imagelist=[]
for i in range(len(cryolines)):
	words=cryolines[i].split()
	imagelist.append(int(words[0].split('@')[0]))

newlines=[]
for line in lines:
	words=line.split()
	if len(words)>5:
		i=int(words[3].split('@')[0])
		if i in imagelist:
			pass
		else:
			continue
	newlines.append(line)
c=sys.argv[3]
fileobj=open(c,'w')
fileobj.writelines(newlines)
fileobj.close()
	
