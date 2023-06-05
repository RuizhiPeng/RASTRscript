#! /usr/bin/env python
### legacy script, old version cryosparc cannot bin output, so doing this to save hard drive space.

import sys
import os
import time
import subprocess

def onlymrc(filelist):
	newlist=[]
	for f in filelist:
		if 'bin' in f :
			continue
		elif f[-3:]=='mrc':
			newlist.append(f)
	return newlist

def run_command(command):
	print ('---- '+command)
	try:
		if sys.argv[1]=='dry':
			pass
	except:
		pass
	if len(sys.argv)==1:
		process=subprocess.Popen(command.split(), stdout=subprocess.PIPE)
		output, error = process.communicate()


def removemicrograph(f):
	cryosparc_id=f[:21]
	micrographname=f.split('_particles')[0]+'_rigid_aligned.mrc'
	if any(cryosparc_id in i for i in optic1):
		run_command('rm /scratch2/Xiaofeng/Apoferritin/22feb18a/P72/J328/motioncorrected/'+micrographname)
	if any(cryosparc_id in i for i in optic2):
		run_command('rm /scratch2/Xiaofeng/Apoferritin/22feb18a/P72/J306/motioncorrected/'+micrographname)

optic1=onlymrc(os.listdir('/scratch2/Xiaofeng/Apoferritin/22feb18a/P72/J328/motioncorrected/.'))
optic2=onlymrc(os.listdir('/scratch2/Xiaofeng/Apoferritin/22feb18a/P72/J306/motioncorrected/.'))

print(len(sys.argv))
while True:
	filelist=onlymrc(os.listdir('.'))	
	print ('detected %i files' %len(filelist))
	for f in filelist:
		run_command('mv '+f+' '+f+'s')
		f=f+'s'
		command='relion_image_handler --i '+f+' --o '+f[:-5]+'bin2.mrcs'+' --angpix 0.29 --rescale_angpix 0.58'
		run_command(command)
		run_command('rm '+f)

		removemicrograph(f)



	time.sleep(120)
