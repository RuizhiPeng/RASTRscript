#!/usr/bin/env python

### usage: ./randomphi.py inputfile
### inputfile should be .par file

import os
import sys
import random

def parseFrealignXParamFile(paramfile):
	"""
	parse a typical FREALIGN X parameter file 
	"""
	if not os.path.isfile(paramfile):
		print "Parameter file does not exist: %s"%(paramfile)

	f = open(paramfile, "r")
	parttree = []
	print "Processing parameter file: %s"%(paramfile)
	for line in f:
		sline = line.strip()
		if sline[0] == "C":
			### comment line
			continue
		words=sline.split()
		
		partdict = {
			'ptclnum': int(words[0]),
			'psi': float(words[1]),
			'theta': float(words[2]),
			'phi': float(words[3]),
			'shx': float(words[4]),
			'shy': float(words[5]),
			'mag': float(words[6]),
			'include': int(words[7]),
			'df1': float(words[8]),
			'df2': float(words[9]),
			'angast': float(words[10]),
			'pshift': float(words[11]),
			'occ': float(words[12]),
			'logp': int(words[13]),
			'sigma': float(words[14]),
			'score': float(words[15]),
			'change': float(words[16]),

		}
		parttree.append(partdict)
	f.close()
	if len(parttree) < 2:
		print "No particles found in parameter file %s"%(paramfile)


	print "Processed %d particles"%(len(parttree))
	return parttree
	
def writeParticleParamLine(particleparams, fileobject):
	p=particleparams
	fileobject.write("%7d %7.2f %7.2f %7.2f   %7.2f   %7.2f %7d %5d %8.1f %8.1f %7.2f %7.2f %7.2f %10d %10.4f %7.2f %7.2f\n" 
		% (p['ptclnum'],p['psi'],p['theta'],p['phi'],p['shx'],p['shy'],p['mag'],
		p['include'],p['df1'],p['df2'],p['angast'],p['pshift'],p['occ'],p['logp'],p['sigma'],p['score'],p['change']))


if __name__=="__main__":
	inpar=sys.argv[1]
	outpar=inpar[:-4]+'randomphi.par'
	ptcllst=parseFrealignXParamFile(inpar)
	f=open(outpar,'w')
	thetas=[90,270]
	for ptcl in ptcllst:
		ptcl['phi']=float(random.randint(0,360))
		random.shuffle(thetas)
		#ptcl['shx']+=10
		#ptcl['theta']=thetas[0]
		writeParticleParamLine(ptcl,f)
	f.close()
