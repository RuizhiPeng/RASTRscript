#! /usr/bin/env python	
###change star file element to a constant
### Ruizhi's script for change star file manually, changeable elements include _rlnMicrographName, _rlnImageName, _rlnMagnification, _rlnAngleRot, _rlnAngleTilt, _rlnAnglePsi, _rlnOriginX, _rlnOriginY
### string type elements can only be changed to one fixed value
### number type elements can be changed to random(r), plus a number(+), minus a number(-)
### eg: ./changestar.py stack.star stackbin4.star -mag 10000.0
### eg: ./changestar.py generate.star generaterandomphi.star -rot r360    (this will give phi angle a random value between 0.0-360.0


import sys
import argparse
import random
### in this script, it's for changing the address of micrograph and image name due to transfer of mrc file to different computer

### get parse_arg values
def parserInput(args):
	parser=argparse.ArgumentParser(description='what column to change')
	parser.add_argument('-mic', '--micrograph', action='store', default=None, dest='micrograph')
	parser.add_argument('-i', '--image', action='store', default=None, dest='image')
	parser.add_argument('-mag', '--magnification', action='store', default=None, dest='mag')
	parser.add_argument('-rot','--anglerot',action='store',default=None,dest='Rot')
	parser.add_argument('-tilt','--angletilt',action='store',default=None,dest='Tilt')
	parser.add_argument('-psi','--anglepsi',action='store',default=None,dest='Psi')
	parser.add_argument('-x','--shiftx',action='store',default=None,dest='X')
	parser.add_argument('-y','--shifty',action='store',default=None,dest='Y')
	return parser.parse_args(args)
### get parameters' column position. supporting star and par file.
def star_column(filename):
	if filename[-4:]=='star':
		paracolumn={}
		fobj=open(filename,'r')
		lines=fobj.readlines()
		fobj.close()
		for line in lines:
			words=line.split()
			if len(words)==2:
				if words[0]=='_rlnMicrographName':
					paracolumn['mic']=int(words[1][1:])-1
				if words[0]=='_rlnImageName':
					paracolumn['image']=int(words[1][1:])-1
				if words[0]=='_rlnMagnification':
					paracolumn['mag']=int(words[1][1:])-1
				if words[0]=='_rlnAngleRot':
					paracolumn['rot']=int(words[1][1:])-1
				if words[0]=='_rlnAngleTilt':
					paracolumn['tilt']=int(words[1][1:])-1
				if words[0]=='_rlnAnglePsi':
					paracolumn['psi']=int(words[1][1:])-1
				if words[0]=='_rlnOriginX':
					paracolumn['shx']=int(words[1][1:])-1
				if words[0]=='_rlnOriginY':
					paracolumn['shy']=int(words[1][1:])-1
		return paracolumn

def par_column(filename):
	if filename[-3:]=='par':
		paracolumn={}
		paracolumn['mag']=6
		paracolumn['psi']=1
		paracolumn['tilt']=2
		paracolumn['rot']=3
		paracolumn['shx']=4
		paracolumn['shy']=5
		return paracolumn



### main function for updating star file
### input filename to change and a dictionary containing values to change
def updatefile(filename,newvalues,outputname):
	### change input file  with values in dictionary newvalues
	### dic newvalues should contain all string type key and value

	### get file lines
	f=open(filename,"r")
	lines=f.readlines()
	f.close()
	print len(lines)
	### get parameter column position

	if filename[-3:]=='par':
		paracolumn=par_column(filename)
	elif filename[-4:]=='star':
		paracolumn=star_column(filename)


	### change per parameter that need to change
	for paraname in newvalues:
		value=newvalues[paraname]
		### default types
		angletype,valuetype,stringtype=False,False,False
		
		### identify parameter type
		### for angle random will be (0, input) for shift random will be (-input, input)
		### more can be added 
		if paraname=='rot' or paraname=='tilt' or paraname=='psi':
			angletype=True
			valuetype=True
		if paraname=='mag' or paraname=='shx' or paraname=='shy':
			valuetype=True
		if paraname=='mic' or paraname=='image':
			stringtype=True

		particlesstart=False
		for i in range(len(lines)):
			words=lines[i].split()
			### skip top lines
			if lines[i]=='data_particles\n' or lines[i]=='data_\n':
				particlesstart=True
				#print 'here'
			if filename[-3:]=='par' and words[0]=='C':
				continue
			if filename[-4:]=='star' and (not particlesstart or len(words)<=2 or lines[i][0]=='#'):
				continue
			#print 'here'
			if stringtype:
				if paraname=='mic':
					words[paracolumn['mic']]=value
				elif paraname=='image':
					words[paracolumn['image']]=words[paracolumn['image']].split('@')[0]+'@'+value
				lines[i]=' '.join(words)+'\n'
				continue
			#print valuetype,angletype
			if valuetype:
				### more can be added
				#### r means random
				if value[0]=='r' and angletype:
					words[paracolumn[paraname]]=str(random.uniform(0,float(value[1:])))
					#print words[paracolumn[paraname]]
				elif value[0]=='r' and not angletype:
					words[paracolumn[paraname]]=str(random.uniform(-1*float(value[1:]),float(value[1:])))
				#### add angle to original
				elif value[0]=='+':
					newvalue=float(words[paracolumn[paraname]])+float(value[1:])
					while angletype and newvalue>360:
						newvalue=newvalue-360
					words[paracolumn[paraname]]=str(newvalue)
					#print words[paracolumn[paraname]]
				#### minus angle to original
				elif value[0]=='-':             
					newvalue=float(words[paracolumn[paraname]])-float(value[1:])
					while angletype and newvalue<0:
						newvalue=newvalue+360
					words[paracolumn[paraname]]=str(newvalue)
				else:
					words[paracolumn[paraname]]=value
				lines[i]=' '.join(words)+' \n'
				continue
			if filename[-3:]=='par':
				### par file only contain value type data
				for j in range(len(words)):
					words[j]=float(words[j])
					### but for column0 (image number), 6(mag), 7(include), 13(logP), they are int
					words[0]=int(words[0])
					words[6]=int(words[6])
					words[7]=int(words[7])
					words[13]=int(words[13])
					lines[i]='%7d %7.2f %7.2f %7.2f   %7.2f   %7.2f %7d %5d %8.1f %8.1f %7.2f %7.2f %7.2f %9d %10.4f %7.2f %7.2f\n' %(words[0],words[1],words[2],words[3],words[4],words[5],words[6],words[7],words[8],words[9],words[10],words[11],words[12],words[13],words[14],words[15],words[16])
				continue
	### write updated file
	fileobj=open(outputname,'w')
	fileobj.writelines(lines)
	fileobj.close()

def main():
	argv=sys.argv
	#get file name
	filename=argv[1]
	outfile=argv[2]
	#get parse value(what to update
	parse=parserInput(argv[3:])
	newvalues={}
	if parse.micrograph:
		newvalues['mic']=parse.micrograph
	if parse.image:
		newvalues['image']=parse.image
	if parse.mag:
		newvalues['mag']=parse.mag
	if parse.Rot:
		newvalues['rot']=parse.Rot
	if parse.Tilt:
		newvalues['tilt']=parse.Tilt
	if parse.Psi:
		newvalues['psi']=parse.Psi		
	if parse.X:
		newvalues['shx']=parse.X
	if parse.Y:
		newvalues['shy']=parse.Y
	#update and write
	print newvalues
	updatefile(filename,newvalues,outfile)

if __name__ == '__main__':
	main()
