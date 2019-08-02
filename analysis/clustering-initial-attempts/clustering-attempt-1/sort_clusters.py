from __future__ import print_function
from tqdm import tqdm
import json
import os.path
import sys

usage = 'Usage: python %s CLUSTERS-FILE OUT-FILE' % __file__
help_message = '''Sorts clusters in the provided file by size, with largest first.
Clusters should be formatted in the same way as accepted by cluster_browser.py. Specify
the name of the output file as OUT-FILE.'''

if __name__ == '__main__':
  # Check usage
  if len(sys.argv[1:]) != 2:
    print(usage)
    print()
    print(help_message)
    sys.exit(1)

  clusters_file = sys.argv[1]
  out_file = sys.argv[2]
  if not os.path.isfile(clusters_file):
    print('Error: Clusters file not found: %s' % clusters_file)
    sys.exit(1)
  if os.path.isfile(out_file):
    print('Error: output file already exists. Exiting to avoid overwriting: %s' % out_file)
    sys.exit(1)

  print('Reading in clusters...')
  clusters = []
  with open(clusters_file, 'r') as f:
    for line in tqdm(f):
      c = json.loads(line)
      clusters.append(c)

  print('Sorting clusters...')
  clusters_sort = sorted(clusters, cmp=lambda x, y: len(y[y.keys()[0]]) - len(x[x.keys()[0]]))

  print('Writing sorted clusters to file...')
  with open(out_file, 'w') as f:
    for c in tqdm(clusters_sort):
      f.write(json.dumps(c) + '\n')
