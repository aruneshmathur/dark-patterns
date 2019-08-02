import sys
import numpy as np
import hdbscan
import pandas as pd

if (len(sys.argv) != 5):
    print 'Usage: python cluster.py [feature_file] [min_cluster_size] [metric] [label_pickle_file]'
    sys.exit(1)

arr = pd.read_csv(sys.argv[1], sep=' ', header=None, dtype=np.float64).values
print arr.shape

clusterer = hdbscan.HDBSCAN(min_cluster_size=int(sys.argv[2]), metric=sys.argv[3], core_dist_n_jobs=-1, algorithm='boruvka_kdtree')
cluster_labels = clusterer.fit_predict(arr)
ser = pd.Series(cluster_labels)

print ser.value_counts().to_string()

ser.to_pickle(sys.argv[4])

