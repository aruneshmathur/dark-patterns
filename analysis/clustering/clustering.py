import pandas as pd
import logging
import os
import fastcluster
from scipy.spatial import distance
from scipy import sparse
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram
import numpy as np

LOG_FILE_NAME = 'clustering.log'

try:
    os.remove(LOG_FILE_NAME)
    os.remove('cluster.csv')
except:
    pass

logger = logging.getLogger(__name__)
lf_handler = logging.FileHandler(LOG_FILE_NAME)
lf_format = logging.Formatter('%(asctime)s - %(message)s')
lf_handler.setFormatter(lf_format)
logger.addHandler(lf_handler)
logger.setLevel(logging.INFO)


if __name__ == '__main__':
    try:
        logger.info('Reading features.txt ...')
        features = sparse.load_npz('features.npz')
        logger.info('Done')

        logger.info('Computing distance metric ...')
        featdense = features.todense()
        distances = distance.pdist(featdense[np.random.randint(featdense.shape[0], size=5000), :], metric='cosine')
        #distances = distance.pdist(featdense[np.random.randint(featdense.shape[0], size=5000), :], metric='euclidean')
        logger.info('Done')

        logger.info('Converting to squareform ...')
        distances = distance.squareform(distances, checks = False)
        logger.info('Done')

        logger.info('Clustering the segments ...')
        clusters = fastcluster.linkage(distances, method = 'ward', preserve_input = False)
        logger.info('Done')

        plt.figure(figsize=(25, 10))
        plt.title('Hierarchical Clustering Dendrogram')
        plt.xlabel('sample index')
        plt.ylabel('distance')
        dendrogram(
            clusters,
            leaf_rotation=90.,  # rotates the x axis labels
            leaf_font_size=8.,  # font size for the x axis labels
        )
        plt.savefig('cluster.png', bbox_inches='tight')
        #plt.show()

    except:
        logger.exception('Exception')
