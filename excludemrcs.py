#! /usr/bin/env python
from pyami import mrc
import sys
import numpy as np
badlist=[249, 418, 695, 729, 950, 1067, 1207, 1331, 1350, 1351, 1352, 1354, 1355, 1358, 1362, 1363, 1749, 2022, 2029, 2212, 3377, 3393, 3394, 3401, 3402, 3403, 3412, 3598, 3943, 4334, 4405, 4424, 4624, 4727, 4756, 4759, 4760, 4863, 5705, 6076, 6077, 6078, 6079, 6080, 6230, 6284, 6302, 6309, 6873, 6982, 7042, 7346, 7355, 7370, 7399, 7524, 7529, 7531, 7535, 7537, 7544, 7866, 7911, 7946, 7949, 8008, 8236, 8417, 8433, 8514, 8515, 8517, 8518, 8520, 8522, 8642, 8668, 8827, 8869, 8874, 8876, 8883, 8963, 9080, 9329, 9339, 9387, 9556, 9799, 9805, 9806, 9807, 9809, 9810, 9813, 9814, 9998, 10136, 10442, 10865, 11048, 11312, 11313, 11314, 11315, 11318, 11569, 11600, 11869, 12223, 12428, 12818, 13073, 13089, 13555, 13656, 13864, 13896, 14459, 14476, 14527, 14569, 14570, 14691, 14800, 14805, 14806, 14807, 14924, 14953, 14969, 14982, 14994, 15001, 15169, 15346, 15442, 15447, 15448, 15449, 15450, 15452, 15453, 15454, 15455, 15456, 15458, 15459, 15461, 15462, 15548, 15549, 15552, 15554, 15561, 15567, 15568, 15569, 15932, 15941, 15954, 16095, 16132, 16137, 16232, 16498, 16593, 16662, 16671, 16690, 16692, 16797, 16805, 16806, 16884, 16898, 17103, 17182, 17390, 17579, 17587, 18060, 18087, 18088, 18089, 18091, 18099, 18513, 18540, 18544, 18549, 18550, 18720, 18729, 19032, 19525, 19572, 19772, 19810, 19823, 19885, 19919, 20073, 20507, 20701, 20706, 20778, 20890, 20928, 21172, 21385, 21386, 21388, 21390, 21392, 21394, 21395, 21458, 21490, 21552, 21664, 21727, 21986, 21989, 21992, 22167, 22493, 22497, 22498, 22519, 22521, 22524, 22525, 22652, 23201, 23202, 23368, 23472, 23475, 23548, 23552, 23578, 23846, 23853, 23864, 23865, 23866, 23868, 23869, 24568, 24787, 24871, 24903, 24911, 24945, 24984, 25097, 25098, 25104, 25109]

def readHeaders(particlestacks):
        f=open(particlestacks,'rb')
        headerbytes=f.read(1024)
        headers=mrc.parseHeader(headerbytes)
        return headers

def writeframe(array,fileobjt):       
        fileobjt.seek(0,2)
        array.tofile(fileobjt)

def readframe(start,length,dataobjt,headerdtype):
	dataobjt.seek(start)
	framearray=np.fromfile(dataobjt,dtype=headerdtype,count=length)
	return framearray
def main():
	datafile=sys.argv[1]
	newfile=sys.argv[2]
	
	headers=readHeaders(datafile)
	box_size=headers['shape'][1]
	bytes_per_pixel=headers['dtype'].itemsize
	framesize=bytes_per_pixel*box_size*box_size
	length=np.prod(headers['shape'][-2:])
	headerdtype=headers['dtype']


	start=1024+headers['nsymbt']

	dataobj=open(datafile,'rb')
	fileobj=open(newfile,'wb')
	fileobj.write(''.join(headers))
	i=0
	while i<25476:
		frame=readframe(start,length,dataobj,headerdtype)
		start=start+framesize
		i+=1
		if i in badlist:
			continue
		writeframe(frame,fileobj)
		
if __name__ == '__main__':
	main()	
