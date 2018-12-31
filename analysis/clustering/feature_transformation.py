import pandas as pd
import logging
import os
import nltk
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from sklearn.preprocessing import normalize
from scipy.sparse import hstack
from scipy import sparse
import numpy as np

LOG_FILE_NAME = 'feature_transformation.log'

try:
    os.remove(LOG_FILE_NAME)
    os.remove('features.txt')
except:
    pass

logger = logging.getLogger(__name__)
lf_handler = logging.FileHandler(LOG_FILE_NAME)
lf_format = logging.Formatter('%(asctime)s - %(message)s')
lf_handler.setFormatter(lf_format)
logger.addHandler(lf_handler)
logger.setLevel(logging.INFO)

stemmer = PorterStemmer()

def tokenize(line):
    if (line is None):
        line = ''
    tokens = [stemmer.stem(t) for t in nltk.word_tokenize(line) if len(t) != 0]
    return tokens

if __name__ == '__main__':
    try:
        logger.info('Reading segments ...')
        segments = pd.read_pickle('segments.dataframe')
        logger.info('Done')

        logger.info('Number of segments: %s' % str(segments.shape))
        logger.info('segments columns: %s' % str(list(segments.columns.values)))

        logger.info('Replacing numbers with DPNUM placeholder ...')
        segments['inner_text_processed'] = segments['inner_text'].str.replace(r'\d+', 'DPNUM')
        segments['longest_text_processed']= segments['longest_text'].str.replace(r'\d+', 'DPNUM')
        logger.info('Done')

        logger.info('Removing redundant nodes ...')
        segments = segments.groupby(['visit_id']).apply(lambda x: x.drop_duplicates(subset=['inner_text_processed'], keep='last'))
        logger.info('Done')

        logger.info('Number of segments: %s' % str(segments.shape))
        logger.info('segments columns: %s' % str(list(segments.columns.values)))

        logger.info('Creating the bag of words representation ...')
        countVec = CountVectorizer(tokenizer=tokenize, binary=False, strip_accents='ascii').fit(segments['inner_text_processed'])
        #countVec = CountVectorizer(tokenizer=tokenize, binary=True, strip_accents='ascii').fit(segments['inner_text_processed'])
        #countVec = TfidfVectorizer(tokenizer=tokenize, binary=False, strip_accents='ascii').fit(segments['inner_text_processed'])
        #countVec = TfidfVectorizer(tokenizer=tokenize, binary=True, strip_accents='ascii').fit(segments['inner_text_processed'])
        logger.info('Length of vocabulary %s' % str(len(countVec.vocabulary_)))
        features = countVec.transform(segments['inner_text_processed'])
        logger.info('Done')

        logger.info('Number of features: %s' % str(features.shape))

        logger.info('Adding in the remaining features ...')
        features = hstack((features, np.array(segments['num_buttons'].astype(int).tolist())[:,None]))
        features = hstack((features, np.array(segments['num_imgs'].astype(int).tolist())[:,None]))
        features = hstack((features, np.array(segments['num_anchors'].astype(int).tolist())[:,None]))
        features = hstack((features, np.array(segments['width'].astype(int).tolist())[:,None]))
        features = hstack((features, np.array(segments['height'].astype(int).tolist())[:,None]))
        logger.info('Done')

        logger.info('Number of features: %s' % str(features.shape))

        logger.info('Scaling the features ...')
        features = normalize(features, axis=0)
        logger.info('Done')

        logger.info('Number of features: %s' % str(features.shape))

        logger.info('Pickling features ...')
        sparse.save_npz('features.npz', features)
        logger.info('Done')

        logger.info('Pickling feature processed segments ...')
        segments.to_pickle('segments_feature.dataframe')
        logger.info('Done')

    except:
        logger.exception('Exception')
