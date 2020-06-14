#! /usr/bin/env python
import sys
filename=sys.argv[1]
f=open(filename,'r')
lines=f.readlines()
f.close()

classcount=[0,0,0]
for line in lines:
        words=line.split()
        try:
                if words[0]:
                        if words[0]=='_rlnClassNumber':
                                column_class=int(words[1][1:])-1                                 
                        pass
	except:
		continue
	if words[0]=='/gpfs/research/stagg/scratch/rp18j/dynaminN4particles/dynaminrastrn4particlesbin4.mrcs':
		classcount[int(words[column_class])-1]+=1

print classcount
