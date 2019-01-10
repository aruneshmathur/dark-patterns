import sys
import logging
import os
import sqlite3
import pandas as pd
from urlparse import urlparse

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

if __name__ == '__main__':
    try:
        db = sys.argv[1]
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

        logger.info('Pickling site_visits ...')
        site_visits.to_pickle('site_visits.dataframe')
        logger.info('Done')

        logger.info('Pickling segments ...')
        segments.to_pickle('segments.dataframe')
        logger.info('Done')

    except:
        logger.exception('Exception')
