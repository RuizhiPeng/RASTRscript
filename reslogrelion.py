#!/usr/bin/env python

from appionlib import starFile
from appionlib import apRelion
import optparse
import sys
import os
import math
import subprocess

def logSplit(start,end,divisions):
	end=math.log(end)
	start=math.log(start)
	incr=(end-start)/divisions
	val=start
	stacklist=[]
	for n in range(0, divisions):
		nptcls=int(round(math.exp(val)))
		stacklist.append(nptcls)
		val+=incr
	print ("Making stacks of the following sizes",stacklist)
	return(stacklist)	

def parseOptions():
	parser=optparse.OptionParser()
	parser.add_option('--star', dest='star', type='str', help='input star file')
	parser.add_option('--sym', dest='sym', type='str', help='symmetry to apply')
	parser.add_option('--queue', dest='queue', type='str', help='queue to launch job')
	parser.add_option('--mem', dest='mem', type='str', help='queue to launch job')
	parser.add_option('--dryrun', dest='dryrun', action='store_true', default=False , help='queue to launch job')
	parser.add_option('--min', dest='min', type='int', default=1000 , help='minimum number of particles')
	parser.add_option('--divisions', dest='divisions', type='int', default=10, help='number of reslog divisions')
	options, args=parser.parse_args()

	if len(args) != 0 or len(sys.argv) == 1:
		parser.print_help()
		sys.exit()
	
	return options

def starDataOut(blockdata):
	datalst=[]
	labels=list(blockdata[0].keys())
	for line in blockdata:
		params = ""
		for p in list(line.values()):
			params += " %s" % p
		datalst.append(params)
	return labels, datalst
	
def writeStar(starname,opticdata,particledata):
	outstar=starFile.StarFile(starname)
	
	#optics block
	opticlabelsout, opticdataout=starDataOut(opticdata)
	outstar.buildLoopFile(opticname,opticlabelsout,opticdataout)
	
	#particles block
	particlelabelsout,particledataout=starDataOut(particledata)
	outstar.buildLoopFile(particlesname,particlelabelsout,particledataout)
	
	outstar.write()

def makeStarDataWithSpecifiedNPtcls(particledata,nptcls):
	skip=len(particledata)//nptcls
	newparticledata=[]
	for n in range(0,len(particledata),skip):
		newparticledata.append(particledata[n])
	
	#before count
	evencount,oddcount=_countevenodd(newparticledata)
	
	#make same number of particles
	if evencount>oddcount:
		remove=evencount-oddcount
		count=0
		for n,ptcl in enumerate(newparticledata):
			if int(ptcl['_rlnRandomSubset']) == 2:
				newparticledata.pop(n)
				count+=1
			if count==remove:
				break
	elif oddcount>evencount:
		remove=oddcount-evencount
		count=0
		for n,ptcl in enumerate(newparticledata):
			if int(ptcl['_rlnRandomSubset']) == 1:
				newparticledata.pop(n)
				count+=1
			if count==remove:
				break
	
	_countevenodd(newparticledata)	
	
	return newparticledata

def _countevenodd(particledata):
	evencount=0
	oddcount=0
	for ptcl in particledata:
		if int(ptcl['_rlnRandomSubset']) == 1:
			oddcount+=1
		elif int(ptcl['_rlnRandomSubset']) == 2:
			evencount+=1
		else:
			print ("Warning, unexpected subset number")
			sys.exit()
	print ("%d particles, %d in subset 1, %d in subset 2" % (len(particledata), oddcount, evencount))
	return evencount,oddcount

def launchjob(command, options):
	#fullcommand='sbatch --mem %s -p %s --wrap="%s"' % (options.mem, options.queue, command)
	fullcommand=command
	print (fullcommand)
	if options.dryrun is False:
		s=subprocess.run(fullcommand, shell=True)
		print (s)
		print ('now running')
	
	
if __name__=="__main__":

	options=parseOptions()
	
	#parse input star file
	star=starFile.StarFile(options.star)
	star.read()
	opticname='data_optics'
	opticblock=star.getDataBlock(opticname)
	opticlabels=opticblock.getLabelDict()
	opticdata=opticblock.getLoopDict()
	
	particlesname='data_particles'
	particlesblock=star.getDataBlock(particlesname)
	particlelabels=particlesblock.getLabelDict()
	particledata=particlesblock.getLoopDict()
	
	totalparticles=len(particledata)
	
	#get reslog particle numbers
	particlesizelist=logSplit(options.min,totalparticles,options.divisions)
	#particlesizelist.pop()
	
	#make star with appropriate number of particles
	for size in particlesizelist:
		dirname='reslog'+str(size)
		if not os.path.exists(dirname):
			os.mkdir(dirname)
		newparticledata=makeStarDataWithSpecifiedNPtcls(particledata,size)
		starpath=os.path.join(dirname,'particles.star')
		writeStar(starpath,opticdata,newparticledata)
		half1=os.path.join(dirname,'half1.mrc')
		half2=os.path.join(dirname,'half2.mrc')
		command1='relion_reconstruct --i %s --o %s --sym %s --ctf --subset 1' % (starpath, half1, options.sym)
		command2='relion_reconstruct --i %s --o %s --sym %s --ctf --subset 2' % (starpath, half2, options.sym)
		launchjob(command1, options)
		launchjob(command2, options)
		
		
		
		
	
	print ("Done!")
