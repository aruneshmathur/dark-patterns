import pandas as pd
import logging
import os
import hdbscan
from scipy import sparse
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.cluster import DBSCAN
import hdbscan
import fastcluster
from scipy.spatial import distance
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Agg')

usage = 'python %s FT-INFILE SEGMENTS-INFILE SEGMENTS-OUTFILE' % __file__
help_message = '''Clusters the feature vectors from the array FT-INFILE, and produces
a copy of the segments dataframe from SEGMENTS-INFILE including a new column for the
cluster labels belonging to each segment. The new segments dataframe is written to
SEGMENTS-OUTFILE.'''
LOG_FILE_NAME = 'clustering.log'

try:
    os.remove(LOG_FILE_NAME)
    os.remove('linkage.matrix')
    os.remove('cluster.png')
    os.remove('clusters.dataframe')
except:
    pass

logger = logging.getLogger(__name__)
lf_handler = logging.FileHandler(LOG_FILE_NAME)
lf_format = logging.Formatter('%(asctime)s - %(message)s')
lf_handler.setFormatter(lf_format)
logger.addHandler(lf_handler)
logger.setLevel(logging.INFO)


def distance_clustering(features):
    logger.info('Clustering the segments using Heirarchical Clustering')

    logger.info('Computing distance metric ...')
    featdense = features.todense()
    distances = distance.pdist(featdense, metric='cosine')
    #distances = distance.pdist(featdense[np.random.randint(featdense.shape[0], size=5000), :], metric='euclidean')
    logger.info('Done')

    logger.info('Converting to squareform ...')
    distances = distance.squareform(distances, checks = False)
    logger.info('Done')

    logger.info('Clustering the segments ...')
    clusters = fastcluster.linkage(distances, method = 'ward', preserve_input = False)

    plt.figure(figsize=(25, 10))
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('sample index')
    plt.ylabel('distance')
    dendrogram(
        clusters,
        leaf_rotation=90.,
        leaf_font_size=8.,
    )
    plt.savefig('cluster.png', bbox_inches='tight')
    logger.info('Done')

    logger.info('Pickling linkage matrix ...')
    np.save('linkage.matrix', clusters)
    logger.info('Done')


def dbscan_clustering(features, segments, segments_outfile, eps, min_samples):
    logger.info('Clustering the segments using DBSCAN ...')
    clusterer = DBSCAN(eps=eps, min_samples=min_samples, n_jobs=10, metric='cosine')
    cluster_labels = clusterer.fit(features)
    segments['cluster'] = pd.Series(cluster_labels.labels_).values

    logger.info('segments[\'cluster\'].value_counts(): \n %s' % segments['cluster'].value_counts().to_string())

    segments.to_pickle(segments_outfile)
    logger.info('Done')


def hdbscan_clustering(features, segments, segments_outfile, min_cluster_size):
    logger.info('Clustering the segments using HDBSCAN ...')

    logger.info('Normalizing each segment vector ...')
    features = normalize(features, axis=1) # Normalize each segment since using euclidean distance metric
    logger.info('Done')

    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric='euclidean')
    cluster_labels = clusterer.fit_predict(features)
    segments['cluster'] = pd.Series(cluster_labels).values

    logger.info('segments[\'cluster\'].value_counts(): \n %s' % segments['cluster'].value_counts().to_string())

    segments.to_pickle(segments_outfile)
    logger.info('Clustering complete')


if __name__ == '__main__':
    if len(sys.argv[1:]) != 3:
        print usage
        print ''
        print help_message
        exit(1)
    features_infile = sys.argv[1]
    segments_infile = sys.argv[2]
    segments_outfile = sys.argv[3]
    try:
        logger.info('Reading features.npy ...')
        features = np.load(features_infile)
        logger.info('Done')

        logger.info('Number of features: %s' % str(features.shape))

        logger.info('Reading segments_feature.dataframe ...')
        segments = pd.read_pickle(segments_infile)
        logger.info('Done')

        #distance_clustering(features)
        dbscan_clustering(features, segments, segments_outfile, 0.0001, 3)
        #hdbscan_clustering(features, segments, segments_outfile, 5)

    except:
        logger.exception('Exception')
