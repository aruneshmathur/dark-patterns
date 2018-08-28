#!/usr/bin/python

import requests
import sys
from base64 import urlsafe_b64encode
import pandas as pd

# Arguments: List of website urls
website_file = sys.argv[1]

# Key to Web Shrinker
key = sys.argv[2]

# Secret Key to Web Shrinker
secret_key = sys.argv[3]

def get_categories(target_website, key, secret_key):
    api_url = 'https://api.webshrinker.com/categories/v3/%s?taxonomy=webshrinker' % urlsafe_b64encode(target_website).decode('utf-8')

    response = requests.get(api_url, auth=(key, secret_key))
    status_code = response.status_code
    data = response.json()

    if status_code == 200:
        category_data = data['data'][0]['categories']
        
        for cat in category_data:
            print target_website + ',' + cat['label']

    elif status_code == 202:
        print target_website + ',' + 'none'

    else:
        print target_website + ',' + 'error'


if __name__ == '__main__':

    website_file = sys.argv[1]
    key = sys.argv[2]
    secret_key = sys.argv[3]
   
    data = pd.read_csv(website_file)

    print 'url' + ',' + 'category'
    for index, row in data.iterrows():
        get_categories(row['url'], key, secret_key)
