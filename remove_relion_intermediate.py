#! /usr/bin/env python

import os
import sys

ifdry=False
try:
	ifdry=sys.argv[1]
	if ifdry=='dry':
		ifdry=True
except:
	pass
def identify_jobfolder():
	dir_path=os.getcwd()
	try:
		if dir_path.split('/')[-1][:3]=='job':
			print ('currently in job directory, will remove intermediate results')
			return True
		else:
			print ('not in job directory, will remove intermediates in all subfolders')
			return False
	except:
		pass
def removefile(filename):
	if ifdry:
		pass
	elif not ifdry:
		os.remove(filename)


def getiterations(filelist):
	iteration=0
	for i in filelist:
		try:
			if int(i.split('_it')[1].split('_')[0])>iteration:
				iteration=int(i.split('_it')[1].split('_')[0])
			else:
				continue
		except:
			pass
	return iteration
def removejobintermediates(path):
	print ('  in %s' %path)
	filelist=os.listdir(path)
	iteration=getiterations(filelist)
	print ('    detected %i interations' %iteration)
	for i in filelist:
		if i.split('.')[-1]=='mrc' or i.split('.')[-1]=='mrcs':
			if '_it' in i:
				if 'it%03i' %iteration not in i:
					filename=(path+'/'+i).replace('//','/')
					removefile(filename)
					print ('      removing %s' %filename)
	print ('    remove completed')

def get_all_jobfolders(jobfolders,path):
	fileobj=os.walk(path)
	for a,b,c in fileobj:
		if a=='.':
			continue
		if 'job' in a:
			jobfolders.append(a)
		if b!=[]:
			for sb in b:
				jobfolders=get_all_jobfolders(jobfolders,a+sb)
	return jobfolders

def main():
	if not ifdry:
		command=input('not in dry mode, print y to continue: ')
		if command!='y':
			sys.exit()
	ifjob=identify_jobfolder()
	if ifjob:
		removejobintermediates('.')
	elif not ifjob:
		jobfolders=get_all_jobfolders([],'.')
		print ('  detected %i job folders' %len(jobfolders))
		for i in jobfolders:
			removejobintermediates(i)
if __name__ =='__main__':
	main()

