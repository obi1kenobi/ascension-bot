"""
  Utility functions that wrap file I/O for us.
"""

import csv
from os import path

# Returns a list of rows, where a row is a list of strings (parsed
# from the file).
def parse_csv_file(file_path):
  assert(file_path.endswith('.csv'))
  # file_path = path.join(path.dirname(__file__), file_path)

  rows = []

  with open(file_path, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
      rows.append(row)

  return rows

def read_lines(file_path):
  # file_path = path.join(path.dirname(__file__), file_path)
  with open(file_path, 'r') as f:
    return [line.strip() for line in list(f)]

def read_kvp_file(file_path, T):
  lines = read_lines(file_path)
  splits = [line.split(':') for line in lines]

  return {split[0]: T(split[1]) for split in splits}

