#! /usr/bin/env python

# Usage ./par2star.py xxx.par yyy.star stack.mrcs
#    or ./par2star.py xxx.par yyy.star stack.star

import sys
import argparse





def main():
	parfile=sys.argv[1]
	starfile=sys.argv[2]

	### determine what stack path to add.
	if sys.argv[3]:
		basefile=sys.argv[3]

	### if input is a stack file, then use it directly
	if basefile.split('.')[-1][:3]=='mrc':
		imagepath=basefile

	### if input is a star file, then process the stack filename.
	star3=False
	opticlines=[]
	if basefile.split('.')[-1]=='star':
		fileobj=open(basefile,'r')
		lines=fileobj.readlines()
		fileobj.close()

		imagecolumn=None
		### get image column number
		for line in lines:
			words=line.split()
			if words[0]=='_rlnImageName':
				imagecolumn=int(words[1][1:])-1
			if not imagecolumn or len(words)<=2:
				continue
			elif imagecolumn!=None and len(words)>2:
				imagepath=words[imagecolumn].split('@')[1]
				break

		### get optic data
		### if file is star3 with optic part, then directly use them
		for line in lines:
			words=line.split()
			if line=='data_optics\n':
				print('found optics data in base file')
				star3=True
			if line=='data_particles\n':
				break
			if star3:
				opticlines.append(line)
	if not star3 or not sys.argv[3]:
	### if file is not star3 with optics, then manual enter them
		print('base file not found or not star3 type, manual input optics:')
		optics=[]
		optics.append(raw_input('voltage(kev): '))
		optics.append(raw_input('spherical aberration: '))
		optics.append(raw_input('amplitude contrast: '))
		optics.append('1')
		optics.append(raw_input('box size: '))
		optics.append(raw_input('pixel size: '))
		optics.append('2')
		opticlines.append('data_optics\n')
		opticlines.append('loop_\n')
		opticlines.append('_rlnVoltage #1\n')
		opticlines.append('_rlnSphericalAberration #2\n')
		opticlines.append('_rlnAmplitudeContrast #3\n')
		opticlines.append('_rlnOpticsGroup #4\n')
		opticlines.append('_rlnImageSize #5\n')
		opticlines.append('_rlnImagePixelSize #6\n')
		opticlines.append('_rlnImageDimensionality #7\n')
		opticlines.append(' '.join([str(item) for item in optics])+'\n')


	### start processing datas
	fileobj=open(parfile,'r')
	lines=fileobj.readlines()
	fileobj.close()

	newlines=[]
	### copy optic part first
	for line in opticlines:
		newlines.append(line)

	### write particle head part	
	newlines.append(' \n')
	newlines.append('data_particles\n')
	newlines.append('loop_\n')
	newlines.append('_rlnImageName #1\n')
	newlines.append('_rlnAnglePsi #2\n')
	newlines.append('_rlnAngleTilt #3\n')
	newlines.append('_rlnAngleRot #4\n')
	newlines.append('_rlnOriginXAngst #5\n')
	newlines.append('_rlnOriginYAngst #6\n')
	newlines.append('_rlnDefocusU #7\n')
	newlines.append('_rlnDefocusV #8\n')
	newlines.append('_rlnDefocusAngle #9\n')
	newlines.append('_rlnPhaseShift #10\n')
	newlines.append('_rlnCoordinateX #11\n')
	newlines.append('_rlnCoordinateY #12\n')
	newlines.append('_rlnOpticsGroup #13\n')

	for line in lines:
		words=line.split()
		if words[0]=='C':
			continue
		words[0]=words[0]+'@'+imagepath
		words[4]=-1*float(words[4])
		words[5]=-1*float(words[5])
		del words[12:]
		del words[7]
		del words[6]
		words.append(0.0)
		words.append(0.0)
		words.append(1)
		newline=' '.join([str(item) for item in words])+'\n'
		newlines.append(newline)
	
	fileobj=open(starfile,'w')
	fileobj.writelines(newlines)
	fileobj.close()



if __name__=='__main__':
	main()
