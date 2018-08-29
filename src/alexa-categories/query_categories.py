#!/usr/bin/python

# Common API (pyalexa) use
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from pyalexa.request import Request

import pandas as pd
import sys

def get_alexa_categories(request, url):

    query = {'ResponseGroup': 'Categories',
             'Action': 'UrlInfo',
             'Url': url}

    return request.categories(query)


if __name__ == '__main__':

    access_key = sys.argv[1]
    secret_key = sys.argv[2]

    request = Request(access_key, secret_key)

    dat = pd.read_csv('../../data/gold-standard/alexa-top-sites-sample.csv')

    print 'url,category'
    for index, row in dat.iterrows():
        categories = get_alexa_categories(request, row['url'])

        if len(categories) == 0:
            print row['url'] + ',None'

        else:
           for cat in categories:
               print row['url'] + ',' + cat.encode('utf-8').strip()
