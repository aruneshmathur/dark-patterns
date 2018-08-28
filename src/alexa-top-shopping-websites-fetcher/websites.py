from alexa.request import Request
import pandas as pd
import sys

def get_rank(request, url):

    query = {'ResponseGroup': 'UsageStats',
             'Action': 'UrlInfo',
             'Url': url}

    return str(request.rank(query))


if __name__ == '__main__':

    query = {'ResponseGroup': 'Listings',
             'Action': 'CategoryListings',
             'SortBy': 'Popularity',
             'Recursive': 'True',
             'Count': 20 }

    access_key = sys.argv[1]
    secret_key = sys.argv[2]

    request = Request(access_key, secret_key)

    dat = pd.read_csv('../../data/alexa-shopping-websites/top-shopping-categories.csv')

    for index, row in dat.iterrows():
        query['Path'] = row['category']
        for count in range(1, row['website_count'], 20):
            query['Start'] = count
            for s in request.sites(query):
                print s[0] + ',' + s[2] + ',' + row['category'] + ',' + get_rank(request, s[0])
