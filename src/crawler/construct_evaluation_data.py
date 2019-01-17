import unicodecsv as csv
import os
import re
import sys

usage = 'Usage: python %s DATA-FOLDER OUTFILE' % os.path.basename(__file__)

# Constructs a csv file containing the data in the data folder. Data is
# expected in the following format: within the folder, each data item should
# be one file. The first line of the file should be the url, and everything
# afterwards is the target element (e.g. add-to-cart button, cart button, etc.).
# Use this script to convert to a csv file since it is difficult to manually
# create a csv file if the target element contains newlines or other special
# characters. All such occurrences of multiple whitespace characters will be
# converted into a single space.
#
# If the output file already contains data, the new data will be appended.
def main():
  if len(sys.argv[1:]) < 2:
    print usage
    exit(1)

  data_folder = sys.argv[1]
  out_file = sys.argv[2]
  data_files = os.listdir(data_folder)

  # Read data
  rows = []
  for data_file in data_files:
    with open(os.path.join(data_folder, data_file), 'r') as f:
      url = f.readline().strip()
      elem = re.sub(r'\s+', ' ', f.read().strip())
      rows.append([url, elem])

  # Write csv
  with open(out_file, 'a') as f:
    writer = csv.writer(f, encoding='utf-8')
    writer.writerows(rows)

  print 'Done'

if __name__ == '__main__':
  main()
