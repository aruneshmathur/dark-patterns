from __future__ import division
import os
import sys
import random
import math
from time import time, sleep
from selenium import webdriver
from urlparse import urlparse, urljoin
from os.path import join, isdir
from numpy.random import choice
from random import randint
from multiprocessing import Pool
from _collections import defaultdict
from polyglot.detect import Detector
import logging

import pickle
import pandas as pd

from pyvirtualdisplay import Display

from selenium.common.exceptions import WebDriverException,\
    NoAlertPresentException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from craw_utils import (get_tld_or_host, dump_as_json, safe_filename_from_url,
                        move_to_element, write_to_file)

from multiprocessing_logging import install_mp_handler
from selenium.webdriver.support.wait import WebDriverWait
from utils import close_dialog
from ml_utils import build_features


class OffDomainNavigationError(Exception):
    """Crawler is redirected to a domain different than we want to visit."""
    pass


logger = logging.getLogger(__name__)
lf_handler = logging.FileHandler('link_extraction_pilot.log')
lf_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
lf_handler.setFormatter(lf_format)
logger.addHandler(lf_handler)
logger.setLevel(logging.INFO)
install_mp_handler()


VIRT_DISPLAY_DIMS = (1200, 1920)  # 24" vertical monitor

HOVER_BEFORE_CLICKING = True
DURATION_SLEEP_AFTER_GET = 3  # Sleep 3 seconds after each page load
ENABLE_XVFB = True


OUTDIR = "output"
ALLOWED_SCHEMES = ["http", "https"]

# don't visit links with those words
EXCLUDED_WORDS = ["login", "register", "subscribe", "sign in",
                  "sign up", "add to cart", "checkout", "privacy policy",
                  "contact us", "about us", "help"]


MAX_NUM_VISITS_TO_SAME_LINK = 2
PAGE_LOAD_TIMEOUT = 60

ONLY_RUN_LANG_DETECTION = False


def get_prod_likelihoods(urls):
    df = pd.DataFrame.from_records([(url,) for url in urls], columns=["url"])
    X = build_features(df, load_scaler_from_file=True)
    model_filename = 'SGDClassifier.est'
    sgd_est = pickle.load(open(model_filename, 'rb'))
    # [1] for product probability
    probas = [x[1] for x in sgd_est.predict_proba(X.values)]
    ranked_probas = zip(urls, probas)
    ranked_probas.sort(key=lambda x: x[1], reverse=True)
    return ranked_probas


class Spider(object):

    def __init__(self, top_url, max_level=5, max_links=50):
        self.top_url = top_url
        self.max_level = max_level
        self.max_links = max_links
        self.observed_links = {}  # page url -> links
        self.visited_links = {}  # page number -> link
        self.product_links = set()
        self.printed_skipped_urls = set()
        # links that redirect to other domains etc.
        self.blacklisted_links = set()
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
        self.product_links_file_name = join(
            self.outdir, 'product_links_%s.txt' % self.base_filename)
        opts = Options()
        opts.log.level = "info"
        self.driver = webdriver.Firefox(firefox_options=opts)
        self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    def __del__(self):
        try:
            if hasattr(self, "driver"):
                self.driver.quit()
        except Exception:
            logger.exception("Exception in destructor")

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
        # relative URLs
        elif not parsed_url.netloc and not parsed_url.scheme\
                and (":" not in href):
            # urlparse return empty scheme for some tel:, sms:, call: urls
            # See, https://bugs.python.org/issue14072#msg179271
            # ":" in check is to avoid treating those links as relative links
            logger.info("Relative URL %s" % href)
            href = urljoin("%s://%s" % (current_scheme, current_netloc), href)
        elif href.startswith("//"):  # Protocol-relative URL
            href = "%s:%s" (current_scheme, href)
        else:
            if parsed_url.scheme not in ["javascript", "mailto", "tel"]:
                # logger.info("NOT adding %s %s" % (href, current_url))
                pass
            return None
        href = href.replace("\r", "").replace("\n", "").replace("\t", "")
        tld = get_tld_or_host(href)
        if tld != self.top_url_tld:  # dont' add external links
            return None
        return href

    def dismiss_alert(self):
        try:
            self.driver.switch_to.alert.accept()
            logger.info("Dismissed an alert box on %s" %
                        self.driver.current_url)
        except NoAlertPresentException:
            pass

    def visit_random_link(self, links, link_areas,
                          use_product_likelihood=False):
        # max num of tries to pick a random link
        MAX_NUM_CHOICES_RANDOM_LINK = 100
        # fall back to random (non-area based) random
        # link selection after a certain number of tries
        MAX_CHOICES_WITH_AREA_WEIGHTED_CHOICE = 50
        # TODO: have a param for method
        if use_product_likelihood:
            AREA_WEIGHTED_CHOICE = False
        else:
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

        elif use_product_likelihood:
            probas = get_prod_likelihoods(link_urls)

        num_choices = 0
        while len(tried_links) < len(link_urls) and (
                num_choices < MAX_NUM_CHOICES_RANDOM_LINK):
            if use_area_weighted_choice:
                link_url = choice(link_urls, p=link_probability_dist)
            elif use_product_likelihood:
                link_url = probas[num_choices][0]
            else:
                link_url = random.choice(links.keys())

            num_choices += 1
            if num_choices == MAX_CHOICES_WITH_AREA_WEIGHTED_CHOICE:
                # fall back to random selection if we can't pick by area
                logger.info("Falling back to random link selection %s" %
                            self.driver.current_url)
                use_area_weighted_choice = False
            tried_links.add(link_url)
            # links that redirect to external domains
            if link_url.rstrip("/").lower() in self.blacklisted_links:
                continue
            # if we clicked/visited this link more than the limit
            if (self.link_visit_counts[link_url] >= MAX_NUM_VISITS_TO_SAME_LINK
                    or link_url in self.product_links):
                continue
            # only difference is the anchor tag
            if use_product_likelihood:   # debugging
                logger.info("Selected the link with P(prod)=%0.3f %s on %s" %
                            (probas[num_choices-1][1], probas[num_choices-1][0],
                             self.driver.current_url))

            try:
                if CLICK_LINKS:
                    link_element = links[link_url]
                    self.click_to_link(link_element)
                else:
                    self.load_url(link_url)
            except OffDomainNavigationError:
                logger.warning("Navigated away from the page %s on %s" %
                               (self.driver.current_url, self.top_url))
            except Exception:
                logger.exception("Exception while following link %s %s" %
                                 (link_url, self.driver.current_url))
            else:
                # logger.info("Visited a link after %s choices on %s" % (
                #    num_choices, self.driver.current_url))
                return link_url
        return None

    def click_to_link(self, link_element):
        if HOVER_BEFORE_CLICKING:
            # scroll to element
            self.driver.execute_script(
                "arguments[0].scrollIntoView();", link_element)
            # Move the mouse to the element
            move_to_element(self.driver, link_element)
        link_element.click()

    def get_page_text(self):
        return self.driver.execute_script(
            "return (!!document.body && document.body.innerText)")

    def check_for_CF_gateway(self):
        CF_TEXT = "Checking your browser before accessing"
        MAX_TRIES = 3
        try_cnt = 0
        while try_cnt < MAX_TRIES:
            try_cnt += 1
            page_text = self.get_page_text()
            if not page_text:
                logger.warning("No page text, will wait %s", self.top_url)
                sleep(3)
            elif CF_TEXT in page_text:
                logger.warning("CF detected, will sleep %s", self.top_url)
                sleep(3)
            else:
                break

    def load_url(self, url, stay_on_same_tld=True):
        self.driver.get(url)
        sleep(DURATION_SLEEP_AFTER_GET)
        self.dismiss_alert()
        if stay_on_same_tld:
            tld = get_tld_or_host(self.driver.current_url)
            if tld != self.top_url_tld:  # is this the domain we want to visit?
                self.blacklisted_links.add(url.rstrip('/').lower())
                raise OffDomainNavigationError()
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.check_for_CF_gateway()

    def get_page_language(self):
        # we expect at least 64 chars to detect language
        MIN_TEXT_LEN_TO_DETECT_LANG = 64
        inner_text = self.get_page_text()
        if not inner_text:
            # this happens when document doesn't have a body
            logger.warning("Cannot read page text: %s" % self.top_url)
            return None
        if len(inner_text) < MIN_TEXT_LEN_TO_DETECT_LANG:
            logger.warning("Text is too short to detect language: %s %s" %
                           (len(inner_text), self.top_url))
            return None

        try:
            lang_detector = Detector(inner_text, quiet=True)
        except Exception:
            logger.exception("Exception while detecting language on %s" %
                             self.top_url)
            return None  # assume a non-english page if we can't detect
        logger.info("Lang code: %s %s" % (self.top_url,
                                          lang_detector.language.code))
        return lang_detector.language.code

    def close_dialog(self):
        # just to try on different website
        TEST_CLOSE_DIALOG = True
        n_closed_dialog_elements = 0
        if TEST_CLOSE_DIALOG:
            self.make_site_dir()
            safe_url = safe_filename_from_url(self.top_url)
            png_file_name = self.png_file_name.replace(
                "PAGE_NO", str("BEFORE")).replace("URL", safe_url)
            self.driver.get_screenshot_as_file(png_file_name)

            try:
                n_closed_dialog_elements = close_dialog(self.driver)
                if n_closed_dialog_elements:
                    logger.info("Closed %d dialogs on %s" % (
                        n_closed_dialog_elements, self.top_url))
                    sleep(1)
            except Exception:
                logger.exception("Error while closing dialog %s" % self.top_url)

            if n_closed_dialog_elements:
                png_file_name = self.png_file_name.replace(
                    "PAGE_NO", str("AFTER")).replace("URL", safe_url)
                self.driver.get_screenshot_as_file(png_file_name)

    def spider_site(self):
        links = []
        link_areas = []
        MAX_SPIDERING_DURATION = 60*60  # in s
        MAX_WALK_COUNT = 100
        num_visited_pages = 0
        # TODO stop condition
        t_start = time()

        logger.info("Will visit %s" % self.top_url)
        # TODO: consider moving exception handling into load_url
        try:
            self.load_url(self.top_url)
        except OffDomainNavigationError:
            logger.warning("Navigated away from the page %s" % self.top_url)
            return
        except TimeoutException:
            logger.warning("Timeout while loading %s" % self.top_url)
            return
        except WebDriverException as wexc:
            if "about:neterror?e=dnsNotFound" in wexc.msg:
                logger.warning("DNS Error while loading %s" % self.top_url)
            else:
                logger.exception("Error while loading %s" % self.top_url)
            return
        except Exception:
            logger.exception("Error while loading %s" % self.top_url)
            return

        lang_code = self.get_page_language()
        # TODO: we continue to spider a page when we can't detect the
        # language. This is to prevent missing english sites for which
        # we can't detect language
        if lang_code is None:
            logger.warn("Cannot detect language %s" % self.top_url)
        elif lang_code != "en":
            logger.info("Will skip non-English page %s" % self.top_url)
            return

        # TODO: set to False once we are done with detecting page languages
        if ONLY_RUN_LANG_DETECTION:
            return

        self.close_dialog()
        home_links, home_link_areas = self.extract_links(0, num_visited_pages)
        if not home_links:
            logger.warning("Cannot find any links on the home page %s" %
                           self.driver.current_url)
            return
        self.observed_links[self.top_url] = home_links.keys()
        num_walks = 0
        MAX_PROD_LINKS = 10
        while (num_walks < MAX_WALK_COUNT and
               num_visited_pages < self.max_links and
               (time() - t_start) < MAX_SPIDERING_DURATION
               and len(self.product_links) < MAX_PROD_LINKS):
            num_walks += 1
            for level in xrange(1, self.max_level+1):
                if level == 1:
                    if num_walks == 1:
                        home_sales_links, home_sales_link_areas = \
                            self.get_sales_links(home_links, home_link_areas)
                        navigated_link = self.visit_random_link(
                            home_sales_links, home_sales_link_areas)
                    else:
                        navigated_link = self.visit_random_link(
                            home_links, home_link_areas,
                            use_product_likelihood=True)
                else:
                    navigated_link = self.visit_random_link(
                        links, link_areas, use_product_likelihood=True)
                current_url = self.driver.current_url
                if navigated_link is None:
                    logger.warning("Cannot find any links on page %s" %
                                   current_url)
                    if current_url != self.top_url:
                        self.blacklisted_links.add(current_url)
                    break

                num_visited_pages += 1
                self.visited_links[num_visited_pages] = navigated_link
                self.link_visit_counts[navigated_link] += 1

                # if we are redirected to another page,
                # increment counter for that URL too
                if current_url != navigated_link:
                    self.link_visit_counts[current_url] += 1
                    logger.info("Link %s of %s. Level %s. Navigated to %s. "
                                "Redirected to: %s" % (
                                    num_visited_pages, self.max_links, level,
                                    navigated_link, current_url))

                else:
                    logger.info("Link %s of %s. Level %s. nProdPages: %d. Navigated to %s. " % (
                                num_visited_pages, self.max_links,
                                level, len(self.product_links), navigated_link))
                if self.is_product_page():
                    self.product_links.add(current_url)
                    logger.info("Found a product page nProdPages: %d %s" %
                                (len(self.product_links), current_url))
                    break  # don't follow links from a product page

                # Extract links
                links, link_areas = self.extract_links(level,
                                                       num_visited_pages)
                if not links:
                    break
                self.observed_links[navigated_link] = links.keys()

        self.finalize_visit(t_start, num_visited_pages, num_walks)

    def finalize_visit(self, t_start, num_visited_pages, num_walks):
        dump_as_json(self.observed_links, self.links_json_file_name)
        dump_as_json(self.visited_links, self.visited_links_json_file_name)
        with open(self.product_links_file_name, "w") as f:
            f.write("\n".join(self.product_links))
        duration = (time() - t_start) / 60
        logger.info("Finished crawling %s in %0.1f mins."
                    " Visited %s pages, made %s walks, found %d product pages"
                    % (self.top_url, duration, num_visited_pages, num_walks, len(self.product_links)))

    def get_sales_links(self, home_links, home_link_areas):
        home_sales_links = {}
        home_sales_link_areas = {}
        SALES_KEYWORDS = ["sale", "clearance", "deal", "special",
                          "offer", "outlet", "promotion"]

        for link_url, link_element in home_links.iteritems():
            try:
                title = link_element.get_attribute("title") or ""
                alt_text = link_element.get_attribute("alt") or ""
                if any((sales_keyword in link_element.text.lower().split() or
                        sales_keyword in title.lower().split() or
                        sales_keyword in alt_text.lower().split())
                       for sales_keyword in SALES_KEYWORDS):
                    # print "Sales related link", link_url, "Text:",\
                    # link_element.text,     "Title:", title, "Alt text:",\
                    # alt_text
                    home_sales_links[link_url] = link_element
                    home_sales_link_areas[link_url] = home_link_areas[link_url]
            except StaleElementReferenceException:
                pass
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

    def is_product_page(self):
        # random id to be able group together logs from the same page
        rand_id = randint(0, 2**32)
        url = self.driver.current_url
        js = self.driver.execute_script
        n_add_to_cart = js("return (document.body.innerHTML.toLowerCase()"
                           ".match(/add to cart/g) || []).length")
        n_add_to_bag = js("return (document.body.innerHTML.toLowerCase()"
                          ".match(/add to bag/g) || []).length")
        buttons = js(open('extract_add_to_cart.js').read() +
                     ";return getPossibleAddToCartButtons();")
        # Check if buttons are clickable
        buttons = [button for button in buttons
                   if button["elem"].is_displayed()
                   and button["elem"].is_enabled()]
        if not (buttons or n_add_to_cart or n_add_to_bag):
            return False
        is_product_by_html = (n_add_to_cart == 1 and not n_add_to_bag) or (
            n_add_to_bag == 1 and not n_add_to_cart)

        for button in buttons:
            logger.info("AddToCartButtons: button txt: %s - %0.3f %s %d" %
                        (button["elem"].text, button["score"], url, rand_id))

        is_product_by_buttons = False
        # either one result
        if len(buttons) == 1:
            is_product_by_buttons = True
        # first and second and different ()
        elif len(buttons) > 1 and (buttons[0]["elem"].text != buttons[1]["elem"].text):
            is_product_by_buttons = True

        logger.info("is_product_page - by_html: %s by_buttons: %s n_button"
                    ": %s n_add_to_cart: %s n_add_to_bag: %s %s %d" %
                    (is_product_by_html, is_product_by_buttons, len(buttons),
                     n_add_to_cart, n_add_to_bag, url, rand_id))
        return is_product_by_html or is_product_by_buttons

    def extract_links(self, level, link_no):
        links = {}
        link_areas = {}
        driver = self.driver
        current_url = driver.current_url
        link_elements = driver.find_elements_by_xpath("//a[@href]")
        for link_element in link_elements:
            try:
                href = link_element.get_attribute("href")
                if href.rstrip("/") == self.top_url.rstrip("/") \
                        or href.rstrip("/") == current_url.rstrip("/"):
                    continue

                if href.rsplit("#", 1)[0] == self.top_url.rstrip("/") \
                        or href.rsplit("#", 1)[0] == current_url.rstrip("/"):
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
                        # logger.info("Link contains excluded words, will skip:"
                        #            " %s - %s" % (link_element.text, href))
                        self.printed_skipped_urls.add(href)
                    continue

                if self.link_visit_counts[href] >= MAX_NUM_VISITS_TO_SAME_LINK:
                    continue

                # avoid previously visited links at the last level of a walk
                # on other levels, we allow visiting up to two times
                # since we may extract a different link from a page
                if level == self.max_level and self.link_visit_counts[href]:
                    continue
                link_url = self.sanitize_url(href, current_url)
                if link_url is None:
                    continue
                # links.add(link_url)
                links[link_url] = link_element
                link_areas[link_url] = self.get_element_area(link_element)
            except Exception:
                logger.exception("Exception in extract_links")
        self.dump_page_data(link_no, current_url)
        return links, link_areas


def crawl(url, max_level=5, max_links=100):
    try:
        spider = Spider(url, max_level, max_links)
        spider.spider_site()
    except Exception:
        logger.exception("Error while spidering %s" % url)


def main(csv_file):
    t0 = time()
    if ENABLE_XVFB:
        display = Display(visible=False, size=VIRT_DISPLAY_DIMS)
        display.start()
    p = Pool(16)
    shop_urls = []
    for line in open(csv_file):
        line = line.rstrip()
        items = line.split(",")
        if items[-1] == "overall_rank" or items[-1] == "category":
            continue
        domain = items[0]
        if not domain.startswith("http"):
            url = "http://" + domain
        else:
            url = domain
        shop_urls.append(url)

    p.map(crawl, shop_urls)
    if ENABLE_XVFB:
        display.stop()
    logger.info("Finished in %0.1f mins" % ((time() - t0) / 60))


DEBUG = False
if __name__ == '__main__':
    if DEBUG:
        url = "http://bathselect.com"
        crawl(url, 5, 200)
    else:
        main(sys.argv[1])
