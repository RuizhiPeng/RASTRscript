#! /usr/bin/env python

### for modifying output my_subtracted_frames_params.star file to usable par file.
### the algorithm output file is incorrect, defocus column position wrong, psi angle axis wrong.
### usage ./azimuthal_average_after.py my_subtracted_frames_params.star  originalmetafile

import sys
from numpy import isclose
import random
input_file=open(sys.argv[1],'r')
lines=input_file.readlines()
input_file.close()


meta_suffix=sys.argv[2].split('.')[-1]

psi_list=[]
df1_list=[]
df2_list=[]

### get psi values
### df1 values are captured for future validation.
for line in lines:
	words=line.split()
	if len(words)<=2 or words[0][0]=='#':
		continue
	if len(words)>3:

		psi_list.append(-1*float(words[1]))
		df1_list.append(float(words[7]))
		df2_list.append(float(words[8]))

psi_list=psi_list[:int(len(psi_list)/4)]
df1_list=df1_list[:int(len(df1_list)/4)]
df2_list=df2_list[:int(len(df2_list)/4)]

metafile=open(sys.argv[2],'r')
metalines=metafile.readlines()
metafile.close()
newlines=[]

if meta_suffix=='par':
	j=0
	for line in metalines:
		words=line.split()
		if words[0]=='C':
			j+=1
	### metalines has the top one additional line
	if len(psi_list)+j!=len(metalines):
		print ('Meta lines not consistent! exciting........')
		sys.exit()
	for i in range(len(metalines)):
		words=metalines[i].split()
		if words[0]=='C':
			newlines.append(metalines[i])
			continue
		if float(words[8])!=df1_list[i-1] or float(words[9])!=df2_list[i-1]:
			print ('defocus not matching, exiting.........')
			sys.exit()
		words[1]=psi_list[i-1]
		for j in range(len(words)):
			words[j]=float(words[j])
		words[0]=int(words[0])
		words[6]=int(words[6])
		words[7]=int(words[7])
		words[13]=int(words[13])

		newline='%7d %7.2f %7.2f %7.2f   %7.2f   %7.2f %7d %5d %8.1f %8.1f %7.2f %7.2f %7.2f %9d %10.4f %7.2f %7.2f\n' %(words[0],words[1],words[2],words[3],words[4],words[5],words[6],words[7],words[8],words[9],words[10],words[11],words[12],words[13],words[14],words[15],words[16])
		newlines.append(newline)

	output_file=open('azimuthal_average_output.par','w')
	output_file.writelines(newlines)
	output_file.close()

if meta_suffix=='star':
	i=0
	### columnnumber is the particle data line columns, not optic line columns
	column_numbers=0
	theta_column=0
	phi_column=0
	for line in metalines:
		words=line.split()
		if len(words)<=2 or words[0][0]=='#':
			if len(words)==2:
				if words[0][:4]=='_rln':
					if column_numbers<int(words[1][1:]):
						column_numbers=int(words[1][1:])
				if words[0]=='_rlnAnglePsi':
					psi_column=int(words[1][1:])
				if words[0]=='_rlnAngleTilt':
					theta_column=int(words[1][1:])
				if words[0]=='_rlnAngleRot':
					phi_column=int(words[1][1:])
				if words[0]=='_rlnDefocusU':
					defocusu_column=int(words[1][1:])

	for line in metalines:
		words=line.split()
		if len(words)==column_numbers:
			i+=1


	if i!=len(psi_list):
		print ('Meta lines not consistent! exciting........')
		sys.exit()
	if theta_column==0 and phi_column==0:
		theta_column=column_numbers+1
		phi_column=column_numbers+2
	elif theta_column==0 and phi_column!=0:
		theta_column=column_numbers+1
	elif phi_column==0 and theta_column!=0:
		phi_column=column_numbers+1

	i=0
	for line in metalines:
		words=line.split()
		if len(words)<column_numbers or words[0][0]=='#':
			newlines.append(line)
			continue
	if theta_column>column_numbers:
		newlines.append('_rlnAngleTilt #'+str(theta_column)+'\n')
	if phi_column>column_numbers:
		newlines.append('_rlnAngleRot #'+str(phi_column)+'\n')
	for line in metalines:
		words=line.split()
		if len(words)==column_numbers:
			if not isclose(float(words[defocusu_column-1]),df1_list[i],rtol=1e-01) and not isclose(float(words[defocusu_column-1]),df2_list[i],rtol=1e-01):
				print (words[defocusu_column-1], df1_list[i], df2_list[i])
				print ('defocus not matching, exiting.........')
				sys.exit()
			words[psi_column-1]=str(psi_list[i])
			i+=1
			if theta_column>column_numbers:
				words.append(str(90.0))
			else:
				words[theta_column-1]='90.0'
			if phi_column>column_numbers:
				words.append(str(float(random.randint(0,360))))
			else:
				words[phi_column-1]=str(float(random.randint(0,360)))


			newline=' '.join(words)+'\n'
			newlines.append(newline)

	outputfile=open('azimuthal_average_output.star','w')
	outputfile.writelines(newlines)
	outputfile.close()




		

