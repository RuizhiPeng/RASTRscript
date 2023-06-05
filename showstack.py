#! /usr/bin/env python
### originally developped to test tkinter GUI display, now function to show particle stacks.
### input can be either mrcs or star file.
### usage ./showstack.py  stack.mrcs
###       ./showstack.py  stack.star

import tkinter as tk
from tkinter import ttk
import numpy as np
from scipy.ndimage import rotate, shift
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mrcfile
import sys
from scipy.ndimage import gaussian_filter
from starparse import StarFile



def readstack(filename, zslice=1):

	if filename[-4:] == 'mrcs':
		with mrcfile.mmap(imagefile, mode='r') as imagestack:
			image_array = imagestack.data[zslice-1]
			center = image_array.shape[0] // 2
		return image_array, center, center

	elif filename[-4:] == 'star':

		starfile = StarFile ( filename )
		optics_df = starfile.optics_df
		pixel_size = float(optics_df.loc[0,'_rlnImagePixelSize'])
		particles_df = starfile.particles_df
		image = particles_df.loc[ zslice-1, '_rlnImageName'].split('@')

		with mrcfile.mmap(image[1], mode='r') as imagestack:
			image_slice = int(image[0])-1
			image_array = imagestack.data[image_slice]

		x = float( particles_df.loc[ zslice-1, '_rlnOriginXAngst']) / pixel_size
		y = float( particles_df.loc[ zslice-1, '_rlnOriginYAngst']) / pixel_size
		center_y, center_x = np.array(image_array.shape) // 2
		x_shifted, y_shifted = center_x - x, center_y - y
		
		return image_array, x_shifted, y_shifted

def rotate_image(image_array, psi=0, x=0, y=0, order=3 ):
	if x != 0 or y != 0:
		image_array = shift ( image_array, (y,x), mode='wrap' )
	if psi != 0:
		image_array = rotate ( image_array, -psi, axes=(0,1), mode='constant', reshape=False, order=order)
	return image_array



class ShowStack:
	def __init__(self, filename):
		self.filename = filename
		self.root = tk.Tk()
		self.root.title("Interactive Plot")
		self.fig, self.ax = plt.subplots(figsize=(5, 3))
		self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
		self.canvas.draw()

		self.frame_controls = ttk.Frame(self.root)
		self.frame_controls.pack(side=tk.TOP, padx=5, pady=5)


		self.zslice = 1
		self.angle = 0.0
		self.sigma = 0
		self.label_slice = ttk.Label(self.frame_controls, text="slice:")
		self.label_slice.pack(side=tk.LEFT, padx=(0, 5))

		self.button_left = tk.Button(self.frame_controls, text="\u25C0", command=self.previous_slice, padx=1, pady=1)
		self.button_left.pack(side=tk.LEFT, padx=(0,1))
		self.zslice_text = tk.StringVar()
		self.zslice_text.set(str(self.zslice))
		self.entry_slice = self.create_entry( self.frame_controls, self.zslice_text)
		self.button_right = tk.Button(self.frame_controls, text="\u25B6", command=self.next_slice, padx=1, pady=1)
		self.button_right.pack(side=tk.LEFT, padx=(0,1))


		self.label_angle = ttk.Label(self.frame_controls, text="angle:")
		self.label_angle.pack(side=tk.LEFT, padx=(10,5))
		self.entry_angle = self.create_entry( self.frame_controls)

		self.label_sigma = ttk.Label(self.frame_controls, text='sigma:')
		self.label_sigma.pack(side=tk.LEFT, padx=(10,5))
		self.entry_sigma = self.create_entry( self.frame_controls)

		self.button_update = ttk.Button(self.frame_controls, text="Update", command=self.update_variable)
		self.button_update.pack(side=tk.LEFT, padx=(5, 0))

		self.root.mainloop()
	def next_slice(self):
		self.zslice += 1
		self.update_plot()
	
	def previous_slice(self):
		if self.zslice > 1:
			self.zslice -= 1
		else:
			print(' already the first slice ')
		self.update_plot()

	def update_variable(self):
		try:
			zslice = int(self.entry_slice.get())
		except:
			zslice = 1
		try:
			angle = float(self.entry_angle.get())
		except:
			angle = 0.0
		try:
			sigma = int(self.entry_sigma.get())
		except:
			sigma = 0

		self.zslice = zslice
		self.angle = angle
		self.sigma = sigma
		self.update_plot()

	def update_plot(self):
		self.zslice_text.set(str(self.zslice))
		try:
			self.ax.clear()
			image_array, x, y = readstack(self.filename, self.zslice)
			image_array = rotate_image(image_array, psi=self.angle)
			image_array = gaussian_filter(image_array, self.sigma)
			self.ax.imshow(image_array, origin='lower', cmap='gray')
			self.ax.scatter(x, y, color='red')
			self.canvas.draw()
		except ValueError:
			pass
	

	def create_entry(self, parent, default_text=None):
		default_text = default_text or tk.StringVar()
		entry = ttk.Entry(parent, width=10, justify=tk.CENTER, textvariable=default_text)
		entry.pack(side=tk.LEFT)
		entry.bind('<Return>', lambda event: self.update_plot())
		entry.bind('<KP_Enter>', lambda event: self.update_plot())
		return entry

if __name__ == '__main__':
	ShowStack(sys.argv[1])




