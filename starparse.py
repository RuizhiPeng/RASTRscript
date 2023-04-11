#! /usr/bin/env python
import pandas as pd
import re
from io import StringIO

class StarFile:
	def __init__(self, file_path):
		self.file_path = file_path
		self.optics_df, self.particles_df = self.read_star_file(file_path)

	def read_star_file(self, file_path):
		with open(file_path, 'r') as file:
			content = file.read()

	
		optics_pattern = r'data_optics(.*?)data_particles'
		particles_pattern = r'data_particles(.*?)$'

		optics_block = re.search(optics_pattern, content, re.DOTALL).group(1).strip()
		particles_block = re.search(particles_pattern, content, re.DOTALL).group(1).strip()

		optics_header, optics_data = self.extract_header_and_data_block(optics_block)
		particles_header, particles_data = self.extract_header_and_data_block(particles_block)

		optics_df = self.create_dataframe_from_data(optics_header, optics_data)
		particles_df = self.create_dataframe_from_data(particles_header, particles_data)

		return optics_df, particles_df

	def extract_header_and_data_block(self, block):
		header_lines = ' '.join([line for line in block.split('\n') if line.startswith('_rln')])
		data_block = '\n'.join([line for line in block.split('\n') if not line.startswith('_rln') and not line.startswith('loop_') and not line.startswith('#')])

		headers = [item.strip() for item in re.findall(r'(_rln\w+)', header_lines)]

		return headers, data_block

	def create_dataframe_from_data(self, headers, data_block):
		data = StringIO(data_block)
		df = pd.read_csv(data, names=headers, delim_whitespace=True)

		return df


	def modify_angle(self, value):
		if '_rlnAngleRot' in self.particles_df.columns:
			self.particles_df['_rlnAngleRot'] += value

	def write(self, output_file_path):
		with open(output_file_path, 'w') as file:
			file.write("# version 30001\n\n")
			file.write("data_optics\n\n")
			file.write("loop_\n")
			file.write(self.dataframe_to_star_block(self.optics_df))
			file.write("\n# version 30001\n\n")
			file.write("data_particles\n\n")
			file.write("loop_\n")
			file.write(self.dataframe_to_star_block(self.particles_df))

	def dataframe_to_star_block(self, df):
		columns = df.columns.tolist()
		header_line = self.build_header_line(columns)
		data_block = df.to_string(header=False, index=False, col_space=12, formatters=self.formatter())
		return header_line + data_block + '\n'

	def build_header_line(self, columns):
		header_line = ''
		for i, col in enumerate(columns, 1):
			header_line += f"{col} #{i} \n"
		return header_line

	def formatter(self):
		return {column: (lambda x: f"{x: >12.6f}" if isinstance(x, float) else f"{x: >12}") for column in self.optics_df.columns}


if __name__ == '__main__':

# Usage example
	file_path = 'test.star'  # Replace with your STAR file path
	star_file = StarFile(file_path)

#	star_file.write( 'test2.star' )

#	print("Optics DataFrame:")
#	print(star_file.optics_df)
#	print("\nParticles DataFrame:")
	print(star_file.particles_df.loc[0,'_rlnAnglePsi'])
