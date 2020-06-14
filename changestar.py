#! /usr/bin/env python	
###change star file element to a constant

import sys
import argparse
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
	return parser.parse_args(args)



### main function for updating star file
def updateStar(filename,parse):
	f=open(filename,"r")
	lines=f.readlines()
	f.close()
	nlines=[]
	append=nlines.append
	### initialize column value
	micrograph,image,mag,Rot,Tilt,Psi=None,None,None,None,None,None
	if parse.micrograph:
		micrograph=parse.micrograph
	if parse.image:
		image=parse.image
	if parse.mag:
		mag=parse.mag
	if parse.Rot:
		Rot=parse.Rot
	if parse.Tilt:
		Tilt=parse.Tilt
	if parse.Psi:
		Psi=parse.Psi
	for line in lines:
		words=line.split()
		### get column position
		try:
			if words[0]:
				if words[0]=='_rlnMicrographName':
					column_mic=int(words[1][1:])-1
				if words[0]=='_rlnImageName':
					column_image=int(words[1][1:])-1
				if words[0]=='_rlnMagnification':
					column_mag=int(words[1][1:])-1
				if words[0]=='_rlnAngleRot':
					column_rot=int(words[1][1:])-1
				if words[0]=='_rlnAngleTilt':
					column_tilt=int(words[1][1:])-1
				if words[0]=='_rlnAnglePsi':
					column_psi=int(words[1][1:])-1
				pass
		except:
			append(line)
			continue
		### update value
		try:
			if len(words)>2:
				if micrograph:
					words[column_mic]=micrograph
				if image:
					words[column_image]=words[column_image].split('@')[0]+'@'+image
				if mag:
					words[column_mag]=mag
				if Rot:
					words[column_rot]=Rot
				if Tilt:
					words[column_tilt]=Tilt
				if Psi:
					words[column_psi]=Psi
		except:
			append(line)
			continue
		blank=' '
		line=blank.join(words)+'\n'
		append(line)
	### write updated file
	f=open(filename.split('.')[0]+'_updated.'+filename.split('.')[1],'w')
	f.writelines(nlines)
	f.close

def main():
	argv=sys.argv
	#get file name
	filename=argv[1]
	#get parse value(what to update
	parse=parserInput(argv[2:])
	#update and write
	updateStar(filename,parse)

if __name__ == '__main__':
	main()
