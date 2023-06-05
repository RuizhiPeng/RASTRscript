#! /usr/bin/env python

import tkinter as tk
import tkinter.scrolledtext as st
from tkinter import ttk
import cupy as cp
from cupyx.scipy.ndimage import rotate, shift, zoom, gaussian_filter
from cupyx.scipy.signal import correlate, correlate2d
import numpy as np
import time
import copy
import argparse
import mrcfile
from scipy.signal import find_peaks
from matplotlib import pyplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
from starparse import StarFile
import pandas as pd

### rotate with three angles, 
def rotate_volume( volume,rot=0,tilt=0,psi=0,order=1):
	newvolume = copy.deepcopy(volume)
	if rot != 0:
		newvolume = rotate(newvolume, angle=rot, axes=(1,2), order=order, mode='constant', reshape=False)
	if tilt != 0:
		newvolume = rotate(newvolume, angle=-tilt, axes=(0,2), order=order, mode='constant', reshape=False)
	if psi != 0:
		newvolume = rotate(newvolume, angle=psi, axes=(1,2), order=order, mode='constant', reshape=False)
	return newvolume

### for rotating raw particle images
def rotate_image( image, psi=0, x=0, y=0, order=1 ):
	if x != 0 or y != 0:
		image = shift ( image, (y,x), mode='wrap' )
	if psi != 0:
		image = rotate ( image, -psi, axes=(0,1), mode='constant', reshape=False, order=order )
	return image

### for rotating volume projections
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


### index_length refers how many angles to return. The angles will be ranked based on correlation score.
def find_psi_gridsearching ( image_array, model_array, center=180.0, angle_range=180.0, step=5.0, order=1, index_length=1 ):
	max_correlation = 0
	correlation_maxs = []
	searching_list = None
	center = cp.atleast_1d(cp.array(center))

	### center can be a list of angles
	### use loop to get multiple ranges combined
	for angle in center:
		min_angle = angle - 0.5 * angle_range
		max_angle = angle + 0.5 * angle_range
		new_angles = cp.arange(min_angle, max_angle, step)
		searching_list = cp.append(searching_list, new_angles) if searching_list is not None else new_angles

	### find the angle with highest correlation 
	for angle in searching_list:
		model_2d_rotated = rotate_image_3dto2d( model_array, psi=angle, x=0, y=0, order=order)
		correlation_array = correlate ( image_array, model_2d_rotated, mode='full', method='fft')
		correlation_maxs.append((angle, cp.max(correlation_array)))
		if cp.max(correlation_array) > max_correlation:
			best_angle = angle
			max_correlation = cp.max(correlation_array)
	correlation_maxs = cp.array( correlation_maxs )
	correlation_maxs = correlation_maxs[cp.argsort(correlation_maxs[:,1])]
	return correlation_maxs[-index_length:,0]

def find_psi( starfile, model_2d=None, mode='full' ):
	optics_df = starfile.optics_df
	particles_df = starfile.particles_df
	if mode == 'full':
		angle_maxs = []
		for line_number, particle in particles_df.iterrows():

			image = particle['_rlnImageName'].split('@')
			image_array = readslice(image)

			box_size = image_array.shape[0]
			edge = 50

			### clip image to avoid bad pixels on edges of micrograph
			image_array = image_array[edge:box_size-edge, edge:box_size-edge]

			angle_max = find_initial_psi_s1( image_array )
			angle_max = find_initial_psi_s1( image_array, center=angle_max-90, angle_range=10, angle_step=0.5)
			angle_maxs.append(angle_max.get())

		particles_df['_rlnAnglePsi'] = angle_maxs
		shifts = [ minimize_shift( particles_df.iloc[line_number]) for line_number in range(starfile.particles_df.shape[0])]
		xshifts, yshifts = zip(*shifts)
		particles_df['_rlnOriginXAngst'] = xshifts
		particles_df['_rlnOriginYAngst'] = yshifts
		model_2d = get_average( optics_df, particles_df )

		for line_number, particle in particles_df.iterrows():
			image = particle['_rlnImageName'].split('@')
			image_array = readslice(image)
			box_size = image_array.shape[0]
			edge = 50
			image_array = image_array[edge:box_size-edge, edge:box_size-edge]
			angle_maxs[line_number] = find_psi_gridsearching ( image_array, model_2d, center=angle_maxs[line_number], angle_range=4.0, step=0.1, order=3 ).get()

	if mode == 'fast':
		angle_maxs = []
		for line_number, particle in particles_df.iterrows():
			image = particle['_rlnImageName'].split('@')
			image_array = readslice(image)
			box_size = image_array.shape[0]
			edge = 50
			image_array = image_array[edge:box_size-edge, edge:box_size-edge]
			angle_max = find_initial_psi_s1( image_array )
			angle_max = find_initial_psi_s1( image_array, center=angle_max-90, angle_range=10, angle_step=0.5)
			angle_max = find_psi_gridsearching ( image_array, model_2d, center=angle_max, angle_range=4.0, step=0.1, order=3 )
			angle_maxs.append(angle_max.get())



	return angle_maxs


	


### using fft of autocorrelation
def find_psi_s1( image_array, model_2d):
	### initial s1 use fft, so the angle is 90 degree offset.
	prior_angle = find_initial_psi_s1( image_array )
	angle_max = find_initial_psi_s1( image_array, center=prior_angle-90, angle_range=10, angle_step=0.5)
	angle_max = find_psi_gridsearching ( image_array, model_2d, center=prior_angle, angle_range=4.0, step=0.1, order=3 )

	return angle_within180( angle_max )


### using autocorrelation
def find_psi_s2( image_array, model_2d):
	prior_angle = find_initial_psi_s2( image_array )
	if model_2d is None:
		angle_max = find_initial_psi_s2( image_array, center=prior_angle, angle_range=10, angle_step=0.1)
	if model_2d is not None:
		angle_max = find_initial_psi_s2( image_array, center=prior_angle, angle_range=10, angle_step=0.5)
		angle_max = find_psi_gridsearching ( image_array, model_2d, center=prior_angle, angle_range=4.0, step=0.1, order=3 )

	return angle_within180( angle_max )




### radon of the center projection of auto correlation
def find_initial_psi_s2( image_array, center=90.0, angle_range=180.0, angle_step=5 ):

	correlation_array = correlate ( image_array, image_array, mode='full', method='fft')

	### auto correlation center peak always too high, removing to increase contrast
	center_x, center_y = correlation_array.shape[1] //2, correlation_array.shape[0] //2
	correlation_array[center_y-1:center_y+1,center_x-1:center_x+1] = 0.0

	### get a list of angles to test
	angle_step = angle_step
	angle_min = center - 0.5 * angle_range
	angle_max = center + 0.5 * angle_range
	thetas = np.arange(angle_min, angle_max, angle_step)

	### defining center box size, the size is important for accuracy.
	width = 4
	length = 200

	initial_angle = customized_radon( correlation_array, thetas, length, width)

	return angle_within180(initial_angle)


### radon of the center projection of fft 
def find_initial_psi_s1( image_array, center=90.0, angle_range=180, angle_step=5 ):

	correlation_array = correlate ( image_array, image_array, mode='full', method='fft')
	center_x, center_y = correlation_array.shape[1] //2, correlation_array.shape[0] //2
	correlation_array[center_y-1:center_y+1,center_x-1:center_x+1] = 0.0

	### the fft of auto correlation == square of fft of raw image. The speed to get the same final fft is similar.
	fft = cp.fft.fft2( correlation_array )
	fft_real = cp.abs( fft )
	real_shift = cp.fft.fftshift( fft_real )

	### clip only the center part.
	center_x, center_y = real_shift.shape[1]//2, real_shift.shape[0]//2
	### somehow making center constant fft pixel zero can make it faster
	real_shift[center_y, center_x] = 0.0
	real_shift = real_shift[center_y-120:center_y+120 , center_x-120:center_x+120]

	### get a list of angles to test
	angle_step = angle_step
	angle_min = center - 0.5 * angle_range
	angle_max = center + 0.5 * angle_range
	thetas = cp.arange(angle_min, angle_max, angle_step)

	width = 4
	length = 100
	
	initial_angle = customized_radon( real_shift, thetas, length, width)

	return angle_within180(initial_angle) + 90.0


### definition: theta is zero when parralel to x axis.

def customized_radon( image, thetas, length=100, width=4):
	thetas = cp.array( thetas )
	sums = cp.array([cp.sum(extract_sub_array(image, length, width, theta)) for theta in thetas])

	return thetas[cp.argmax(sums)]

### use boolen mask to extract a sub array
def extract_sub_array(image, length, width, angle):
	center_y, center_x = np.array(image.shape) / 2 
	angle_rad = np.deg2rad(angle)
	y,x = cp.indices(image.shape)

	x_shifted = x - center_x
	y_shifted = y - center_y

	# width define the distance of pixel away from box axis
	width_rotated = x_shifted * cp.sin(angle_rad) + y_shifted * cp.cos(angle_rad)
	# length define the distance of the projection of pixel on axis to center of box, 
	length_rotated = -x_shifted * cp.cos(angle_rad) + y_shifted * cp.sin(angle_rad)

	# Define the mask for the sub-array by creating boolen array
	mask = (cp.abs(width_rotated) <= width // 2) & (cp.abs(length_rotated) <= length // 2)

	# Create an empty sub-array with the same shape as the image
	sub_array = cp.zeros_like(image)

	# Assign the values from the image to the sub-array using the mask
	sub_array[mask] = image[mask]

	return sub_array


### psi 40 is the same as theta 220 for this script's purpose, so we bring them all to 0-180
def angle_within180( angle ):
	return (angle + 360.0) % 180



def angle_within360( angle ):
	if angle < 0.0:
		angle += 360.0
		return angle_within360( angle )
	elif angle > 360.0:
		angle -= 360.0
		return angle_within360( angle )
	else:
		return angle


### Find the highest two peaks. min_gap defines the minimum distance of this two peaks
def find_peak( array_1d, min_gap=80):

	array_1d_np = cp.asnumpy(array_1d)
	peaks = find_peaks( array_1d_np )[0]

	sorted_peaks = peaks[np.argsort(array_1d_np[peaks])][::-1]
	highest_peak = sorted_peaks[0]
	second_highest_pesk = None
	
	for peak in sorted_peaks[1:]:
		if abs(peak - highest_peak) >= min_gap:
			second_highest_peak = peak
			break
	sorted_indices = sorted([highest_peak, second_highest_peak])
	return sorted_indices[0], sorted_indices[1]



### based on a list of diameters, plot histogram
def plot_diameter_histogram(diameter_file):
	diameters = []
	with open(diameter_file, 'r') as fileobj:
		lines = fileobj.readlines()
		for line in lines:
			diameters.append( float(line))
	diameters = np.array(diameters)

	pyplot.hist(diameters, bins=200)
	pyplot.xlabel('diameter(A)')
	pyplot.ylabel('number of particles')
	pyplot.show()



### Input image should be a two element list with slice number first, image file name second.
def readslice( image ):
	with mrcfile.mmap(image[1], mode='r') as imagestack:
		zslice = int(image[0])-1
		image_array = imagestack.data[zslice]
		image_array = cp.asarray(image_array)
	return image_array



def find_diameter( particles_df, sigma, min_gap):
	
	diameters={'_rlnDiameterByRASTR':[]}

	for line_number in range(particles_df.shape[0]):
		psi = angle_within180( particles_df.loc[ line_number, '_rlnAnglePsi'] )
		image = particles_df.loc[ line_number, '_rlnImageName'].split('@')
		image_array = readslice( image )
		image_array_lowpass = gaussian_filter(image_array , sigma)
		image_array_rotated = rotate_image( image_array_lowpass, psi=psi)
		image_1d = cp.sum(image_array_rotated, axis=1)
		peak_one, peak_two = find_peak(image_1d.get(), min_gap=min_gap)

		diameter = abs((peak_one - peak_two) * pixel_size)
		### bug exist for the following
		diameters['_rlnDiameterByRASTR'].append(diameter)
	return diameters


### GUI window to manually find the optimal parameters
### sigma and minimum gap
class optimize_diameter_parameter:
	def __init__(self, particles_df ):
		self.particles_df = particles_df

	def update_parameter(self):
		try:
			self.zslice = int(self.entry_slice.get())
		except: self.zslice = 1

		self.angle_str.set(str(self.particles_df.loc[ self.zslice-1, '_rlnAnglePsi']))
		try:
			self.angle = float(self.entry_angle.get())
		except: 
			self.angle = self.particles_df.loc[ self.zslice-1, '_rlnAnglePsi']
		try:
			self.sigma = int(self.entry_sigma.get())
		except: self.sigma = 0
		try:
			self.min_gap = float(self.entry_min_gap.get())
		except: self.min_gap = 0.0

	def create_entry(self, parent, default_text=None):
		default_text = default_text or tk.StringVar()
		entry = ttk.Entry(parent, width=10, textvariable=default_text)
		entry.pack(side=tk.LEFT)
		entry.bind('<Return>', lambda event: self.update_plot())
		entry.bind('<KP_Enter>', lambda event: self.update_plot())
		return entry

	def update_plot(self):
		self.update_parameter()
		zslice = self.zslice
		angle = self.angle
		sigma = self.sigma
		min_gap = self.min_gap

		image = self.particles_df.loc[ zslice-1, '_rlnImageName'].split('@')
		image_array = readslice( image )
		image_array = rotate_image( image_array, psi=angle)
		image_array = gaussian_filter( image_array, sigma)
		image_array_vertical = rotate_image(image_array, psi=-90)
		image_1d = cp.sum( image_array, axis=1)
		peak_one, peak_two = find_peak(image_1d.get(), min_gap=min_gap)

		self.ax1.clear()
		self.ax1.imshow(image_array_vertical.get(), origin='lower', cmap='gray')
		self.ax2.clear()
		self.ax2.plot(image_1d.get())
		self.ax2.set_xlim(0,image_1d.shape[0]-1)
		self.ax2.set_box_aspect(0.5)
		self.ax2.scatter(peak_one, image_1d[peak_one].get(), color='red')
		self.ax2.scatter(peak_two, image_1d[peak_two].get(), color='red')

		self.add_log('peaks at %s and %s, diameter: %.2f pixels' %(peak_one, peak_two, abs(peak_one - peak_two)))

		self.canvas.draw()

	def save_variable(self):
		self.update_parameter()
		self.optimized_sigma = self.sigma
		self.optimized_min_gap = self.min_gap
		self.ax1.clear()
		self.ax2.clear()
		self.root.destroy()

	def add_log(self, log_text):
		self.log_area.configure(state='normal')
		self.log_area.insert(tk.END, log_text + '\n')
		self.log_area.configure(state='disabled')
		self.log_area.see(tk.END)


	def startwindow(self):
		### create tkinter window
		self.root = tk.Tk()
		self.root.title("diameter finding optimization")
	
		### Create the input box and button 
		frame_controls = ttk.Frame(self.root)
		frame_controls.pack(side=tk.TOP, padx=5, pady=5)
		self.frame_controls = frame_controls
		label_slice = ttk.Label(frame_controls, text="image:")
		label_slice.pack(side=tk.LEFT, padx=(0, 5))
		slice_default = tk.StringVar()
		slice_default.set('1')
		self.entry_slice = self.create_entry( self.frame_controls, slice_default)

		label_angle = ttk.Label(frame_controls, text="angle:")
		label_angle.pack(side=tk.LEFT, padx=(10,5))
		self.angle_str = tk.StringVar()
		self.entry_angle = self.create_entry( self.frame_controls)
		angle_fromstar = ttk.Label(frame_controls, textvariable=self.angle_str)
		angle_fromstar.pack(side=tk.LEFT, padx=(10,5))

		label_sigma = ttk.Label(frame_controls, text='sigma:')
		label_sigma.pack(side=tk.LEFT, padx=(10,5))
		sigma_default = tk.StringVar()
		sigma_default.set('0')
		self.entry_sigma = self.create_entry( self.frame_controls )

		label_min_gap = ttk.Label(frame_controls, text='gap:')
		label_min_gap.pack(side=tk.LEFT, padx=(10,5))
		self.entry_min_gap = self.create_entry( self.frame_controls )

		button_update = ttk.Button(frame_controls, text="Update", command=self.update_plot)
		button_update.pack(side=tk.LEFT, padx=(5, 0))

		button_save = ttk.Button(frame_controls, text="Save", command=self.save_variable)
		button_save.pack(side=tk.LEFT)

		### create log area
		self.log_area = st.ScrolledText( self.root, wrap=tk.WORD, width=60, height=10)
		self.log_area.pack(padx=10, pady=10)
		self.log_area.configure(state='disabled')

		### create Matplotlib plot
		image = self.particles_df.loc[ 0, '_rlnImageName'].split('@')
		image_array = readslice( image )
		image_1d = cp.sum(image_array, axis=1)
	
		self.fig, (self.ax1, self.ax2) = pyplot.subplots(2, 1, figsize=(4,6), gridspec_kw={'height_ratios':[2,1]}, layout="constrained")
		self.ax1.imshow(image_array.get(), origin='lower', cmap='gray')
		self.ax2.plot(image_1d.get())
		self.ax2.set_xlim(0, image_1d.shape[0]-1)
		self.ax2.set_box_aspect(0.5)
	
		### Display the plot in the tkinter window
		self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
		self.canvas.draw()
	
		### start Tkinter event loop
		self.root.mainloop()
	
	def report(self):
		return self.optimized_sigma, self.optimized_min_gap, True


class choose_threshold_window:
	def __init__(self, particles_df):
		self.particles_df = particles_df
		self.startwindow()

	def startwindow(self):
		self.root = tk.Tk()
		self.root.title("choose diameter")

		### Create the input box and button
		frame_controls = ttk.Frame(self.root)
		frame_controls.pack(side=tk.TOP, padx=8, pady=8)


		label_min = ttk.Label(frame_controls, text="min:")
		label_min.pack(side=tk.LEFT, padx=(0, 5))
		self.entry_min = ttk.Entry(frame_controls, width=10)
		self.entry_min.pack(side=tk.LEFT)

		label_max = ttk.Label(frame_controls, text='max:')
		label_max.pack(side=tk.LEFT, padx=(10, 5))
		self.entry_max = ttk.Entry(frame_controls, width=10)
		self.entry_max.pack(side=tk.LEFT)

		self.button_save = ttk.Button(frame_controls, text="Save", command=self.save)
		self.button_save.pack(side=tk.LEFT, padx=(5, 0))

		self.fig, self.ax = pyplot.subplots(figsize=(6, 4))
		self.fig.subplots_adjust(bottom=0.1)
		self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1, pady=5)

		self.ax.hist(self.particles_df['_rlnDiameterByRASTR'], bins=200, color='blue', edgecolor='black')
		self.ax.set_title('Diameter distribution')
		self.ax.set_ylabel('#particles')
		self.ax.set_xlabel('diameter(A)')
		self.ax.grid(True)
		self.fig.tight_layout()

		self.canvas.mpl_connect('button_press_event', self.on_mouse_move)

		self.coords_label = ttk.Label(self.root, text="")
		self.coords_label.pack()

		self.canvas.draw()
		self.root.mainloop()

	def save(self):
		try:
			min_diameter = float(self.entry_min.get())
		except: min_diameter = 0.0
		try:
			max_diameter = float(self.entry_max.get())
		except: max_diameter = 10000.0
		self.min_diameter = min_diameter
		self.max_diameter = max_diameter
		self.thresholding()
		self.root.destroy()

	def thresholding(self):
		df = self.particles_df
		self.particles_df = df.loc[(df['_rlnDiameterByRASTR'] >= self.min_diameter) & (df['_rlnDiameterByRASTR'] <= self.max_diameter)]
	
	def on_mouse_move(self, event):
		if event.inaxes is not self.ax:
			return

		x, y = event.xdata, event.ydata
		self.coords_label['text'] = f'x={x:.2f}, y={y:.2f}'


def minimize_shift( particle ):
	image = particle['_rlnImageName'].split('@')
	psi = particle['_rlnAnglePsi']

	image_array = readslice(image)
	image_array = gaussian_filter( image_array, 2)
	image_array_rotated = rotate_image( image_array, psi=psi, x=0, y=0, order=3)
	image_projection = cp.sum(image_array_rotated, axis=1)
	peak_one, peak_two = find_peak( image_projection )

	distance = (peak_one + peak_two)/2 - image_array_rotated.shape[1]//2
	x = -distance * math.sin( psi/180.0*math.pi )
	y = -distance * math.cos( psi/180.0*math.pi )

	image_array_rotated = rotate_image( image_array, psi=psi, x=x, y=y, order=3)
	image_array_vertical = rotate_image( image_array_rotated, psi=-90, order=3)
	image_projection = cp.sum(image_array_rotated, axis=1)
	peak_one, peak_two = find_peak( image_projection )
	distance_after = abs( (peak_one + peak_two)/2 - image_array_rotated.shape[1]//2)

	if  distance_after >0:
		#print (image,' distance: ', distance_after)
		#image_array_vertical[240][240] = 9
		#pyplot.imshow(image_array_vertical.get(), origin='lower', cmap='gray')
		#pyplot.show()
		pass


	return x*pixel_size , y*pixel_size


def get_average( optics_df, particles_df ):

	boxsize = int( optics_df.loc[ 0, '_rlnImageSize' ] )
	projection = cp.zeros(( boxsize, boxsize ))

	for line_number, particle in particles_df.iterrows():
		image = particle['_rlnImageName'].split('@')
		image_array = readslice(image)


		psi = float( particle['_rlnAnglePsi'])
		x = float( particle['_rlnOriginXAngst']) / pixel_size
		y = float( particle['_rlnOriginYAngst']) / pixel_size

		image_array_rotated = rotate_image( image_array, psi=psi, x=x, y=y, order=3)

		projection += image_array_rotated
		print(f'Processed {line_number + 1} /{particles_df.shape[0]}', end='\r')
	projection /= particles_df.shape[0]

	return projection

def parseOptions():
	parser = argparse.ArgumentParser()

	parser.add_argument('-i','--i', action='store', dest='input_star',
			help=' initial star file with correct psi angles')

	parser.add_argument('-o','--o', action='store', dest='output_star',
			help=' output star file')

	parser.add_argument('-m','--model', action='store', dest='model', default=None,
			help=' azimuthal average model as reference')

	parser.add_argument('-d','--diameter', action='store_true', dest='find_diameter', default=False,
			help=' option to classify images based on diameters')

	parser.add_argument('-p','--psi', action='store_true', dest='find_psi', default=False,
			help=' option to find the correct psi angle')

	parser.add_argument('-s','--shift', action='store_true', dest='minimize_shift', default=False,
			help=' option to minimize x, y shift based on correct psi angle')

	parser.add_argument('--particle_number', action='store', dest='particle_number', default=None,
			help=' option to process a small number of particles first')

	parser.add_argument('--classify', action='store_true', dest='justclassify', default=False, 
			help=' when you just want to classify based on diameters calculated already')

	parser.add_argument('--showaverage', action='store_true', dest='showaverage', default=False,
			help=' check diameter and shifts by calculating an average particle')

	results=parser.parse_args()

	#make sure required arguments are present
	if results.input_star == None:
		pass

	return (results)



def main():

	results = parseOptions()

	starfile = StarFile( results.input_star )
	optics_df = starfile.optics_df

	if results.model is not None:
		model_3d = mrcfile.read(results.model)
		model_3d = cp.asarray( model_3d )
		model_2d = project_volume ( volume=model_3d, rot=0, tilt=90, psi=0, order=3 )
	else:
		model_2d = None


	if results.particle_number is not None:
		starfile.particles_df = starfile.particles_df.sample(n=int(results.particle_number)).reset_index(drop=True)
	particles_df = starfile.particles_df

	global pixel_size
	pixel_size = float(optics_df.loc[0,'_rlnImagePixelSize'])

	print ( 'parsing finished, start calculation')

	if results.justclassify:
		threshold_window = choose_threshold_window( starfile.particles_df )
		starfile.particles_df = threshold_window.particles_df

	if results.find_diameter:
		optimized = False
		while not optimized:
			optimizer = optimize_diameter_parameter( particles_df )
			optimizer.startwindow()
			sigma, min_gap, optimized = optimizer.report()
			pyplot.close()

	if results.find_psi:
		# If model is provided, only one iteration.
		if model_2d is None:
			updated_psi_values = find_psi( starfile, model_2d, mode='full' )
		else:
			updated_psi_values = find_psi( starfile, model_2d, mode='fast' )

		starfile.particles_df['_rlnAnglePsi'] = updated_psi_values
		particles_df = starfile.particles_df


	if results.find_diameter:

		diameters = find_diameter( particles_df, sigma, min_gap)
		diameters_df = pd.DataFrame(diameters)
		starfile.particles_df = pd.concat([particles_df, diameters_df], axis=1)
		threshold_window = choose_threshold_window( starfile.particles_df )

		starfile.particles_df = threshold_window.particles_df
		

	if results.minimize_shift:
		shifts = [ minimize_shift( starfile.particles_df.iloc[line_number]) for line_number in range(starfile.particles_df.shape[0])]
		xshifts, yshifts = zip(*shifts)
		starfile.particles_df['_rlnOriginXAngst'] = xshifts
		starfile.particles_df['_rlnOriginYAngst'] = yshifts
		particles_df = starfile.particles_df


	if results.showaverage:
		average = get_average( optics_df, particles_df )
		pyplot.clf()
		pyplot.imshow(average.get(), origin='lower', cmap='gray')
		pyplot.show()

	starfile.write( results.output_star)

if __name__ == '__main__':
	main()
