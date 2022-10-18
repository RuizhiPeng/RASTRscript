#! /usr/bin/env python
#### this script is for changing image path name for cs transferred star file. Relion3 don't take .mrc as particle stack, so we have to change both the path, and the suffix
#### usage ./xxx.py originalstar outputstarname  cryosparcjobpath
#### jobpath should be down to project directory eg '/scratch2/ruizhi/21nov12a/P69'
import sys


file_1=sys.argv[1]
file_2=sys.argv[2]
job_prefix=sys.argv[3]


a=open(file_1,'r')
lines=a.readlines()
a.close()

newlines=[]
particlesstart=False
for line in lines:
	words=line.split()
	### write optics part without changing anything
	if not particlesstart:
		newlines.append(line)
	### write particls column part without changing anything
	elif particlesstart and len(words)<=2:
		newlines.append(line)
    ### decide if particles part started
	if line=='data_particles\n':
		particlesstart=True
	### change first column path name. First column should be image name if csparc2star.py works correctly
	if particlesstart and len(words)>2:
		if job_prefix[-1]!='/':
			job_prefix+='/'
		#### words[0] should be image name column in default.
		if words[0][-4:]=='.mrc':
			words[0]=job_prefix.join(words[0].split('>'))+'s'
		elif words[0][-5:]=='.mrcs':
			words[0]=job_prefix.join(words[0].split('>'))

		### words[1] should be micrograph names
		if words[1][-4:]=='.mrc':
			words[1]=job_prefix.join(words[1].split('>'))+'s'
		elif words[1][-5:]=='.mrcs':
			words[1]=job_prefix.join(words[1].split('>'))

		newline=(' ').join(words)+'\n'

		newlines.append(newline)

b=open(file_2,'w')
b.writelines(newlines)
b.close()
