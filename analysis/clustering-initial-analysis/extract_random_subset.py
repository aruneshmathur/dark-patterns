from common import *
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

  # Extract random subset of data and write out to target file
  debug('Reading clustering data...')
  segments = pd.read_pickle(datafile)
  debug('Done')

  debug("segments['inner_text']: %s" % str(segments['inner_text'].shape))
  debug("segments['cluster']: %s" % str(segments['cluster'].shape))

  debug('Extracting random subset of size %d...' % size_subset)
  n = segments['inner_text'].shape[0]
  subset_indices = np.random.choice(np.arange(n), size=size_subset, replace=False)
  subset = pd.DataFrame.from_dict({'inner_text': segments['inner_text'][subset_indices], 'cluster': segments['cluster'][subset_indices]})
  subset.to_pickle('cluster_subset_%d.dataframe' % size_subset)
  debug('subset shape (should be (%d, %d) where columns are "inner_text" and "cluster"): %s' % (size_subset, 2, str(subset.shape)))
  debug('Done')
