from lxml import etree
from myawis import *
import json, sys, os

if __name__ == '__main__':

    categories = json.loads(open('../../data/alexa-shopping-websites/top-shopping-categories.json').read())

    for cat in categories:
        print cat['path'] + ',' + str(cat['sites_count'])
