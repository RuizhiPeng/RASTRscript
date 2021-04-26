#! /usr/bin/env python
import os
from matplotlib import pyplot



### get total iterations
def countits(files):
	modelfiles=[]
	itnumber=0
	for sfile in files:
		if sfile[-10:]=='model.star':
			itnumber+=1	
	return itnumber


### get information for project
def initial(files):
	result={}
	for sfile in files:
		### get into any optimiser file
		if sfile[-14:]=='optimiser.star':
			a=open(sfile,'r')
			lines=a.readlines()
			a.close()
			for line in lines:
				if len(line)>18:
					### get output root name for relion project, typically 'run'
					if line[:18]=='_rlnOutputRootName':
						name=line.split()[1]
						result['rootname']=name
						break
			break
	a=open(name.split('/')[2]+'_it000_model.star','r')
	lines=a.readlines()
	a.close()
	### get total classes
	for line in lines:
		if len(line)>13:
			if line[:13]=='_rlnNrClasses':
				classes=line.split()[1]
				result['classes']=int(classes)
				break
	return result

		


### pyplot show function, show resolution first, then distribution
def show(itnumber,res=None,percent=None):
	for i in res:
		pyplot.plot(range(itnumber),res[i])
	pyplot.legend([i for i in res])
	pyplot.xlabel('iteration')
	pyplot.ylabel('resolution')
	pyplot.show()
	for i in res:
		pyplot.plot(range(itnumber),percent[i])
	pyplot.legend([i for i in res])
	pyplot.xlabel('iteration')
	pyplot.ylabel('distribution')
	pyplot.show()
	pass

### open it000_model file to get position of resolution and distribution
def dataposition(filename):
	a=open(filename,'r')
	lines=a.readlines()
	a.close()
	position={}
	for line in lines:
		if len(line)>14:
			if line.split()[0]=='_rlnClassDistribution':
				position['percent']=int(line.split()[1][1:])-1
			elif line.split()[0]=='_rlnEstimatedResolution':
				position['res']=int(line.split()[1][1:])-1
			
			if line=='data_model_class_1\n':
				break
	return position

def analyze():
	files=os.listdir('.')
	### initialization
	itnumber=countits(files)
	initials=initial(files)
	rootname=initials['rootname']
	classes=initials['classes']	

	### get a list of strings of classname
	classname=[]
	for clas in range(classes):
		classname.append('class'+str('%03i' %(clas+1)))
	### create res, percent blank dictionary
	res={}
	percent={}
	for i in classname:
		res[i]=[]	
		percent[i]=[]
	
	position=dataposition(rootname.split('/')[2]+'_it000_model.star')


	### append model file stepwise
	for i in range(itnumber):
		iteration='it'+str('%03i' %i)
		a=open(rootname.split('/')[2]+'_'+iteration+'_model.star','r')
		lines=a.readlines()
		a.close()
		
		for line in lines:
			if len(line)>len(rootname):
				words=line.split()
				if words[0][:len(rootname)]==rootname:
					res[words[0][(len(rootname)+7):-4]].append(float(words[position['res']]))
					percent[words[0][(len(rootname)+7):-4]].append(float(words[position['percent']]))
				if line=='data_model_class_1\n':
					break
	return itnumber,res,percent


def main():
	itnumber,res,percent=analyze()
	show(itnumber,res,percent)
	pass



main()
