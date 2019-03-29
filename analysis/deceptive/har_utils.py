import binascii
import json
from glob import glob
from haralyzer import HarParser
from collections import defaultdict, Counter
from urlparse import urlparse
from os.path import join


def get_response_contents_from_har(har_path):
    response_contents = defaultdict(str)
    with open(har_path, 'r') as f:
        try:
            har_parser = HarParser(json.loads(f.read()))
        except ValueError:
            return response_contents
        for page in har_parser.pages:
            for entry in page.entries:
                try:
                    url = entry["request"]["url"]
                    base_url = url.split("?")[0].split("#")[0]
                    mime_type = entry["response"]["content"]["mimeType"]
                    if "image" in mime_type or "font" in mime_type or \
                            "css" in mime_type:
                        continue
                    # print mime_type
                    body = entry["response"]["content"]["text"]
                    # print url, body[:128]
                    # response_contents.append((url, body))
                    response_contents[base_url] += ("\n======\n" + body)
                except Exception:
                    pass
    return response_contents


def get_response_contents_from_hars(har_dir):
    har_dir_response_contents = defaultdict(str)
    for har_path in glob(har_dir + "/*.har"):
        response_contents = get_response_contents_from_har(har_path)
        for base_url, content in response_contents.iteritems():
            har_dir_response_contents[base_url] += ("\n======\n" + content)

    return har_dir_response_contents


def search_keywords_in_har_files(page_url, keywords):
    hit_counts = Counter()
    har_dir = get_output_dir_path_from_url(page_url)
    har_dir_response_contents = get_response_contents_from_hars(har_dir)
    for url, content in har_dir_response_contents.iteritems():
        content_lower = content.lower()
        for keyword in keywords:
            if keyword in content_lower:
                # print "found", keyword, url
                hit_counts[url] += 1
    top_hit = hit_counts.most_common(1)
    if not len(top_hit):
        return "", "", ""
    base_url = top_hit[0][0]
    hit_count = top_hit[0][1]
    hit_content = har_dir_response_contents[url]
    return base_url, hit_count, hit_content


def get_output_dir_path_from_url(url):
    hostname = urlparse(url).hostname
    social_proof_root_dir = "../../data/monitoring/social_proof_monitoring_crawl/output/"
    checksum = hex(binascii.crc32(url)).split('x')[-1]
    return join(social_proof_root_dir, "%s_%s" % (hostname, checksum))


if __name__ == '__main__':
    page_url = "https://knockaround.com/collections/best-selling-sunglasses/products/matte-black-on-black-smoke-premiums"
    base_url, hit_count, hit_content = search_keywords_in_har_files(
        page_url, [u'londonderry', u'arcanum', u'helena', u'scott', u'lauren',
                   u'glen', u'venice', u'matthew', u'rose', u'josh',
                   u'minnesota', u'burlington', u'maryland', u'texas',
                   u'carolina', u'dan', u'lemoore', u'dothan', u'jacksonville',
                   u'harbor', u'james', u'ryan', u'bay', u'whitefish',
                   u'cutler', u'ohio', u'navarre', u'force', u'jennifer',
                   u'portland', u'matt', u'chicago', u'daniel', u'benjamin',
                   u'wisconsin', u'base', u'california', u'york', u'santa',
                   u'league', u'central', u'coram', u'florida', u'angeles',
                   u'south', u'washington', u'rosa', u'city', u'ian', u'west',
                   u'jarrettsville', u'gig', u'los', u'dewy', u'john',
                   u'north', u'inverness', u'oregon', u'riverside', u'georgia',
                   u'ellyn', u'air', u'dane', u'waunakee', u'charlotte',
                   u'wappingers', u'san', u'kingston', u'minneapolis',
                   u'diego', u'hampshire', u'illinois', u'brian', u'vancouver',
                   u'chester', u'raymond', u'kansas', u'falls', u'montana',
                   u'chaska', u'pennsylvania', u'baird', u'adam', u'brendan',
                   u'alabama'])
    print base_url, hit_count, "\n==============\n", hit_content[:128]
