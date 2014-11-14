"""
  Utility functions that wrap file I/O for us.
"""

import csv

# Returns a list of rows, where a row is a list of strings (parsed
# from the file).
def parse_csv_file(file_path):
  assert(file_path.endswith('.csv'))

  rows = []

  with open(file_path, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
      rows.append(row)

  return rows
  
def read_lines(file_path):
  with open(file_path, 'r') as f:
    return [line.strip() for line in list(f)]

