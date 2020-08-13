#! /usr/bin/env python
import sys
filename=sys.argv[1]
f=open(filename,'r')
lines=f.readlines()
f.close()

f=open(filename[0:9]+'_model.star','r')
modellines=f.readlines()
f.close()
for line in modellines:
	words=line.split()
	if len(words)==2 and words[0]=='_rlnNrClasses':
		classnumber=int(words[1])

classcount=[0 for i in range(classnumber)]
for line in lines:
        words=line.split()
        try:
                if words[0]:
                        if words[0]=='_rlnClassNumber':
                                column_class=int(words[1][1:])-1                                 
                        pass
	except:
		continue
	if len(words)>2:
		classcount[int(words[column_class])-1]+=1

print classcount
