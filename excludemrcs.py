#! /usr/bin/env python
### usage ./*.py  inputfilepath outputfilepath  framelist(format: 1,2,3)

from pyami import mrc
import sys
import numpy as np

### parse mrc file headers, return a dictinary
def readHeaders(particlestacks):
        f=open(particlestacks,'rb')
        headerbytes=f.read(1024)
        headers=mrc.parseHeader(headerbytes)
        return headers

### write a array to a fileobjt at the end.
def writeframe(array,fileobjt):       
        fileobjt.seek(0,2)
        array.tofile(fileobjt)

### read a single frame from the mrc file, start as where in the file to start read, length as the bytes to read,
def readframe(start,length,dataobjt,headerdtype):
	dataobjt.seek(start)
	framearray=np.fromfile(dataobjt,dtype=headerdtype,count=length)
	return framearray

### main 
def main():
	## get filename of input mrc file as datafile 
	datafile=sys.argv[1]
	## get output filename of output mrc file as newfile
	newfile=sys.argv[2]
	## get bad particles
	badlist=sys.argv[3].split(',')

	## parse necessary headers
	headers=readHeaders(datafile)
	box_size=headers['shape'][1]
	bytes_per_pixel=headers['dtype'].itemsize
	framesize=bytes_per_pixel*box_size*box_size
	length=np.prod(headers['shape'][-2:])
	headerdtype=headers['dtype']
	lenz=headers['shape'][0]

	## update headers
	headers['nz']=headers['shape'][0]-len(badlist)
	headers['shape']=tuple([headers['nz'],box_size,box_size])


	## initial start point of the first frame
	start=1024+headers['nsymbt']
	## open file
	dataobj=open(datafile,'rb')
	fileobj=open(newfile,'wb')

	## write header bytes
	headerbytes=mrc.makeHeaderData(headers)
	fileobj.write(headerbytes)

	## write frames
	i=0
	while i<lenz:
		frame=readframe(start,length,dataobj,headerdtype)
		start=start+framesize
		i+=1
		## skip bad ones
		if str(i) in badlist:
			continue
		writeframe(frame,fileobj)
		
if __name__ == '__main__':
	main()	
