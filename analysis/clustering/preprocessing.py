from common import *
import logging
import nltk
from nltk.stem.porter import PorterStemmer
import numpy as np
import os
import pandas as pd
from scipy.sparse import hstack
from scipy import sparse
from sklearn.decomposition import PCA
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

stemmer = PorterStemmer()
stopwords = nltk.corpus.stopwords.words('english')

def tokenize(line):
    if (line is None):
        line = ''
    tokens = [stemmer.stem(t) for t in nltk.word_tokenize(line) if len(t) != 0 and t not in stopwords and not t.isdigit()]
    return tokens

def get_count_features(column, binary_rep):
    debug('Using CountVectorizer with binary=%s' % str(binary_rep))
    vec = CountVectorizer(tokenizer=tokenize, binary=binary_rep, strip_accents='ascii').fit(column)
    debug('Length of vocabulary %s' % str(len(vec.vocabulary_)))
    vec = vec.transform(column)
    return normalize(vec, axis=0)

def get_tfidf_features(column, binary_rep):
    debug('Using TfidfVectorizer with binary=%s' % str(binary_rep))
    vec = TfidfVectorizer(tokenizer=tokenize, binary=binary_rep, strip_accents='ascii').fit(column)
    debug('Length of vocabulary %s' % str(len(vec.vocabulary_)))
    return vec.transform(column)

def get_word_vector_features(column):
    nlp = spacy.load('en_core_web_lg')
    vecs = []

    debug('Using word vectors')
    for doc in nlp.pipe(column.str.replace(r'\d+', '').astype('unicode').values, batch_size=10000, n_threads=7):
        if doc.is_parsed:
            vecs.append(doc.vector)
        else:
            vecs.append(None)

    return np.array(vecs)

# Project the data matrix with examples in columns (`X`) into a lower
# dimensional space. Number of dimensions can be specified by one of the
# optional parameters, listed in order of priority: ndims (number of dimensions
# to reduce to), or svthresh (keep all singular values above this minimum
# threshold).
def pca(X, ndims=None, svthresh=None):
    if ndims is not None:
        debug('Reducing data to %d dimensions via PCA...' % ndims)
        p = PCA(n_components=ndims)
        p.fit(X)
    elif svthresh is not None:
        debug('Reducing dimension via PCA using svthresh %e...' % svthresh)
        p = PCA(tol=svthresh)
        p.fit(X)
    else:
        debug('error in pca: must set one of ndims or svthresh')
        raise Exception()
    debug('Matrix of PCs: %s' % str(p.components_.shape))
    debug('Data matrix: %s' % str(X.shape))

    # Projected data is given by U^T * X, where U is matrix with PCs in cols
    X_proj = p.components_.dot(X)
    debug('Done')
    return X_proj

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
        debug('Reading site_visits ...')
        site_visits = pd.read_sql_query('''SELECT * from site_visits''', con)
        debug('Done')

        debug('Number of site visits: %s' % str(site_visits.shape))
        debug('site_visits columns: %s' % str(list(site_visits.columns.values)))

        debug('Extracting domains from site visits ...')
        site_visits['domain'] = site_visits['site_url'].apply(lambda x: urlparse(x).netloc)
        grouped = site_visits.groupby(['domain']).count().sort_values('visit_id', ascending=False)
        debug('Done')

        debug('Number of unique domains: %s' % str(grouped.shape[0]))

        # TODO: Analyzing product interaction

        # TODO: Analyzing add-to-cart flows

        # Analyzing segments
        debug('Reading segments ...')
        segments = pd.read_sql_query('''SELECT * from segments''', con)
        debug('Done')

        debug('Number of segments: %s' % str(segments.shape))
        debug('segments columns: %s' % str(list(segments.columns.values)))

        debug('Joining segments and site_visits ...')
        segments = segments.reset_index().set_index('visit_id').join(site_visits.reset_index()[['visit_id', 'site_url', 'domain']].set_index('visit_id'), how='inner')
        debug('Done')

        debug('Number of segments: %s' % str(segments.shape))
        debug('segments columns: %s' % str(list(segments.columns.values)))

        debug('Ignore <body> tags and those with inner_text null ...')
        segments['inner_text'] = segments['inner_text'].str.strip()
        segments = segments[(segments['node_name'] != 'BODY') & (segments['inner_text'] != '')]
        debug('Done')

        debug('Number of segments: %s' % str(segments.shape))

        segments['newline_count'] = segments['inner_text'].apply(lambda x: len(x.split('\n')))
        segments['inner_text_length'] = segments['inner_text'].apply(lambda x: len(x))

        debug('segments[\'newline_count\'].describe(): \n %s' % segments['newline_count'].describe().to_string())
        debug('segments[\'inner_text_length\'].describe(): \n %s' % segments['inner_text_length'].describe().to_string())
    except Exception, e:
        debug('Exception: %s' % str(e))

    # Create feature vectors from data
    try:
        debug('Replacing numbers with DPNUM placeholder ...')
        segments['inner_text_processed'] = segments['inner_text'].str.replace(r'\d+', 'DPNUM')
        segments['longest_text_processed']= segments['longest_text'].str.replace(r'\d+', 'DPNUM')
        debug('Done')

        debug('Removing redundant nodes ...')
        segments = segments.groupby(['domain']).apply(lambda x: x.drop_duplicates(subset=['inner_text_processed'], keep='last'))
        debug('Done')

        debug('Number of segments: %s' % str(segments.shape))
        debug('segments columns: %s' % str(list(segments.columns.values)))

        debug('Creating the feature representation ...')
        #features = get_count_features(segments['inner_text'], True)
        features = get_count_features(segments['inner_text_processed'], False)
        #features = get_tfidf_features(segments['inner_text'], True)
        #features = get_tfidf_features(segments['inner_text'], False)
        #features = get_word_vector_features(segments['inner_text'])
        debug('feature matrix shape: %s' % str(features.shape))
        features = pca(features, svthresh=1e-5)
        debug('feature matrix shape (after PCA): %s' % str(features.shape))
        debug('Done')

        debug('Pickling features ...')
        if (sparse.issparse(features)):
            features = features.toarray()
        np.save(features_outfile, features)
        debug('Done')

        debug('Pickling feature processed segments ...')
        segments.to_pickle(segments_outfile)
        debug('Done')
    except Exception, e:
        debug('Exception: %s' % str(e))
