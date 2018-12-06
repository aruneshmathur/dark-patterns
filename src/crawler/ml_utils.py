import os
import pickle
import re
from sklearn.preprocessing import StandardScaler
from urlparse import urlparse


PATH_LEN_CAP=100
MIN_PROD_ID_LEN = 3
MAX_PROD_ID_LEN = 32


def has_product_id(path):
    if not re.search(r'\d', path):
        return 0
    for num in re.findall(r'[0-9]+', path):
        if len(num) > MIN_PROD_ID_LEN and len(num) < MAX_PROD_ID_LEN:
            return 1
    return 0


def build_features(df, load_scaler_from_file=False):
    processed_features = df[["url"]].copy()
    processed_features["path"] = processed_features["url"].map(
        lambda x: urlparse(x).path + urlparse(x).params + urlparse(x).query + urlparse(x).fragment)
    processed_features["path_len"] = processed_features["path"].map(
        lambda x: min(len(x), PATH_LEN_CAP))
    processed_features["num_hyphen"] = processed_features["path"].map(
        lambda x: x.count("-"))
    processed_features["num_slash"] = processed_features["path"].map(
        lambda x: x.rstrip("/").count("/"))
    processed_features["contains_product"] = processed_features["path"].map(
        lambda x: 1 if "product" in x else 0)
    processed_features["contains_category"] = processed_features["path"].map(
        lambda x: 1 if "category" in x else 0)
    # processed_features["longest_num"] = processed_features["path"].map(lambda x: len(max(re.findall(r'[0-9]+', x), key=len)) if re.search(r'\d', x) else 0)
    processed_features["contains_pid"] = processed_features["path"].map(
        lambda x: has_product_id(x))
    cols_to_drop = ['url', 'path']
    processed_features.drop(cols_to_drop, axis=1, inplace=True)
    scaled_features = processed_features.copy()
    FEATURES_TO_SCALE = ["num_hyphen", "num_slash"]
    features = scaled_features[FEATURES_TO_SCALE]
    scaler_filename = 'StandardScaler.est'
    if load_scaler_from_file and os.path.isfile(scaler_filename):
        scaler = pickle.load(open(scaler_filename, 'rb'))
    else:
        scaler = StandardScaler()
        scaler = StandardScaler().fit(features.values)
        pickle.dump(scaler, open(scaler_filename, 'wb'))

    features = scaler.transform(features.values)
    scaled_features[FEATURES_TO_SCALE] = features
    return scaled_features