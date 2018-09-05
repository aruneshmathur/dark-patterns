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
from tld import get_fld
from pyvirtualdisplay import Display
from numpy.random import choice
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException,\
    NoAlertPresentException
from multiprocessing import Pool
import traceback
from _collections import defaultdict


HOVER_BEFORE_CLICKING = True
DURATION_SLEEP_AFTER_GET = 3  # Sleep 3 seconds after each page load
ENABLE_XVFB = True

OUTDIR = "output"
ALLOWED_SCHEMES = ["http", "https"]

# don't visit links with those words
EXCLUDED_WORDS = ["login", "register", "subscribe", "sign in",
                  "sign up", "add to cart", "checkout", "privacy policy", "contact us",
                  "about us", "help"]


MAX_FILENAME_LEN = 128
MAX_NUM_VISITS_TO_SAME_LINK = 2


def dump_as_json(obj, json_path):
    with open(json_path, 'w') as f:
        json.dump(obj, f, indent=2)


def write_to_file(file_path, txt):
    with io.open(file_path, 'w', encoding='utf-8') as f:
        f.write(txt)


# https://stackoverflow.com/a/7406369
def safe_filename_from_url(url):
    keepcharacters = ('.', '_', '-')
    return "".join(c for c in url if c.isalnum() or
                   c in keepcharacters).rstrip()[:MAX_FILENAME_LEN]


def get_tld_or_host(url):
    if not url.startswith("http"):
        url = 'http://' + url

    try:
        return get_fld(url, fail_silently=False)
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
        self.observed_links = {}  # page url -> links
        self.visited_links = {}  # page number -> link
        self.printed_skipped_urls = set()
        self.blacklisted_links = set()  # links that redirect to other domains etc.
        self.link_visit_counts = defaultdict(int)  # page number -> link
        self.top_url_tld = get_tld_or_host(top_url)  # TLD for the first URL
        self.base_filename = safe_filename_from_url(
            top_url.replace("http://", "").replace("https://", ""))
        self.outdir = join(OUTDIR, self.base_filename)
        self.png_file_name = join(self.outdir, 'PAGE_NO_URL.png')
        self.page_src_file_name = join(self.outdir, 'PAGE_NO_URL.html')
        self.links_json_file_name = join(
            self.outdir, 'links_%s.json' % self.base_filename)
        self.visited_links_json_file_name = join(
            self.outdir, 'visited_links_%s.json' % self.base_filename)
        self.make_site_dir()
        if ENABLE_XVFB:
            self.display = Display(visible=0, size=(1200, 1920))  # 24" vertical
            self.display.start()
        self.driver = webdriver.Firefox()

    def __del__(self):
        if ENABLE_XVFB:
            self.display.stop()
        try:
            self.driver.close()
        except Exception:
            pass

    def make_site_dir(self):
        if not isdir(self.outdir):
            os.makedirs(self.outdir)

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
        if tld != self.top_url_tld:  # dont' add external links
            return None
        return href

    def dismiss_alert(self):
        try:
            self.driver.switch_to.alert.accept()
            print "Dismissed an alert box on", self.driver.current_url
        except NoAlertPresentException:
            pass

    def visit_random_link(self, links, link_areas):
        AREA_WEIGHTED_CHOICE = True
        use_area_weighted_choice = AREA_WEIGHTED_CHOICE
        CLICK_LINKS = False
        tried_links = set()
        link_urls = list(set(links.keys()))

        if not link_urls or not link_areas:
            return None
        max_area_sqrt = math.sqrt(max(link_areas.values()))

        if use_area_weighted_choice:
            try:
                link_probabilities = [
                    math.sqrt(link_areas[link_url]) / max_area_sqrt
                    for link_url in link_urls]
                # probabilities should add up to 1
                link_probability_dist = [probability / sum(link_probabilities)
                                         for probability in link_probabilities]
            except ZeroDivisionError:
                use_area_weighted_choice = False

        num_choices = 0
        while len(tried_links) < len(link_urls) and (num_choices < 100):
            if use_area_weighted_choice:
                link_url = choice(link_urls, p=link_probability_dist)
            else:
                link_url = random.choice(links.keys())
            num_choices += 1
            tried_links.add(link_url)
            # links that redirect to external domains
            if link_url.rstrip("/").lower() in self.blacklisted_links:
                continue
            # if we clicked/visited this link more than the limit
            if self.link_visit_counts[link_url] >= MAX_NUM_VISITS_TO_SAME_LINK:
                # print "Visited this link %s times, will skip: %s on %s" % (
                #    self.link_visit_counts[link_url], link_url, self.driver.current_url)
                continue

            try:
                if CLICK_LINKS:
                    link_element = links[link_url]
                    self.click_to_link(link_element)
                else:
                    self.load_url(link_url)
            except Exception as e:
                print "Exception while following link", link_url, e, self.driver.current_url
            else:
                return link_url
        print "Cannot find any link on", self.driver.current_url
        return None

    def click_to_link(self, link_element):
        if HOVER_BEFORE_CLICKING:
            # scroll to element
            self.driver.execute_script(
                "arguments[0].scrollIntoView();", link_element)
            # Move the mouse to the element
            move_to_element(self.driver, link_element)
        link_element.click()

    def load_url(self, url, stay_on_same_tld=True):
        self.driver.get(url)
        sleep(DURATION_SLEEP_AFTER_GET)
        self.dismiss_alert()
        if stay_on_same_tld:
            tld = get_tld_or_host(self.driver.current_url)
            if tld != self.top_url_tld:
                self.blacklisted_links.add(url.rstrip('/').lower())
                raise WebDriverException("Navigated away from the domain")

    def spider_site(self):
        links = []
        link_areas = []
        MAX_SPIDERING_DURATION = 60*60  # 15 mins
        MAX_WALK_COUNT = 50
        num_visited_pages = 0
        # TODO stop condition
        t_start = time()

        print "Will visit", self.top_url
        try:
            self.load_url(self.top_url)
        except WebDriverException as e:
            print "Error while loading the home page", self.top_url, e, traceback.format_exc()
            return
        home_links, home_link_areas = self.extract_links(0, num_visited_pages)
        if not home_links:
            print "Cannot find any links on the home page", self.driver.current_url
            return
        self.observed_links[self.top_url] = home_links.keys()
        walks_cnt = 0
        while (walks_cnt < MAX_WALK_COUNT and
               num_visited_pages < self.max_links and
               (time() - t_start) < MAX_SPIDERING_DURATION):
            walks_cnt += 1
            for level in xrange(1, self.max_level+1):
                if level == 1:
                    if walks_cnt == 1:
                        home_sales_links, home_sales_link_areas = \
                            self.get_sales_links(home_links, home_link_areas)
                        navigated_link = self.visit_random_link(home_sales_links, home_sales_link_areas)
                    else:
                        navigated_link = self.visit_random_link(home_links, home_link_areas)
                else:
                    navigated_link = self.visit_random_link(links, link_areas)
                current_url = self.driver.current_url
                if navigated_link is None:
                    print "Can't find any links on page", current_url
                    break
                num_visited_pages += 1
                self.visited_links[num_visited_pages] = navigated_link
                self.link_visit_counts[navigated_link] += 1

                # if we are redirected to another page,
                # increment counter for that URL too
                if current_url != navigated_link:
                    self.link_visit_counts[current_url] += 1
                    print ("Link %s of %s. Level %s. Navigated to %s. "
                           "Redirected to: %s" % (
                            num_visited_pages, self.max_links, level,
                            navigated_link, current_url))

                else:
                    print ("Link %s of %s. Level %s. Navigated to %s. " % (
                            num_visited_pages, self.max_links, level, navigated_link))
                # Extract links
                links, link_areas = self.extract_links(level, num_visited_pages)
                if not links:
                    break
                self.observed_links[navigated_link] = links.keys()
        dump_as_json(self.observed_links, self.links_json_file_name)
        dump_as_json(self.visited_links, self.visited_links_json_file_name)
        duration = (time() - t_start) / 60
        print "Finished crawling %s in %0.1f mins" % (self.top_url, duration)

    def get_sales_links(self, home_links, home_link_areas):
        home_sales_links = {}
        home_sales_link_areas = {}
        SALES_KEYWORDS = ["sale", "clearance", "deal", "special",
                          "offer", "outlet", "promotion"]

        for link_url, link_element in home_links.iteritems():
            title = link_element.get_attribute("title") or ""
            alt_text = link_element.get_attribute("alt") or ""
            if any((sales_keyword in link_element.text.lower().split() or
                    sales_keyword in title.lower().split() or
                    sales_keyword in alt_text.lower().split())
                   for sales_keyword in SALES_KEYWORDS):
                print "Sales related link", link_url, "Text:", link_element.text, \
                    "Title:", title, "Alt text:", alt_text
                home_sales_links[link_url] = link_element
                home_sales_link_areas[link_url] = home_link_areas[link_url]
        return home_sales_links, home_sales_link_areas

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

    def extract_links(self, level, link_no):
        links = {}
        link_areas = {}
        driver = self.driver
        current_url = driver.current_url
        # print "Link no %s of %s Level: %s, URL: %s" % (
        #    link_no, self.max_links, level, current_url)
        link_elements = driver.find_elements_by_xpath("//a[@href]")
        for link_element in link_elements:
            try:
                href = link_element.get_attribute("href")
                if href.rstrip("/") == self.top_url.rstrip("/") \
                        or href.rstrip("/") == current_url.rstrip("/"):
                    continue
                # links that redirect to external domains
                if href.rstrip("/").lower() in self.blacklisted_links:
                    continue
                # avoid image and pdf links
                if ".jpg" in href or ".jpeg" in href or ".pdf" in href:
                    continue
                # exclude registration, login etc. links
                link_text_lower = link_element.text.lower()
                if any(excluded_word == link_text_lower
                       for excluded_word in EXCLUDED_WORDS):
                    if href not in self.printed_skipped_urls:
                        print "Link contains excluded words, will skip:", \
                            link_element.text, " - ", href
                        self.printed_skipped_urls.add(href)
                    continue

                if self.link_visit_counts[href] >= MAX_NUM_VISITS_TO_SAME_LINK:
                    # print "Visited this link %s times, will skip: %s on %s" % (
                    #     self.link_visit_counts[href], href, self.driver.current_url)
                    continue

                # avoid previously visited links at the last level of a walk
                # on other levels, we allow visiting up to two times
                # since we may extract a different link from a page
                if level == self.max_level and self.link_visit_counts[href]:
                    # print "Last level, link visited before, will skip", href
                    continue
                link_url = self.sanitize_url(href, current_url)
                if link_url is None:
                    continue
                # links.add(link_url)
                links[link_url] = link_element
                link_areas[link_url] = self.get_element_area(link_element)
            except Exception as e:
                print "Exception:", e
        self.dump_page_data(link_no, current_url)
        return links, link_areas


# https://stackoverflow.com/a/48149461
def crawl(url, max_level=5, max_links=200):
    try:
        spider = Spider(url, max_level, max_links)
        spider.spider_site()
    except Exception as e:
        print "Error while spidering", url, e, traceback.format_exc()


def main(csv_file):
    t0 = time()
    p = Pool(8)
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


DEBUG = False
if __name__ == '__main__':
    if DEBUG:
        url = "http://www.homestead.com"
        crawl(url, 5, 200)
    else:
        main(sys.argv[1])
