#! /usr/bin/env python
import tkinter as tk
from tkinter import ttk
import numpy as np
from scipy.ndimage import rotate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mrcfile
import sys
from scipy.ndimage import gaussian_filter


imagefile = sys.argv[1]

def readmrcs(filename, zslice=0):
	with mrcfile.mmap(imagefile, mode='r') as imagestack:
		image_array = imagestack.data[zslice]
	return image_array

def rotate_image(image_array, psi=0 ):
	if psi != 0:
		image_array = rotate ( image_array, -psi, axes=(0,1), mode='constant', reshape=False, order=3)
	return image_array


# Function to update the plot based on user input
def update_plot():
	try:
		zslice = int(entry_slice.get()) - 1
	except:zslice = 1
	try:
		angle = float(entry_angle.get())
	except:angle = 0.0
	try:
		sigma = int(entry_sigma.get())
	except:sigma = 0
	try:
		image_array = readmrcs( imagefile, zslice)
		image_array = rotate_image(image_array, psi=angle)
		image_array = gaussian_filter(image_array, sigma)
		ax.clear()
		ax.imshow(image_array, origin='lower', cmap='gray')
		canvas.draw()
	except ValueError:
		pass

# Create the Tkinter window
root = tk.Tk()
root.title("Interactive Plot")

# Create the input box and button
frame_controls = ttk.Frame(root)
frame_controls.pack(side=tk.TOP, padx=5, pady=5)

label_slice = ttk.Label(frame_controls, text="slice:")
label_slice.pack(side=tk.LEFT, padx=(0, 5))
slice_default = tk.StringVar()
slice_default.set('1')
entry_slice = ttk.Entry(frame_controls, width=10, textvariable=slice_default)
entry_slice.pack(side=tk.LEFT)

label_angle = ttk.Label(frame_controls, text="angle:")
label_angle.pack(side=tk.LEFT, padx=(10,5))
entry_angle = ttk.Entry(frame_controls, width=10)
entry_angle.pack(side=tk.LEFT)

label_sigma = ttk.Label(frame_controls, text='sigma:')
label_sigma.pack(side=tk.LEFT, padx=(10,5))
entry_sigma = ttk.Entry(frame_controls, width=10)
entry_sigma.pack(side=tk.LEFT)



button_update = ttk.Button(frame_controls, text="Update", command=update_plot)
button_update.pack(side=tk.LEFT, padx=(5, 0))

# Create the Matplotlib plot
image_array = readmrcs(imagefile, 0)



fig, ax = plt.subplots(figsize=(5, 3))
ax.imshow(image_array, origin='lower', cmap='gray')

# Display the plot in the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
canvas.draw()

# Run the Tkinter event loop
root.mainloop()
