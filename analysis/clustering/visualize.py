from collections import defaultdict
import logging
import numpy as np
import pandas as pd
import sys
import unicodecsv as csv

usage = 'Usage: python %s DATAFILE' % __file__
help_message = '''Produces a CSV file that shows the segments in each cluster. DATAFILE
should the output of clustering.py.'''

if __name__ == '__main__':
  # Check arg
  if len(sys.argv[1:]) != 1 or sys.argv[1] in ['-h', '--help']:
    print usage
    print ''
    print help_message
    exit(1)
  datafile = sys.argv[1]

  # Set up logger
  logfile = '%s.log' % __file__.replace('.py', '')
  try:
    os.remove(logfile)
  except:
    pass
  logger = logging.getLogger(__name__)
  lf_handler = logging.FileHandler(logfile)
  lf_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
  logger.addHandler(lf_handler)
  logger.setLevel(logging.INFO)

  # Generate CSV file from clusters
  logger.info('Reading segments...')
  segments = pd.read_pickle(datafile)
  logger.info('Done')

  inner_texts = segments['inner_text']
  cluster_labels = segments['cluster']
  logger.info("segments['inner_text'] is %s, segments['cluster'] is %s (should be the same)" % (str(inner_texts.shape), str(cluster_labels.shape)))
  assert inner_texts.shape == cluster_labels.shape

  logger.info('Grouping segments by cluster...')
  segments_by_cluster = defaultdict(lambda: [])
  for i in range(inner_texts.shape[0]):
    segments_by_cluster[str(cluster_labels[i])].append(inner_texts[i])
  logger.info('Done')

  logger.info('Outputting CSV file...')
  with open('clusters.csv', 'wb') as f:
    writer = csv.writer(f)
    for cluster, segments in segments_by_cluster.iteritems():
      segments_str = '\n\n'.join(segments)
      writer.writerow([cluster, segments_str])
  logger.info('Done')
