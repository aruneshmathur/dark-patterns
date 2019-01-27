import logging
import numpy as np
import os
import pandas as pd
import sys

usage = 'Usage: python %s DATAFILE SIZE' % __file__
help_message = '''Extracts a subset of SIZE examples from the DATAFILE. The
DATAFILE should be in the format output by clustering.py.'''

if __name__ == '__main__':
  # Check arg
  if len(sys.argv[1:]) != 2:
    print usage
    print ''
    print help_message
    exit(1)
  datafile = sys.argv[1]
  size_subset = int(sys.argv[2])

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

  # Extract random subset of data and write out to target file
  logger.info('Reading clustering data...')
  segments = pd.read_pickle(datafile)
  logger.info('Done')

  logger.info("segments['inner_text']: %s" % str(segments['inner_text'].shape))
  logger.info("segments['cluster']: %s" % str(segments['cluster'].shape))

  logger.info('Extracting random subset of size %d...' % size_subset)
  n = segments['inner_text'].shape[0]
  subset_indices = np.random.choice(np.arange(n), size=size_subset, replace=False)
  subset = pd.DataFrame.from_dict({'inner_text': segments['inner_text'][subset_indices], 'cluster': segments['cluster'][subset_indices]})
  subset.to_pickle('cluster_subset_%d.dataframe' % size_subset)
  logger.info('subset shape (should be (%d, %d) where columns are "inner_text" and "cluster"): %s' % (size_subset, 2, str(subset.shape)))
  logger.info('Done')
