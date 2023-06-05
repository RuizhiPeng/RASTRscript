#! /usr/bin/env python
import sys
import numpy as np
import mrcfile
from multiprocessing import Pool
import os
import time
def bin2(img):
	"""Bin an image by a factor of 2."""
	return img.reshape((img.shape[0]//2, 2, img.shape[1]//2, 2)).mean(axis=(1, 3))

def bin_image(img, factor):
	"""Bin an image by a specified factor."""
	for _ in range(int(np.log2(factor))):
		img = bin2(img)
	return img

def bin_images(input_file, start, end, output_file, factor):
	"""Bin all images in an MRC file by a specified factor."""
	with mrcfile.mmap(input_file, 'r') as mrc:
		images = mrc.data[start:end]
		bin_images = np.empty((images.shape[0], images.shape[1]//factor, images.shape[2]//factor), dtype=images.dtype)
		for i in range(images.shape[0]):
			bin_images[i] = bin_image(images[i], factor)

	with mrcfile.new(output_file, overwrite=True) as mrc:
		mrc.set_data(bin_images)

def process_chunk(args):
	"""Process a chunk of images."""
	input_file, start, end, output_file, factor = args
	bin_images(input_file, start, end, output_file, factor)

def main(input_file, factor, num_processes=2):
	time_1 = time.time()
	"""Main function."""
	factor = int(factor)
	num_processes = int(num_processes)
	assert factor & (factor - 1) == 0, "Factor must be a power of 2"
	output_file = f"{os.path.splitext(input_file)[0]}bin{factor}.mrc"
	with mrcfile.mmap(input_file, 'r') as mrc:
		num_images = mrc.data.shape[0]
	chunk_size = (num_images + num_processes - 1) // num_processes
	chunks = [(input_file, i*chunk_size, min((i+1)*chunk_size, num_images), f"tempfile{i}.mrc", factor) for i in range(num_processes)]
	with Pool(num_processes) as pool:
		pool.map(process_chunk, chunks)
	with mrcfile.mmap(f"tempfile0.mrc", 'r') as temp_mrc:
		data = temp_mrc.data
	for i in range(1,num_processes):
		with mrcfile.mmap(f"tempfile{i}.mrc", 'r') as temp_mrc:
			data = np.concatenate((data, temp_mrc.data)) if data is not None else temp_mrc.data
		os.remove(f"tempfile{i}.mrc")
	with mrcfile.new(output_file, overwrite=True) as mrc:
		mrc.set_data(data)
	os.remove("tempfile0.mrc")
	time_2 = time.time()
	print("time spent: ",time_2-time_1," seconds")
if __name__ == "__main__":
	main(*sys.argv[1:])

