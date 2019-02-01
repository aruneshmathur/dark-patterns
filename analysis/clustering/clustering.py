from common import *
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

def distance_clustering(features):
    debug('Clustering the segments using Heirarchical Clustering')

    debug('Computing distance metric ...')
    featdense = features.todense()
    distances = distance.pdist(featdense, metric='cosine')
    #distances = distance.pdist(featdense[np.random.randint(featdense.shape[0], size=5000), :], metric='euclidean')
    debug('Done')

    debug('Converting to squareform ...')
    distances = distance.squareform(distances, checks = False)
    debug('Done')

    debug('Clustering the segments ...')
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
    debug('Done')

    debug('Pickling linkage matrix ...')
    np.save('linkage.matrix', clusters)
    debug('Done')


def dbscan_clustering(features, segments, segments_outfile, eps, min_samples):
    debug('Clustering the segments using DBSCAN ...')
    clusterer = DBSCAN(eps=eps, min_samples=min_samples, n_jobs=10, metric='cosine')
    cluster_labels = clusterer.fit(features)
    segments['cluster'] = pd.Series(cluster_labels.labels_).values

    debug('segments[\'cluster\'].value_counts(): \n %s' % segments['cluster'].value_counts().to_string())

    segments.to_pickle(segments_outfile)
    debug('Done')


def hdbscan_clustering(features, segments, segments_outfile, min_cluster_size):
    debug('Clustering the segments using HDBSCAN ...')

    debug('Normalizing each segment vector ...')
    features = normalize(features, axis=1) # Normalize each segment since using euclidean distance metric
    debug('Done')

    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric='euclidean')
    cluster_labels = clusterer.fit_predict(features)
    segments['cluster'] = pd.Series(cluster_labels).values

    debug('segments[\'cluster\'].value_counts(): \n %s' % segments['cluster'].value_counts().to_string())

    segments.to_pickle(segments_outfile)
    debug('Clustering complete')


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
        debug('Reading features.npy ...')
        features = np.load(features_infile)
        debug('Done')

        debug('Number of features: %s' % str(features.shape))

        debug('Reading segments_feature.dataframe ...')
        segments = pd.read_pickle(segments_infile)
        debug('Done')

        #distance_clustering(features)
        dbscan_clustering(features, segments, segments_outfile, 0.0001, 3)
        #hdbscan_clustering(features, segments, segments_outfile, 5)

    except Exception, e:
        debug('Exception: %s' % str(e))
