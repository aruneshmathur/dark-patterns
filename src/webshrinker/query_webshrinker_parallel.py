#!/usr/bin/python

import requests
import sys
from base64 import urlsafe_b64encode
import pandas as pd
from itertools import izip_longest
import multiprocessing as mp
from functools import partial

def grouper(n, iterable, fillvalue = None):
  args = [iter(iterable)] * n
  return izip_longest(fillvalue = fillvalue, *args)


def get_categories_websites(key, secret_key, websites):
    result = []
    for website in websites:

        if website is not None:
            categories = get_categories(website, key, secret_key)
            
            for cat in categories:
                print website + ',' + cat


def get_categories(target_website, key, secret_key):
    api_url = 'https://api.webshrinker.com/categories/v3/%s?taxonomy=webshrinker' % urlsafe_b64encode(target_website).decode('utf-8')

    response = requests.get(api_url, auth=(key, secret_key))
    status_code = response.status_code
    data = response.json()

    result = []

    if status_code == 200:
        category_data = data['data'][0]['categories']
        
        for cat in category_data:
            result.append(cat['label'])

    elif status_code == 202:
        result.append('None')

    else:
        result.append('Error')

    return result


if __name__ == '__main__':

    website_file = sys.argv[1]
    key = sys.argv[2]
    secret_key = sys.argv[3]
   
    data = pd.read_csv(website_file)

    urls = data['url'].tolist()

    urls_chunks = grouper(10000, urls)
    urls_chunks_list = []

    for us in urls_chunks:
        urls_chunks_list.append(us) 

    print 'url,category'

    pool = mp.Pool(processes=10)
   
    func = partial(get_categories_websites, key, secret_key)

    pool.map(func, urls_chunks_list)
