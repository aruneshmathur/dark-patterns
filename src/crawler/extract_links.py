import sys
import ipaddress
import io
from time import time, sleep
from selenium import webdriver
from urlparse import urlparse, urljoin
from os.path import join
from tld import get_tld
from collections import deque


OUTFILE = "crawl.log"
ALLOWED_SCHEMES = ["http", "https"]
SCREENSHOTS_DIR = "screenshots"
HTML_DIR = "htmls"


def write_to_file(file_path, txt):
    with io.open(file_path, 'w', encoding='utf-8') as f:
        f.write(txt)


# https://stackoverflow.com/a/7406369
def safe_filename_from_url(url):
    keepcharacters = ('.', '_', '-')
    return "".join(c for c in url if c.isalnum() or c in keepcharacters).rstrip()


def get_tld_or_host(url):
    if not url.startswith("http"):
        url = 'http://' + url

    try:
        return get_tld(url, fail_silently=False)
    except Exception:
        hostname = urlparse(url).hostname
        try:
            ipaddress.ip_address(hostname)
            return hostname
        except Exception:
            return None


class Spider(object):

    def __init__(self, url):
        self.url = url
        self.current_tld = get_tld_or_host(url)
        self.base_filename = safe_filename_from_url(url)
        self.png_file_name = join(SCREENSHOTS_DIR, '%s.png' % self.base_filename)
        self.page_src_file_name = join(HTML_DIR, '%s.html' % self.base_filename)
        self.driver = webdriver.Firefox()

    def sanitize_url(self, href, current_url):
        href = href.strip()
        if not href or (href == "/"):
            return None
        parsed_current_url = urlparse(current_url)
        current_scheme = parsed_current_url.scheme
        current_netloc = parsed_current_url.netloc
        parsed_url = urlparse(href)
        if parsed_url.scheme in ALLOWED_SCHEMES:
            # href = href.replace(parsed_url.scheme + "://", "", 1)
            pass
        elif not parsed_url.netloc and not parsed_url.scheme:  # relative URLs
            print "RELRELRELRELRELRELRELREL", href
            href = urljoin("%s://%s" % (current_scheme, current_netloc), href)
        elif href.startswith("//"):  # Protocol-relative URL
            href = "%s:%s" (current_scheme, href)
        else:
            if parsed_url.scheme not in ["javascript", "mailto", "tel"]:
                print "NOT adding", href, current_url  # debug
            return None
        href = href.replace("\r", "").replace("\n", "").replace("\t", "")
        tld = get_tld_or_host(href)
        if tld != self.current_tld:  # dont' add external links
            return None
        return href

    def extract_links(self):
        links = set()
        driver = self.driver
        driver.get(self.url)
        sleep(1)
        current_url = driver.current_url
        page_links = driver.find_elements_by_xpath("//a[@href]")
        for page_link in page_links:
            try:
                href = page_link.get_attribute("href")
                link_url = self.sanitize_url(href, current_url)
                if link_url is None:
                    continue
                links.add(link_url)
            except Exception as e:
                print "Exception:", e

        driver.get_screenshot_as_file(self.png_file_name)
        write_to_file(self.page_src_file_name, driver.page_source)
        driver.close()
        print "Num. links", len(links)
        with open(OUTFILE, "a") as f_out:
            for link in links:
                f_out.write("%s - %s\n" % (self.url, link))
                print self.url, link

        return links


# https://stackoverflow.com/a/48149461
def crawl(url, max_level=2):
    # TODO
    queue = deque([url])
    level = 0

    while queue and level < max_level:
        urls = queue.popleft()
        print "$$$$$$$$$4", urls
        for _url in urls:
            spider = Spider(url)
            links = spider.extract_links()
            queue.append(links)
            level += 1


def main(csv_file):
    # f_out.truncate(0)
    for line in open(csv_file):
        line = line.rstrip()
        items = line.split(",")
        if items[-1] == "overall_rank":
            continue
        domain = items[0]
        if not domain.startswith("http"):
            url = "http://" + domain
        else:
            url = domain
        crawl(url, max_level=2)
        # spider = Spider(url)
        # links = spider.extract_links()
        ss
    print "Finished in %0.1f mins" % ((time() - t0) / 60)


if __name__ == '__main__':
    t0 = time()
    main(sys.argv[1])
