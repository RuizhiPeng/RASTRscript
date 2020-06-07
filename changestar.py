#! /usr/bin/env python	
###change star file element to a constant

import sys
import argparse
### in this script, it's for changing the address of micrograph and image name due to transfer of mrc file to different computer


def parserInput(args):
	parser=argparse.ArgumentParser(description='what column to change')
	parser.add_argument('-mic', '--micrograph', action='store', default=None, dest='micrograph')
	parser.add_argument('-i', '--image', action='store', default=None, dest='image')
	parser.add_argument('-mag', '--magnification', action='store', default=None, dest='mag')
	return parser.parse_args(args)




def updateStar(filename,pobj):
	filename=sys.argv[1]
	f=open(filename,"r")
	lines=f.readlines()
	f.close()
	nlines=[]
	for line in lines:
		words=line.split()
		try:
			if words[0]:
				if words[0]=='_rlnMicrographName':
					column_mic=int(words[1][1:])
				if words[0]=='_rlnImageName':
					column_image=int(words[1][1:])
				if words[0]=='_rlnMagnification':
					column_mag=int(words[1][1:])
				pass
		except:
			nlines.append(line)
			continue
		try:
			if len(words)>2:
				if pobj.micrograph:
					words[column_mic-1]=pobj.micrograph
				if pobj.image:
					words[column_image-1]=words[column_image-1].split('@')[0]+'@'+pobj.image
				if pobj.mag:
					words[column_mag-1]=pobj.mag
		except:
			nlines.append(line)
			continue
		string=' '
		line=string.join(words)+'\n'
		nlines.append(line)
	f=open(filename.split('.')[0]+'_updated.'+filename.split('.')[1],'w')
	f.writelines(nlines)
	f.close



if __name__ == '__main__':
	filename=sys.argv[1]
	pobj=parserInput(sys.argv[2:])
	newstar=updateStar(filename,pobj)
