from __future__ import division
import sys
import json
import sqlite3
from tld import get_fld
from urlparse import urlparse
import ipaddress
from time import time
from os.path import join, basename, dirname
from collections import defaultdict
from tqdm import tqdm


def get_tld_or_host(url):
    try:
        return get_fld(url, fail_silently=False)
    except Exception:
        hostname = urlparse(url).hostname
        try:
            ipaddress.ip_address(hostname)
            return hostname
        except Exception:
            return None

def get_base_url(url):
    return url.split('://')[-1].split("?")[0].split("#")[0]

def is_third_party(req_url, top_level_url):
    # TODO: when we have missing information we return False
    # meaning we think this is a first-party
    # let's make sure this doesn't have any strange side effects
    # We can also try returning `unknown`.
    if not top_level_url:
        return (None, "", "")

    site_ps1 = get_tld_or_host(top_level_url)
    if site_ps1 is None:
        return (None, "", "")

    req_ps1 = get_tld_or_host(req_url)
    if req_ps1 is None:
        return (None, "", site_ps1)
    if (req_ps1 == site_ps1):
        return (False, req_ps1, site_ps1)

    return (True, req_ps1, site_ps1)


def dump_as_json(obj, json_path):
    with open(json_path, 'w') as f:
        json.dump(obj, f)


def dump_tp_to_publisher_mapping(db_path, out_dir=""):
    crawl_name = basename(db_path).replace(".sqlite", "")
    if not out_dir:
        out_dir = dirname(db_path)
    print("Will process %s " % db_path)
    processed = 0
    tp_to_publishers = defaultdict(set)
    publisher_to_tps = defaultdict(set)
    publisher_to_base_urls = defaultdict(set)
    db_conn = sqlite3.connect(db_path)
    db_conn.row_factory = sqlite3.Row
    query = """SELECT sv.visit_id, sv.site_url, r.url, r.top_level_url
                FROM http_requests as r LEFT JOIN site_visits as sv
                ON sv.visit_id = r.visit_id"""
    for row in tqdm(db_conn.execute(query)):
        processed += 1
        site_url = row["site_url"]
        # use top_level_url, otherwise fall back to top_url
        top_url = row["top_level_url"]
        if not top_url:
            # print "Warning, missing top_url", row
            continue
        is_tp, req_ps1, _ = is_third_party(row["url"], top_url)
        if is_tp:
            tp_to_publishers[req_ps1].add(site_url)
            publisher_to_tps[site_url].add(req_ps1)
            publisher_to_base_urls[site_url].add(get_base_url(row["url"]))

    print("Will write output files to %s " % out_dir)
    tp_to_publishers = {tp: "\t".join(publishers)
                        for (tp, publishers) in tp_to_publishers.iteritems()}
    dump_as_json(tp_to_publishers, join(
        out_dir, "%s_tp_to_publishers.json" % crawl_name))

    publisher_to_tps = {publisher: "\t".join(tps)
                        for (publisher, tps) in publisher_to_tps.iteritems()}
    dump_as_json(publisher_to_tps, join(
        out_dir, "%s_publishers_to_tps.json" % crawl_name))

    publisher_to_base_urls = {publisher: "\t".join(tps)
                              for (publisher, tps) in publisher_to_base_urls.iteritems()}
    dump_as_json(publisher_to_tps, join(
        out_dir, "%s_publishers_to_base_urls.json" % crawl_name))



if __name__ == '__main__':
    t0 = time()
    dump_tp_to_publisher_mapping(sys.argv[1])
    print "Analysis finished in %0.1f mins" % ((time() - t0) / 60)
