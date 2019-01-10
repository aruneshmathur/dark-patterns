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
import spacy

LOG_FILE_NAME = 'feature_transformation.log'

try:
    os.remove(LOG_FILE_NAME)
    os.remove('features.npy')
    os.remove('segments_feature.dataframe')
except:
    pass

logger = logging.getLogger(__name__)
lf_handler = logging.FileHandler(LOG_FILE_NAME)
lf_format = logging.Formatter('%(asctime)s - %(message)s')
lf_handler.setFormatter(lf_format)
logger.addHandler(lf_handler)
logger.setLevel(logging.INFO)

stemmer = PorterStemmer()
stopwords = nltk.corpus.stopwords.words('english')

def tokenize(line):
    if (line is None):
        line = ''
    tokens = [stemmer.stem(t) for t in nltk.word_tokenize(line) if len(t) != 0 and t not in stopwords and not t.isdigit()]
    return tokens


def get_count_features(column, binary_rep):
    logger.info('Using CountVectorizer with binary=%s' % str(binary_rep))
    vec = CountVectorizer(tokenizer=tokenize, binary=binary_rep, strip_accents='ascii').fit(column)
    logger.info('Length of vocabulary %s' % str(len(vec.vocabulary_)))
    vec = vec.transform(column)
    return normalize(vec, axis=0)


def get_tfidf_features(column, binary_rep):
    logger.info('Using TfidfVectorizer with binary=%s' % str(binary_rep))
    vec = TfidfVectorizer(tokenizer=tokenize, binary=binary_rep, strip_accents='ascii').fit(column)
    logger.info('Length of vocabulary %s' % str(len(vec.vocabulary_)))
    return vec.transform(column)


def get_word_vector_features(column):
    nlp = spacy.load('en_core_web_lg')
    vecs = []

    logger.info('Using word vectors')
    for doc in nlp.pipe(column.str.replace(r'\d+', '').astype('unicode').values, batch_size=10000, n_threads=7):
        if doc.is_parsed:
            vecs.append(doc.vector)
        else:
            vecs.append(None)

    return np.array(vecs)


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
        segments = segments.groupby(['domain']).apply(lambda x: x.drop_duplicates(subset=['inner_text_processed'], keep='last'))
        logger.info('Done')

        logger.info('Number of segments: %s' % str(segments.shape))
        logger.info('segments columns: %s' % str(list(segments.columns.values)))

        logger.info('Creating the feature representation ...')
        #features = get_count_features(segments['inner_text'], True)
        features = get_count_features(segments['inner_text'], False)
        #features = get_tfidf_features(segments['inner_text'], True)
        #features = get_tfidf_features(segments['inner_text'], False)
        #features = get_word_vector_features(segments['inner_text'])
        logger.info('Done')

        logger.info('Number of features: %s' % str(features.shape))

        logger.info('Pickling features ...')

        if (sparse.issparse(features)):
            features = features.toarray()

        np.save('features', features)

        logger.info('Done')

        logger.info('Pickling feature processed segments ...')
        segments.to_pickle('segments_feature.dataframe')
        logger.info('Done')

    except:
        logger.exception('Exception')
