#! /usr/bin/env python
import numpy as np
def check(matrix):
    for i in matrix:
        for j in i:
            if j==0:
                return True

    return False

def update(matrix):
    ## check by line by lane by 3x3box

    if nmatrix==matrix:
        nmatrix=guess(matrix)


    matrix=nmatrix


    return matrix

def guess(matrix):
    pass



def getmatrix():
    matrix=[[] for x in range(9)]
    ### judge if raw input or GUI input
    if True:
        for i in range(9):
            itemline=raw_input('input %i line:' %(i+1))
            items=[int(x.strip()) for x in itemline.split(',')]
            for j in range(9):
                matrix[i][j]=items[j]

    return matrix




def main():
    matrix=getmatrix()
    while check(matrix):
        matrix=update(matrix)
        

getmatrix()


                    
