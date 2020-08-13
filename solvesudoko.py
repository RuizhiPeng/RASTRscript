#! /usr/bin/env python3
import numpy as np
import copy

### check if there is unsettled number
def unsolved(matrix):
  for i in matrix:
    for j in i:
      if type(j)==list:
        return True
  return False

### delete decided integer from undecided lists, row and lane
def delexist(matrix):
	for i in range(9):
		for j in range(9):
			if type(matrix[i][j])==list:
				for z in range(9):
					if type(matrix[i][z])==int and (matrix[i][z] in matrix[i][j]):
						matrix[i][j].remove(matrix[i][z])
				for z in range(9):
					if type(matrix[z][j])==int and (matrix[z][j] in matrix[i][j]):
						matrix[i][j].remove(matrix[z][j])
			elif type(matrix[i][j])==int:
				continue
	return matrix
### delte decided integer from undecided lists, within a 3x3 box
def delbox(matrix):
	for i in range(9):
		for j in range(9):
			if type(matrix[i][j])==list:
				x=int(i/3)*3
				y=int(j/3)*3
				for z in range(3):
					for k in range(3):
						if type(matrix[x+z][y+k])==int and (matrix[x+z][y+k] in matrix[i][j]):
							matrix[i][j].remove(matrix[x+z][y+k])
	return matrix

### change list that has only one element left to integer
def listtoint(matrix):
  for i in range(9):
    for j in range(9):
      if type(matrix[i][j])==list and len(matrix[i][j])==1:
        matrix[i][j]=matrix[i][j][0]
  return matrix

### medium to hard problem logic
### if an element only exist in one list in the row, lane and box. then this element must be the value of that position
def unique(matrix):
  nmatrix=copy.deepcopy(matrix)
  for i in range(9):
    for j in range(9):
      if type(matrix[i][j])==list:
        for item in matrix[i][j]:
          ### initial exist=False
          exist=False
          ### this loop is for detecting if an element exist only in this list in the row
          for z in range(9):
            if type(matrix[i][z])==list and (item in matrix[i][z]) and z!=j:
              exist=True
          if not exist:
            nmatrix[i][j]=[item]
            #print (1)
            continue
          exist=False
          ### this loop is for detecting if an element exist only in this list in the lane
          for z in range(9):    
            if type(matrix[z][j])==list and (item in matrix[z][j]) and z!=i:
              exist=True
          if not exist:
            nmatrix[i][j]=[item]
            #print (2)
            continue
          exist=False
          x=int(i/3)*3
          y=int(j/3)*3
          ### this loop is for detecting if an element exist only in this list in the 3x3 box
          for k in range(3):
            for m in range(3):
              if type(matrix[x+k][y+m])==list and (item in matrix[x+k][y+m]):
                if (x+k)!=i or (y+m)!=j:
                  exist=True
          if not exist:
            nmatrix[i][j]=[item]
            #print(3)
            continue
  return nmatrix

### packed logic for upgrading matrix
def update(matrix):
    ### check by line by lane by 3x3box
    nmatrix=listtoint(matrix)
    nmatrix=delexist(nmatrix)
    nmatrix=delbox(nmatrix)
    ### check by if the element is unique in the row, lane, box
    nmatrix=unique(nmatrix)
    if nmatrix==matrix:
        nmatrix=guess(nmatrix)
    return nmatrix

### when medium to hard logic cannot solve the problem, we have to guess a position. Not finished
def guess(matrix):
    return matrix


### show 9x9 matrix with good format.(currently print mode, GUI mode unfinished)
def showmatrix(matrix):
	m=copy.deepcopy(matrix)
	for i in range(9):
		for j in range(9):
			if type(m[i][j])==list:
				m[i][j]=' '
	print ('|-----------------------|')
	for i in range(9):
		print ('|',m[i][0],m[i][1],m[i][2],'|',m[i][3],m[i][4],m[i][5],'|',m[i][6],m[i][7],m[i][8],'|')
		if i%3 ==2:
			print ('|-----------------------|')


### input matrix and store in 2D lists, currently have interactive mode and file mode, elements separated by ' ,'. unkown position input as zero
def getmatrix():
	matrix=[[0,0,0,0,0,0,0,0,0] for x in range(9)]
    ### judge if raw input or GUI input
	if False:
		for i in range(9):
			itemline=input('input %i line:' %(i+1))
			items=[int(x.strip()) for x in itemline.split(',')]
			for j in range(9):
				if items[j]!=0:
					matrix[i][j]=items[j]
				elif items[j]==0:
					matrix[i][j]=[1,2,3,4,5,6,7,8,9]
	if True:
		a=open('sudokuproblem.txt','r')
		lines=a.readlines()
		a.close()
		for i in range(9):
			words=lines[i].split(',')
			for j in range(9):
				matrix[i][j]=int(words[j])
				if matrix[i][j]==0:
					matrix[i][j]=[1,2,3,4,5,6,7,8,9]
	return matrix	




def main():
	matrix=getmatrix()
	state='c'
#	print (unsolved(matrix))
	while unsolved(matrix):
		matrix=update(matrix)
		showmatrix(matrix)
		state=input('quit?(q or c):')
		if state=='q':
			break
		else:
			continue
        


main()
                    
