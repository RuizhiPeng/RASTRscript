#! /usr/bin/env python3


#### this script is for transforming relion3 star file format to relion2 star file format. old cistem or relion cannot take relion3 star format

import sys




###return a dictionary containing optics data
### return a list of lines with particle data, eg angles, defocus, etc
def get_star3_data(name):
    fileobj=open(name,'r')
    lines=fileobj.readlines()
    fileobj.close()

    optics={}
    particles=[]
    optic_line=None
    particles_line=None

    for i in range(len(lines)):
        if lines[i][:11]=='data_optics':
            print ('getting optics data')
            optic_line=True
            continue
        elif lines[i][:14]=='data_particles':
            print ('getting particles data')
            particles_line=True
            continue
        if lines[i][:4]=='_rln':
            if optic_line:
                print ('getting optic columns')
                optics[lines[i].split()[0][4:]]=0
                continue
            elif particles_line:
                print ('getting particles columns')
                particles.append(lines[i])
                continue

        elif optic_line and len(lines[i].split())>2:
            words=lines[i].split()
            j=0
            for key in optics:
                optics[key]=words[j]
                j+=1
            optic_line=False
            continue
        elif not optic_line and particles_line and len(lines[i].split())>2:
            particles.append(lines[i])
#    print (optics)
#    print (particles)
    return optics,particles

### write relion2 star file
def write_star2(name,optics,particles):
    fileobj=open(name,'w')

    column_count=0
    for line in particles:
        if len(line.split())==2:
            column_count+=1
    for key in optics:
        if key=='Voltage' or key=='SphericalAberration' or key=='AmplitudeContrast':
            particles.insert(column_count,'_rln'+key+' #%i' %(column_count+1)+'\n')
            column_count+=1
        elif key=='ImagePixelSize':
            particles.insert(column_count,'_rlnMagnification'+' #%i' %(column_count+1)+'\n')
            particles.insert(column_count+1,'_rlnDetectorPixelSize'+' #%i' %(column_count+2)+'\n')

    newlines=[]
    for line in particles:
        if len(line.split())==2:
            newlines.append(line)
        if len(line.split())>2:
            words=line.split()
            for key in optics:
                if key=='Voltage' or key=='SphericalAberration' or key=='AmplitudeContrast':
                    words.append(optics[key])
                elif key=='ImagePixelSize':
                    words.append('10000.0')
                    words.append(optics[key])
            newline=' '.join(words)+'\n'
            newlines.append(newline)
    newlines.insert(0,'data_images\n')
    newlines.insert(1,'loop_\n')
    fileobj.writelines(newlines)
    fileobj.close()






def main():
    star3=sys.argv[1]
    star2=sys.argv[2]

    optics,particles=get_star3_data(star3)
    write_star2(star2,optics,particles)



if __name__ =='__main__':
    main()

