#!/bin/bash
db=$1
source /n/fs/darkpatterns/analysis/dp/bin/activate && \
  python preprocessing.py $db features.npy segments.dataframe && \
  python clustering.py features.npy segments.dataframe segments_cluster.dataframe && \
  python visualize.py segments_cluster.dataframe clusters.csv
