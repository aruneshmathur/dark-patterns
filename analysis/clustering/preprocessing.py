import logging
import nltk
from nltk.stem.porter import PorterStemmer
import numpy as np
import os
import pandas as pd
from scipy.sparse import hstack
from scipy import sparse
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import normalize
import spacy
import sqlite3
import sys
from urlparse import urlparse

usage = 'python %s DB FT-OUTFILE SEGMENTS-OUTFILE' % __file__
help_message = '''Computes feature vectors from the segment data read from the DB.
Produces an array of feature vectors to FT-OUTFILE, and a new segments dataframe written
to SEGMENTS-OUTFILE.'''
LOG_FILE_NAME = 'preprocessing.log'

try:
    os.remove(LOG_FILE_NAME)
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
    # Check args
    if len(sys.argv[1:]) != 3:
        print usage
        print ''
        print help_message
        exit(1)
    db = sys.argv[1]
    features_outfile = sys.argv[2]
    segments_outfile = sys.argv[3]

    # Read segment data from database
    try:
        con = sqlite3.connect(db)

        # Analyzing websites visited
        logger.info('Reading site_visits ...')
        site_visits = pd.read_sql_query('''SELECT * from site_visits''', con)
        logger.info('Done')

        logger.info('Number of site visits: %s' % str(site_visits.shape))
        logger.info('site_visits columns: %s' % str(list(site_visits.columns.values)))

        logger.info('Extracting domains from site visits ...')
        site_visits['domain'] = site_visits['site_url'].apply(lambda x: urlparse(x).netloc)
        grouped = site_visits.groupby(['domain']).count().sort_values('visit_id', ascending=False)
        logger.info('Done')

        logger.info('Number of unique domains: %s' % str(grouped.shape[0]))

        # TODO: Analyzing product interaction

        # TODO: Analyzing add-to-cart flows

        # Analyzing segments
        logger.info('Reading segments ...')
        segments = pd.read_sql_query('''SELECT * from segments''', con)
        logger.info('Done')

        logger.info('Number of segments: %s' % str(segments.shape))
        logger.info('segments columns: %s' % str(list(segments.columns.values)))

        logger.info('Joining segments and site_visits ...')
        segments = segments.reset_index().set_index('visit_id').join(site_visits.reset_index()[['visit_id', 'site_url', 'domain']].set_index('visit_id'), how='inner')
        logger.info('Done')

        logger.info('Number of segments: %s' % str(segments.shape))
        logger.info('segments columns: %s' % str(list(segments.columns.values)))

        logger.info('Ignore <body> tags and those with inner_text null ...')
        segments['inner_text'] = segments['inner_text'].str.strip()
        segments = segments[(segments['node_name'] != 'BODY') & (segments['inner_text'] != '')]
        logger.info('Done')

        logger.info('Number of segments: %s' % str(segments.shape))

        segments['newline_count'] = segments['inner_text'].apply(lambda x: len(x.split('\n')))
        segments['inner_text_length'] = segments['inner_text'].apply(lambda x: len(x))

        logger.info('segments[\'newline_count\'].describe(): \n %s' % segments['newline_count'].describe().to_string())
        logger.info('segments[\'inner_text_length\'].describe(): \n %s' % segments['inner_text_length'].describe().to_string())
    except:
        logger.exception('Exception')

    # Create feature vectors from data
    try:
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

        np.save(features_outfile, features)

        logger.info('Done')

        logger.info('Pickling feature processed segments ...')
        segments.to_pickle(segments_outfile)
        logger.info('Done')
    except:
        logger.exception('Exception')
