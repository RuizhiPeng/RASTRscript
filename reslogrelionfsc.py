#!/usr/bin/env python

from appionlib import starFile
import optparse
import sys
import os
import math
import subprocess
import glob
#which relion_postprocess` --mask mask.mrc --i reslog1000/half1.mrc --o reslog1000/postprocess --angpix 0.599 --auto_bfac --autob_lowres 10

def parseOptions():
	parser=optparse.OptionParser()
	parser.add_option('--apix', dest='apix', type='float', help='input star file')
	parser.add_option('--mask', dest='mask', type='str', help='path to mask')
	parser.add_option('--out', dest='out', type='str', help='reslog out')
	parser.add_option('--dryrun', dest='dryrun', action='store_true', default=False , help='queue to launch job')
	options, args=parser.parse_args()

	if len(args) != 0 or len(sys.argv) == 1:
		parser.print_help()
		sys.exit()
	
	return options
	
	
	
if __name__=="__main__":

	options=parseOptions()
	
	#find reslog directories
	directories=glob.glob('reslog*')
	resloglst=[]
	for d in directories:
		command=['relion_postprocess', '--auto_bfac', '--autob_lowres', '10']
		half1=os.path.join(d,'half1.mrc')
		command.append('--i')
		command.append(half1)
		output=os.path.join(d,'postprocess')
		command.append('--o')
		command.append(output)
		command.append('--angpix')
		command.append(str(options.apix))
		command.append('--mask')
		command.append(options.mask)
		print (command)
		returned=subprocess.run(command)
		
		#parse input star file
		star=starFile.StarFile(os.path.join(d,'particles.star'))
		star.read()
		particlesname='data_particles'
		particlesblock=star.getDataBlock(particlesname)
		particlelabels=particlesblock.getLabelDict()
		particledata=particlesblock.getLoopDict()	
		totalparticles=len(particledata)
		
		#parse fsc star
		star=starFile.StarFile(os.path.join(d,'postprocess.star'))
		star.read()
		postname='data_general'
		postblock=star.getDataBlock(postname)
		postlabels=postblock.getLabelDict()
		resolution=postlabels['_rlnFinalResolution']
		resloglst.append([totalparticles,resolution])
		#print (resloglst)
	resloglst.sort()
	f=open(options.out,'w')
	f.write("nptcls\tfsc0.143\tfscfreq0.143\n")
	for line in resloglst:
		freq=1/float(line[1])
		f.write("%s\t%s\t%f\n" % (line[0],line[1],freq))
	f.close()
			
	print ("Done!")
