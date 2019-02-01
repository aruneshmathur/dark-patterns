from common import *
from collections import defaultdict
import logging
import numpy as np
import pandas as pd
import sys
import unicodecsv as csv

usage = 'Usage: python %s SEGMENTS-INFILE OUTFILE' % __file__
help_message = '''Reads the segments from SEGMENTS-INFILE and produces a CSV file
(written to OUTFILE) that shows the segments in each cluster. SEGMENTS-INFILE should
be the output of clustering.py.'''

if __name__ == '__main__':
  # Check arg
  if len(sys.argv[1:]) != 2:
    print usage
    print ''
    print help_message
    exit(1)
  datafile = sys.argv[1]
  outfile = sys.argv[2]

  # Generate CSV file from clusters
  debug('Reading segments...')
  segments = pd.read_pickle(datafile)
  debug('Done')

  inner_texts = segments['inner_text']
  cluster_labels = segments['cluster']
  debug("segments['inner_text'] is %s, segments['cluster'] is %s (should be the same)" % (str(inner_texts.shape), str(cluster_labels.shape)))
  assert inner_texts.shape == cluster_labels.shape

  debug('Grouping segments by cluster...')
  segments_by_cluster = defaultdict(lambda: [])
  for i in range(inner_texts.shape[0]):
    segments_by_cluster[str(cluster_labels[i])].append(inner_texts[i])
  debug('Done')

  debug('Outputting CSV file...')
  with open(outfile, 'wb') as f:
    writer = csv.writer(f)
    for cluster, segments in segments_by_cluster.iteritems():
      segments_str = '\n\n'.join(segments)
      writer.writerow([cluster, segments_str])
  debug('Done')
