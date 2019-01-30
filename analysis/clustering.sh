source /n/fs/darkpatterns/analysis/dp/bin/activate && \
  python preprocessing.py $1 segments.dataframe && \
  python feature_transformation.py segments.dataframe features.npy segments_feature.dataframe && \
  python clustering.py features.npy segments_feature.dataframe segments_cluster.dataframe && \
  python visualize.py segments_cluster.dataframe clusters.csv
