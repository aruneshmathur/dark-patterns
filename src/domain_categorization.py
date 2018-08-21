# from __future__ import print_function
import json
import sys
import subprocess
import requests
from time import sleep
from os.path import isfile
from _collections import defaultdict


OUTFILE = "../data/bluecoat/alexa_shopping_bluecoat.csv"


class DomainInfo(object):
    def __init__(self):
        self.baseurl = "http://sitereview.bluecoat.com/resource/lookup"
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/67.0.3396.99 Chrome/67.0.3396.99 Safari/537.36",
                        "Content-Type": "application/json"}

    def get_category(self, url):
        category_list = []
        if not url.startswith("http"):
            url = "http://" + url

        print "Will query %s" % url
        payload = {"url": url, "captcha": ""}

        try:
            self.response = requests.post(
                self.baseurl,
                headers=self.headers,
                data=json.dumps(payload),
            )
        except requests.ConnectionError:
            print("[-] ConnectionError: "
                  "A connection error occurred")
            return "ConnectionError"

        if self.response.status_code != 200:
            print("[-] HTTP {} returned".format(self.response.status_code))
        else:
            try:
                response_content = json.loads(self.response.
                                              content.decode("UTF-8"))
                # url = response_content["url"]
                categories = response_content["categorization"]
                for idx in xrange(len(categories)):
                    category_list.append(categories[idx]["name"])
                    # print category_list
                return ",".join(category_list)
            except Exception as e:
                print "Exception:", e
                return "DecodingError"


def read_known_cats():
    domain_cats = defaultdict(set)
    if not isfile(OUTFILE):
        return {}
    for l in open(OUTFILE):
        items = l.rstrip().split(",")
        domain = items[0]
        domain_cats[domain] = items[1:]
    return domain_cats


def main(csv_file):
    known_sites = read_known_cats()
    d = DomainInfo()
    cnt = 0
    with open(OUTFILE, "a") as f_out:
        # f_out.truncate(0)
        for line in open(csv_file):
            line = line.rstrip()
            items = line.split(",")
            if items[-1] == "overall_rank":
                continue
            domain = items[0]
            if domain in known_sites:
                print domain, "is already known, will skip"
                continue
            category = d.get_category(domain)
            cnt += 1
            print cnt, domain, category
            if category is None:  # captcha
                subprocess.Popen(['chromium-browser', 'http://sitereview.bluecoat.com/lookup'])
                sleep(30)
                continue
            f_out.write("%s,%s\n" % (domain, category))
            sleep(5)


if __name__ == "__main__":
    main(sys.argv[1])
