#! /usr/bin/env python
import cupy as cp
import cv2
from cupyx.scipy.ndimage import rotate, shift, zoom
from cupyx.scipy.signal import correlate, correlate2d
import numpy as np
import sys
import time
import copy
import argparse
import mrcfile
#from scipy.ndimage import shift, zoom
from scipy.signal import find_peaks
from matplotlib import pyplot
import math
from starparse import StarFile
from skimage.transform import radon

def rotate_volume( volume,rot=0,tilt=0,psi=0,order=1):
	newvolume = copy.deepcopy(volume)
	if rot != 0:
		newvolume = rotate(newvolume, angle=rot, axes=(1,2), order=order, mode='constant', reshape=False)
	if tilt != 0:
		newvolume = rotate(newvolume, angle=-tilt, axes=(0,2), order=order, mode='constant', reshape=False)
	if psi != 0:
		newvolume = rotate(newvolume, angle=psi, axes=(1,2), order=order, mode='constant', reshape=False)
	return newvolume

def rotate_image( image, psi=0, x=0, y=0, order=1 ):
	if x != 0 or y != 0:
		image = shift ( image, (y,x), mode='wrap' )
	if psi != 0:
		image = rotate ( image, -psi, axes=(0,1), mode='constant', reshape=False, order=order )
	return image

def rotate_image_3dto2d ( image, psi=0, x=0, y=0, order=1 ):
	if psi != 0:
		image = rotate ( image, psi, axes=(0,1), mode='constant', reshape=False, order=order )
	if x!=0 or y!= 0:
		image = shift ( image, (-y,-x), mode='wrap' )
	return image

def project_volume( volume, rot=0, tilt=0, psi=0, x=0, y=0, order=1):
	volume_rotated = rotate_volume ( volume, rot, tilt, 0, order=order)
	projection = cp.sum( volume_rotated, axis=0 )
	projection = rotate_image_3dto2d ( projection, psi, x, y, order)
	return projection


def find_psi_gridsearching ( image_array, model_array, center=180.0, angle_range=10.0, step=5.0, order=1, show=False, index_length=1 ):
	max_correlation = 0
	correlation_maxs = []
	searching_list = None
	center = cp.atleast_1d(cp.array(center))

	for angle in center:
		min_angle = angle - 0.5 * angle_range
		max_angle = angle + 0.5 * angle_range
		new_angles = cp.arange(min_angle, max_angle, step)
		searching_list = cp.append(searching_list, new_angles) if searching_list is not None else new_angles

	for angle in searching_list:
		model_2d_rotated = rotate_image_3dto2d( model_array, psi=angle, x=0, y=0, order=order)
		correlation_array = correlate ( image_array, model_2d_rotated, mode='full', method='fft')
		correlation_maxs.append((angle, cp.max(correlation_array)))
		if cp.max(correlation_array) > max_correlation:
			best_angle = angle
			max_correlation = cp.max(correlation_array)
	if show:
		for angle in correlation_maxs:
			print (angle)
	correlation_maxs = cp.array( correlation_maxs )
	correlation_maxs = correlation_maxs[cp.argsort(correlation_maxs[:,1])]
	return correlation_maxs[-index_length:,0]


### using autocorrelation to find initial psi then run precise grid searching
def find_psi_s1( image_array, model_2d):
	prior_angle = find_initial_psi ( image_array )
	angle_max = find_psi_gridsearching ( image_array, model_2d, center=prior_angle, angle_range=20.0, step=0.5, order=3 )
	return angle_within180( angle_max )


### using iterations of grid searching. step size decreasing sequentially.
def find_psi_s2( image_array, model_2d, show=False):
	angle_it1 = find_psi_gridsearching ( image_array, model_2d, center=90.0, angle_range=180.0, step=10.0, order=1, show=show, index_length=4 )
	angle_it2 = find_psi_gridsearching ( image_array, model_2d, center=angle_it1, angle_range=20.0, step=2.0, order=2, show=show, index_length=1 )
	angle_it3 = find_psi_gridsearching ( image_array, model_2d, center=angle_it2, angle_range=4.0, step=0.5, order=3, show=show )
	return angle_within180( angle_it3 )


### using created radon transform
def find_psi_s3( image_array, model_2d):
	prior_angle = 90 + find_initial_psi_s2( image_array )
	angle_max = find_psi_gridsearching ( image_array, model_2d, center=prior_angle, angle_range=10.0, step=0.5, order=3 )

	return angle_within180( angle_max )

def find_psi_s4( image_array, model_2d):
	prior_angle = find_initial_psi_s3( image_array )
	angle_max = find_psi_gridsearching ( image_array, model_2d, center=prior_angle, angle_range=15.0, step=0.5, order=3 )

	return angle_within180( angle_max )




### radon of the center projection of auto correlation
def find_initial_psi_s3( image_array ):
	correlation_array = correlate ( image_array, image_array, mode='full', method='fft')
	center_x, center_y = correlation_array.shape[1] //2, correlation_array.shape[0] //2
	correlation_array[center_y-1:center_y+1,center_x-1:center_x+1] = 0.0

	#pyplot.imshow(correlation_array.get())
	#pyplot.show()

	angle_step = 5
	theta = np.arange(0., 180., angle_step)
	sums = np.zeros(( len(theta) ))

	width = 4
	length = 200

	for a in range(len(theta)):
		sub_correlation_array = extract_sub_array(correlation_array, length, width, theta[a])
		sums[a] = np.sum( sub_correlation_array )	
	pyplot.close()
	pyplot.plot( sums )
	#pyplot.show()
	angle_index = np.argmax(sums)
	initial_angle = theta[ angle_index ]

	return angle_within180(initial_angle)

### radon of the center projection of fft 
def find_initial_psi_s2( image_array ):
	correlation_array = correlate ( image_array, image_array, mode='full', method='fft')
	center_x, center_y = correlation_array.shape[1] //2, correlation_array.shape[0] //2
	correlation_array[center_y-1:center_y+1,center_x-1:center_x+1] = 0.0

	#image_array_pad = cp.zeros((correlation_array.shape))
	#image_array_pad[ center_y: center_y+480, center_x: center_x+480] = image_array


	a = cp.fft.fft2( correlation_array )
	real = cp.abs( a)
	real_shift = cp.fft.fftshift( real )
	#real_shift = real_shift * real_shift
	center_y, center_x = real_shift.shape[1]//2, real_shift.shape[0]//2
	real_shift[center_y, center_x] = 0.0
	real_shift = real_shift[center_y-120:center_y+120 , center_x-120:center_x+120]
	#real_shift[center_y-5:center_y+5 , center_x-5:center_x+5] = 0.0

	angle_step = 5
	theta = np.arange(0., 180., angle_step)
	sums = np.zeros(( len(theta) ))

	width = 4
	length = 100
	
	for a in range(len(theta)):
		sub_fft_array = extract_sub_array(real_shift, length, width, theta[a])
		sums[a] = np.sum( sub_fft_array )
#		if a == 0 or a == 45:
#			pyplot.imshow(sub_fft_array.get())
#			pyplot.show()
	#pyplot.plot(sums)
	#pyplot.show()
	angle_index = np.argmax(sums)
	initial_angle = theta[ angle_index ]

#	pyplot.imshow(correlation_array.get())
#	pyplot.show()
#	pyplot.imshow(real_shift.get())
#	pyplot.show()
	

	return angle_within180(initial_angle)


def extract_sub_array(image, length, width, angle):
	center_y, center_x = np.array(image.shape) / 2 -0.5
	angle = 90 - angle
	angle_rad = np.deg2rad(angle)
	y,x = cp.indices(image.shape)

	x_shifted = x - center_x
	y_shifted = y - center_y


	width_rotated = x_shifted * cp.cos(angle_rad) + y_shifted * cp.sin(angle_rad)
	length_rotated = -x_shifted * cp.sin(angle_rad) + y_shifted * cp.cos(angle_rad)

	# Define the mask for the sub-array
	mask = (cp.abs(width_rotated) <= width // 2) & (cp.abs(length_rotated) <= length // 2)
	#print (mask.shape)
	# Create an empty sub-array with the same shape as the image
	sub_array = cp.zeros_like(image)

	# Assign the values from the image to the sub-array using the mask
	sub_array[mask] = image[mask]
	#pyplot.imshow(sub_array[center_y-40:center_y+40, center_x-40:center_x+40].get())
	#pyplot.show()
	return sub_array


def radon_strip( image, theta, width):
	assert 0 <= width <= image.shape[0], "Width must be between 0 and the image size"

	num_angles = len(theta)
	center = np.array(image.shape) / 2 -0.5
	diagonal = int(np.ceil(np.sqrt(2) * max(image.shape)))
	half_width = width // 2
	strip_projection = np.zeros((width, num_angles))

	for col in range(width):
		offset = col - half_width
		for a in range(num_angles):
			angle = np.deg2rad(theta[a])
			x = center[1] + offset * np.cos(angle)
			y = center[0] - offset * np.sin(angle)

			if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
				strip_projection[col, a] = image[int(y), int(x)]
	return strip_projection



def find_initial_psi ( image_array ):
	### this is done in cupy
	correlation_array = correlate ( image_array, image_array, mode='full', method='fft')

	### transform cupy.array to numpy.array, opencv take only numpy.array
	correlation_array_numpy = cp.asnumpy( correlation_array )
	center_x, center_y = correlation_array_numpy.shape[1] //2, correlation_array_numpy.shape[0] //2
	correlation_array_numpy[center_y-10:center_y+10,center_x-10:center_x+10] = 0.0
	correlation_array[center_y-10:center_y+10,center_x-10:center_x+10] = 0.0

	a = cp.fft.fft2( correlation_array)
	real = cp.abs( a)
	real_shift = cp.fft.fftshift( real )
	real_shift[center_y-10:center_y+10 , center_x-10:center_x+10] = 0.0
	coordinate = cp.unravel_index( cp.argmax( real_shift ), real_shift.shape)
	real_shift[coordinate[0], coordinate[1]] = 999999999999
	angle = cp.arctan2(coordinate[0]-center_y, coordinate[1]-center_x) * 180 /cp.pi
	angle = -angle-90.0
#	print (angle)
	#log_real = np.log(1+real_shift)
	#pyplot.imshow(log_real[center_y-130:center_y+130, center_x-130:center_x+130].get(), cmap='gray')
	#pyplot.show()

	return angle_within180(angle)


def angle_within180( angle ):
	if angle < 0.0 :
		angle += 360.0
		return angle_within180( angle )
	elif angle > 180.0:
		angle -= 180.0
		return angle_within180( angle )
	else:
		return angle

def angle_within360( angle ):
	if angle < 0.0:
		angle += 360.0
		return angle_within360( angle )
	elif angle > 360.0:
		angle -= 360.0
		return angle_within360( angle )
	else:
		return angle

### strategy 1
def find_initial_psi_1 ():
	center_x, center_y = correlation_array_numpy.shape[1] //2, correlation_array_numpy.shape[0] //2
	correlation_array_numpy[center_y-10:center_y+10,center_x-10:center_x+10] = 0.0
	#pyplot.imshow(correlation_array_numpy)
	#pyplot.show()
	normalized_array = cv2.normalize ( correlation_array_numpy, None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
#	normalized_array[ normalized_array < 100] = 0
	#pyplot.imshow( normalized_array )
	#pyplot.show()
#	gray_image = (normalized_array * 255).astype(np.uint8)
#	gray_image = (correlation_array_numpy).astype(np.uint8)
#	pyplot.imshow(gray_image)
#	pyplot.show()

	edges = cv2.Canny( normalized_array, 100, 100 )
#	pyplot.imshow( edges )
#	pyplot.show()
	lines = cv2.HoughLinesP( edges, 1, np.pi / 180, 2, minLineLength=100, maxLineGap=10)
	#print (lines.shape)
	most_evident_line = max( lines, key=lambda x: np.linalg.norm(x[0][0]-x[0][1]))

	x1,y1,x2,y2 = most_evident_line[0]
	angle = -np.arctan2(y2-y1, x2-x1 ) * 180/np.pi
	print (angle)




### strategy 2
	#start_time = time.time()
	#angles = np.arange(180)
	#sinogram = radon( correlation_array_numpy, theta=angles, circle=False)
	#print (sinogram.shape)
	#pyplot.imshow(sinogram)
	#angle = np.unravel_index( np.argmax( sinogram ), sinogram.shape)[1]
	#print (angle-90.0, 'by radon')
	#end_time = time.time()
	#print (end_time - start_time, 'seconds')
	#pyplot.show()

def find_peak( array_1d, spacing=20):
	array_1d_np = cp.asnumpy(array_1d)
	peaks = find_peaks( array_1d_np )[0]

	sorted_peaks = peaks[np.argsort(array_1d_np[peaks])][::-1]
	highest_peak = sorted_peaks[0]
	second_highest_pesk = None
	
	for peak in sorted_peaks[1:]:
		if abs(peak - highest_peak) >= spacing:
			second_highest_peak = peak
			break
	return highest_peak, second_highest_peak

def test_psi (array):
	return True


def parseOptions():
	parser = argparse.ArgumentParser()

	parser.add_argument('-i','--i',action='store',dest='input_star',
			help=' initial star file with correct psi angles')

	parser.add_argument('-o','--o',action='store',dest='output_star',
			help=' output star file')

	parser.add_argument('-m','--model',action='store',dest='model',
			help=' azimuthal average model as reference')

	parser.add_argument('-d','--diameter',action='store_true',dest='find_diameter', default=False,
			help=' option to classify images based on diameters')

	parser.add_argument('-p','--psi',action='store_true',dest='find_psi', default=False,
			help=' option to find the correct psi angle')

	parser.add_argument('-s','--shift',action='store_true',dest='minimize_shift', default=False,
			help=' option to minimize x, y shift based on correct psi angle')

	results=parser.parse_args()

	#make sure required arguments are present
	if results.input_star == None:
		pass

	return (results)



def main():

	results = parseOptions()

	model_3d = mrcfile.read(results.model)
	model_3d = cp.asarray( model_3d )
	model_2d = project_volume ( volume=model_3d, rot=0, tilt=90, psi=0, order=3 )
	#pyplot.imshow(model_2d)
	#pyplot.show()

	starfile = StarFile( results.input_star )
	particles_df = starfile.particles_df	
	optics_df = starfile.optics_df

	pixel_size = float(optics_df.loc[0,'_rlnImagePixelSize'])


	print ( 'parsing finished, start calculation')

	for line_number in range( particles_df.shape[0] ):
		psi = particles_df.loc[ line_number, '_rlnAnglePsi']
		psi = angle_within180( psi )
		image = particles_df.loc[ line_number, '_rlnImageName'].split('@')
		### I choose to open fileobj every time because imagestack might be different between particles
		with mrcfile.mmap(image[1], mode='r') as imagestack:
			zslice = int(image[0])-1
			image_array = imagestack.data[zslice]
			image_array = cp.asarray(image_array)
		if results.find_psi:
			image_array = image_array[50:430, 50:430]
			angle_max = 0.0
			max_correlation = 0.0

			start_time = time.time()
			angle_max = find_psi_s3( image_array, model_2d )
			#angle_max = find_psi_s2( image_array, model_2d )
			#print (angle_max)
			end_time = time.time()
			print( 'time elapsed:  ', end_time-start_time)

			


			if cp.abs( angle_max - psi ) > 2:
				print ('incosistency found at image: ', zslice + 1)
				print ('current: ', angle_max, '   star: ', psi)
				#pyplot.imshow(image_array.get())
				#angle_max = find_psi_s2( image_array, model_2d, show=True )
				pyplot.show()
			


			#if cp.abs( angle_it3 - angle_max ) > 15.0 :
				#print ('incosistency found at image: ', zslice)
				#print ('fft: ', angle_max, '   gridsc: ', angle_it3)
				#find_psi_gridsearching ( image_array, model_2d, min_angle=prior_angle-10.0, max_angle=prior_angle+10.0, step=0.5, order=3, show=True )
				#pyplot.show()
				#find_psi_gridsearching ( image_array, model_2d, min_angle=angle_it1-20.0, max_angle=angle_it1+20.0, step=1.0, order=2, show=True )
				#pyplot.imshow(image_array.get())
				#pyplot.show()







			starfile.particles_df.at[line_number, '_rlnAnglePsi'] = angle_max

		if results.find_diameter:
			image_array = image_array[50:430, 50:430]
			model_2d_cropped = model_2d
			#model_2d_cropped[:184, :] = 0.0 
			#model_2d_cropped[296:, :] = 0.0
			model_2d_cropped[model_2d_cropped < 0 ] = 0.0
			model_2d_cropped = model_2d_cropped[50:430, 50:430]
			
			#pyplot.imshow(model_2d.get())
			#pyplot.show()
			#model_2d = cp.zeros((480,480))
			#model_2d[225:235,:] = 1.0
			#model_2d[245:255,:] = 1.0
			image_array_rotated = rotate_image( image_array, psi=psi, x=0, y=0, order=3 )
			#print ( image_array_rotated.shape)
			max_correlation = 0
			middle_index = model_2d_cropped.shape[0] // 2



			image_autocorrelation = correlate ( image_array_rotated, image_array_rotated, mode='full', method='fft')
			correlation_middle_index = image_autocorrelation.shape[0] // 2
			image_autocorrelation[ correlation_middle_index-1:correlation_middle_index+1,correlation_middle_index-1:correlation_middle_index+1 ] = 0.0
			model_autocorrelation = correlate ( model_2d_cropped, model_2d_cropped, mode='full', method='fft')
			pyplot.imshow(image_autocorrelation.get())
			pyplot.show()
			pyplot.imshow(model_autocorrelation.get())
			pyplot.show()
			#correlation_array = correlate( image_autocorrelation, model_autocorrelation, mode='full', method='fft')
			#pyplot.imshow(correlation_array.get())
			#pyplot.show()


			middle_index = model_2d_cropped.shape[0] // 2
			insert = 0
			max_insert = 0
			first_half = model_2d_cropped[:middle_index]
			second_half = model_2d_cropped[middle_index:]
			while insert <= 100:
				zeros = cp.zeros((insert, model_2d_cropped.shape[1]))
				inserted_array = cp.concatenate((first_half, zeros, second_half), axis=0)
				model_2d_inserted = inserted_array[insert * 0.5 : model_2d_cropped.shape[0] + insert * 0.5, :]
				#print (model_2d_inserted.shape)
				#print ('current insertion: ', insert)
				#pyplot.imshow(model_2d_inserted.get())
				#pyplot.show()
				model_2d_autocorrelation = correlate ( model_2d_inserted, model_2d_inserted, mode='full', method='fft')
				correlation_array = correlate ( image_autocorrelation, model_2d_autocorrelation, mode='full', method='fft')
				if cp.max(correlation_array) > max_correlation:
					max_correlation = cp.max(correlation_array)
					max_array = correlation_array
					max_model = model_2d_inserted
					max_insert = insert
				insert += 4
				#print ('max value: ', cp.max(correlation_array))
				#pyplot.imshow(correlation_array.get())
				#pyplot.show()
			print ('max insert: ', max_insert)
			f,(img_1,img_2,img_3) = pyplot.subplots(1,3)
			img_1.imshow( image_array_rotated.get())
			img_2.imshow( max_model.get())
			img_3.imshow( max_array.get())
			pyplot.show()
			#pyplot.imshow(max_array.get())
			#pyplot.show()


		if results.minimize_shift:
			image_array_rotated = rotate_image( image_array, psi=psi, x=10, y=-10, order=3)
			image_projection = cp.sum(image_array_rotated, axis=1)
			peak_one, peak_two = find_peak( image_projection )
			
#			image_array[240,240]=9
#			pyplot.imshow(image_array.get())
#			pyplot.show()

			distance = (peak_one + peak_two)/2 - image_array_rotated.shape[1]//2 + 0.5
			#print ('peaks: ', peak_one, peak_two)
			#print ('distance: ' ,distance)
			x = -distance * math.sin( psi/180.0*math.pi )
			y = -distance * math.cos( psi/180.0*math.pi )

			print('x,y: ', x, y)


			image_array_rotated = rotate_image( image_array, psi=psi, x=x, y=y, order=3)
			image_projection = cp.sum(image_array_rotated, axis=1)
			peak_one, peak_two = find_peak( image_projection )
			distance = abs( (peak_one + peak_two)/2 - image_array_rotated.shape[1]//2 + 0.5)
			#print ('peaks after: ', peak_one, peak_two)
			#print ('distance after: ', distance)


			if  distance >1.5:
				print ('distance after: ', distance)
				image_array[240:240] = 9
				pyplot.imshow(image_array_rotated.get())
				pyplot.show()





#			model_array_rotated = rotate_image( model_2d, psi=-psi, x=0, y=0, order=3 )
#			correlation_array = correlate ( image_array, model_array_rotated, mode='full', method='fft')
#			distance = cp.unravel_index( cp.argmax(correlation_array), correlation_array.shape)[0]-0.5*correlation_array.shape[0]+0.5
#			#print ( 'raw distance: ', distance )
#			#pyplot.imshow(correlation_array)
#			#pyplot.show()
#			x = -distance * math.sin( psi/180.0*math.pi )
#			y = -distance * math.cos( psi/180.0*math.pi )
#			#pyplot.imshow(correlation_array.get())
#			#pyplot.show()

#			### test x,y shift found
#			image_array_rotated_shifted = rotate_image( image_array, psi=psi, x=x, y=y, order=3 )
#			correlation_array = correlate ( image_array_rotated_shifted, model_2d, mode='full', method='fft')
#			distance = cp.unravel_index( cp.argmax(correlation_array), correlation_array.shape)[0]-0.5*correlation_array.shape[0]+0.5
#			#print ( 'after shift: ', distance )
#			if distance > 1 :
#				continue
#				print ('image %i is still not at zero' %line_number)
#				print ('center detected: ', x,y, 'distance: ', distance)
#				pyplot.imshow(correlation_array.get())
#				pyplot.show()
#			#print (line_number)

			particles_df.at[line_number, '_rlnOriginXAngst'] = x * pixel_size
			particles_df.at[line_number, '_rlnOriginYAngst'] = y * pixel_size
		
	starfile.particles_df = particles_df
	starfile.write( results.output_star)


if __name__ == '__main__':
	main()
