#! /usr/bin/env python

import random
import sys

input_file = sys.argv[1]
output_file = input_file.split('.')[0]+'randomphi.par'

# Open the original file and a new file to write to
with open(input_file, 'r') as f, open(output_file, 'w') as out:
    # Read the first line (header) and write it to the new file
    header = f.readline()
    out.write(header)

    # Process the remaining lines
    for line in f:
        if line[0] == 'C':
            out.write(line)
            continue
        # Split the line into columns
        columns = line.split()

        # Replace the PHI value with a random value between 0 and 360
        columns[3] = "{:.2f}".format(random.uniform(0, 360))

        # Recreate the line with the original spacing
        new_line = "{:>7}{:>8}{:>8}{:>8}{:>10}{:>10}{:>8}{:>6}{:>9}{:>9}{:>8}{:>8}{:>8}{:>10}{:>11}{:>8}{:>8}\n".format(*columns)
        # Write the line to the new file
        out.write(new_line)

