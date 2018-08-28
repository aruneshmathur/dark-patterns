from lxml import etree
from myawis import *
import json, sys

def getCategories(awisAPI, path, depth):

    params = {
        'Action': "CategoryBrowse",
        'Path': path,
        'Descriptions': 'True',
        'ResponseGroup' : 'Categories'
    }

    url, headers = awisAPI.create_v4_signature(params)

    awisAPIResponseContent = awisAPI.return_output(url, headers)

    ret = []

    for category in awisAPIResponseContent.find_all('Category'):
        categories_count = int(category.SubCategoryCount.contents[0])
        sites_count = int(category.TotalListingCount.contents[0])

        if sites_count > 0:
            ret.append({
                'title' : category.Title.contents[0],
                'path' : category.Path.contents[0],
                'categories_count' : categories_count,
                'sites_count' : sites_count,
                'categories' : [] if categories_count == 0 or depth > 2 else getCategories(awisAPI, category.Path.contents[0], depth + 1)
            })

    return ret


if __name__ == '__main__':

    access_key = sys.argv[1]
    secret_key = sys.argv[2]

    awisAPI = CallAwis(access_key, secret_key)

    data = getCategories(awisAPI, 'Top/Shopping', 1)

    print(json.dumps(data))
