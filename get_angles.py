#! /usr/bin/env python3
### usage ./get_angles.py  a  b
### get angle from a to b
import sys

def main():
    a=sys.argv[1]
    b=sys.argv[2]
    fileobj=open(a,'r')
    lines=fileobj.readlines()
    fileobj.close()
    
    angle_list=[]
    for line in lines[1:]:
        words=line.split()
        if words[0]!='C':
            angle_list.append(words[1])


    fileobj=open(b,'r')
    lines=fileobj.readlines()
    fileobj.close()

    newlines=[]
    j=0
    for i in range(len(lines)):
        words=lines[i].split()
        if words[0]!='C':
            words[1]=str(float(angle_list[j])*-1)
            j+=1
            words[0]=int(words[0])
            words[7]=int(words[7])
            for i in range(len(words)):
                if type(words[i])!='int':
                    words[i]=float(words[i])
            newline='%7d %7.2f %7.2f %7.2f   %7.2f   %7.2f %7d %5d %8.1f %8.1f %7.2f %7.2f %7.2f %10d %10.4f %7.2f %7.2f\n' %(words[0],words[1],words[2],words[3],words[4],words[5],words[6],words[7],words[8],words[9],words[10],words[11],words[12],words[13],words[14],words[15],words[16])
        else:
            newline=lines[i]
        newlines.append(newline)

    fileobj=open(b[:-4]+'_updated.par','w')
    fileobj.writelines(newlines)
    fileobj.close()


if __name__ =='__main__':
    main()
