from __future__ import division
import os
import sys
import random
import ipaddress
import io
import json
import math
from time import time, sleep
from selenium import webdriver
from urlparse import urlparse, urljoin
from os.path import join, isdir
from tld import get_tld
from pyvirtualdisplay import Display
from numpy.random import choice
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from multiprocessing import Pool


ENABLE_XVFB = True

OUTFILE = "crawl.log"
ALLOWED_SCHEMES = ["http", "https"]


def dump_as_json(obj, json_path):
    with open(json_path, 'w') as f:
        json.dump(obj, f, indent=2)


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


def move_to_element(driver, element):
    try:
        ActionChains(driver).move_to_element(element).perform()
    except WebDriverException:
        pass


class Spider(object):

    def __init__(self, top_url, max_level=5, max_links=50):
        self.top_url = top_url
        self.max_level = max_level
        self.max_links = max_links
        self.observed_links = {}  # page-> link
        self.visited_links = {}  # page-> link
        self.current_tld = get_tld_or_host(top_url)
        self.base_filename = safe_filename_from_url(top_url)
        self.png_file_name = join(self.base_filename, 'PAGE_NO_URL.png')
        self.page_src_file_name = join(self.base_filename, 'PAGE_NO_URL.html')
        self.links_json_file_name = join(self.base_filename, 'links_%s.json' % self.base_filename)
        self.visited_links_json_file_name = join(self.base_filename, 'visited_links_%s.json' % self.base_filename)
        self.make_site_dir()
        if ENABLE_XVFB:
            self.display = Display(visible=0, size=(1200, 1920))  # 24" vertical
            self.display.start()
        self.driver = webdriver.Firefox()

    def __del__(self):
        if ENABLE_XVFB:
            self.display.stop()
        self.driver.close()

    def make_site_dir(self):
        if not isdir(self.base_filename):
            os.makedirs(self.base_filename)

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
            print "Relative URL", href
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

    def visit_random_link(self, links, link_areas):
        AREA_WEIGHTED_CHOICE = True
        HOVER_BEFORE_CLICKING = True
        CLICK_LINKS = False
        tried_links = set()
        link_urls = links.keys()
        max_area_sqrt = math.sqrt(max(link_areas.values()))
        link_probabilities = [math.sqrt(link_areas[link_url]) / max_area_sqrt
                              for link_url in link_urls]
        print sum(link_probabilities)
        link_probabilities = [probability / sum(link_probabilities)
                              for probability in link_probabilities]
        while len(tried_links) < len(links):
            if AREA_WEIGHTED_CHOICE:
                link_url = choice(link_urls, p=link_probabilities)
            else:
                link_url = random.choice(links.keys())
            tried_links.add(link_url)
            try:
                link_element = links[link_url]
                self.driver.execute_script("arguments[0].scrollIntoView();",
                                           link_element)
                if HOVER_BEFORE_CLICKING:
                    move_to_element(self.driver, link_element)
                if CLICK_LINKS:
                    link_element.click()
                else:
                    self.driver.get(link_url)
            except Exception as e:
                print "Exception while clicking link", link_url, e
            else:
                print "Clicked on", link_url
                return link_url
        return None

    def spider_site(self):
        num_visited_pages = 0
        first_visit = True
        while num_visited_pages < self.max_links:
            print "Will visit", self.top_url
            try:
                self.driver.get(self.top_url)
            except WebDriverException as e:
                print "Error while loading the home page", self.top_url, e
                return
            sleep(3)
            links, link_areas = self.extract_links(0, num_visited_pages, first_visit)
            if not links:
                print "Cannot find any links on the home page", self.driver.current_url
                return
            self.observed_links[self.top_url] = links.keys()
            first_visit = False
            for level in xrange(1, self.max_level+1):
                navigated_link = self.visit_random_link(links, link_areas)
                if navigated_link is None:
                    print "Can't find any links to click on this page", self.driver.current_url
                    break
                sleep(3)
                num_visited_pages += 1
                self.visited_links[num_visited_pages] = navigated_link
                print "Navigated to", navigated_link, "link %s of %s" % (num_visited_pages, self.max_links)
                links, link_areas = self.extract_links(level, num_visited_pages, True)
                if not links:
                    break
                self.observed_links[navigated_link] = links.keys()
        dump_as_json(self.observed_links, self.links_json_file_name)
        dump_as_json(self.visited_links, self.visited_links_json_file_name)

    def dump_page_data(self, link_no, current_url):
        driver = self.driver
        safe_url = safe_filename_from_url(current_url)
        png_file_name = self.png_file_name.replace(
            "PAGE_NO", str(link_no)).replace("URL", safe_url)
        driver.get_screenshot_as_file(png_file_name)
        page_src_file_name = self.page_src_file_name.replace(
            "PAGE_NO", str(link_no)).replace("URL", safe_url)
        write_to_file(page_src_file_name, driver.page_source)

    def get_element_area(self, element):
        try:
            dimensions = element.size
            return dimensions["width"] * dimensions["height"]
        except Exception:
            return 0

    def extract_links(self, level, link_no, dump_page_data=True):
        links = {}
        link_areas = {}
        driver = self.driver
        # TODO: make sure we are still on the same domain
        current_url = driver.current_url
        print "Level: %s, URL: %s" % (current_url, level)
        link_elements = driver.find_elements_by_xpath("//a[@href]")
        for link_element in link_elements:
            try:
                href = link_element.get_attribute("href")
                if href == self.top_url or href == current_url:
                    continue
                if ".jpg" in href or ".jpeg" in href:  # avoid image links
                    continue
                link_url = self.sanitize_url(href, current_url)
                if link_url is None:
                    continue
                # links.add(link_url)
                links[link_url] = link_element
                link_areas[link_url] = self.get_element_area(link_element)
            except Exception as e:
                print "Exception:", e
        if dump_page_data:
            self.dump_page_data(link_no, current_url)
        return links, link_areas


# https://stackoverflow.com/a/48149461
def crawl(url, max_level=5, max_links=200):
    spider = Spider(url, max_level, max_links)
    try:
        spider.spider_site()
    except Exception as e:
        print "Error while spidering", url, e


def main(csv_file):
    p = Pool(10)
    shop_urls = []
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
        shop_urls.append(url)
        # crawl(url, 5, 50)
    p.map(crawl, shop_urls)
    print "Finished in %0.1f mins" % ((time() - t0) / 60)


if __name__ == '__main__':
    t0 = time()
    main(sys.argv[1])
