#! /usr/bin/env python
import sys
parfile=sys.argv[1]
datafile=sys.argv[2]
a=open(parfile,'r')
par=a.readlines()
a.close()
b=open(datafile,'r')
data=b.readlines()
b.close()
particles=[]
for line in par:
	words=line.split()
	for word in words:
		if '@' in word:
			particles.append(word.split('@')[0])
print 'particles number: ', len(particles)
count={
'1':0,
'2':0,
'3':0,
'4':0,
'5':0,
'6':0,
'7':0,
'8':0,
'9':0,
'10':0,
}
for line in data:
	words=line.split()
	if len(words)>0:
		if words[0]=='_rlnClassNumber':
			clasnum=int(words[1][1:])-1
	if len(words)>0:
		if words[0]=='_rlnImageName':
			imagenum=int(words[1][1:])-1
	if len(words)>2:
		if words[imagenum].split('@')[0] in particles:
			count[words[clasnum]]+=1


for i in count:
	print i,count[i]
