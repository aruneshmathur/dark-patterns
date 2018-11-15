#!/usr/bin/python

from selenium import webdriver
from time import sleep
import codecs
import re
import sys

# Set to True for debugging output
DEBUG = True

# Debug statements
def debug(statement):
    if DEBUG:
        print statement
    else:
        pass

# Checks whether an element is disabled. Returns True if it has the 'disabled'
# attribute and it is actually disabled.
def is_disabled(elem):
    return elem.disabled and elem.disabled == 'disabled'

# Attempts to find an add-to-cart button at the given url. Returns a list of
# all possible buttons as 2-tuples (button, is_disabled) where is_disabled is
# a boolean indicating whether the button is disabled or not.
def get_add_to_cart_button(driver, url):
    debug('Opening url: %s' % url)
    driver.get(url)
    sleep(5)

    # TODO: init to all elems
    elems = []

    # Filter elements that can be buttons
    possible_btns = ['button', 'input', 'a']

    # Filter elements in the "middle" of the page (middle third)
    # TODO

    # Try various heuristics for identifying the add-to-cart button
    pattern = re.compile('[Aa][Dd][Dd].*[Tt][Oo].*')
    results = []
    for elem in elems:
        # Inner text says "add to ___"
        # TODO: Need to account for cases when inner text is within children
        # (e.g. in a span)
        if pattern.match(elem.text):
            results.append((elem, is_disabled(elem)))
            continue

        # Any attribute contains "add to ___" or some variant
        # TODO

        # Parent div(s) has attribute that contains "add to ___" or some variant
        # TODO

        # If it's an image, img src contains some form of "add to ___"
        # TODO

    return results

# Adds the product to the cart at the given url
def add_to_cart(driver, url):
    results = get_add_to_cart_button(driver, url)

    if len(results) == 0:
        debug('No add-to-cart buttons found at this url: %s' % url)
        return

    if len(results) > 0:
        debug('Found %d possible add-to-cart buttons. Clicking all of them' % len(results))

    for i in range(len(results)):
        button, is_disabled = results[i]
        if is_disabled:
            debug('%dth possible add-to-cart button was disabled, not clicking: %s' % (i, str(button)))
        else:
            button.click()

if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf8')(sys.stderr)

    # Run on sample page
    driver = webdriver.Firefox(executable_path=r'/usr/local/bin/geckodriver')
    url = 'https://www.the-house.com/el3smo04dg18zz-element-t-shirts.html'

    results = get_add_to_cart_button(driver, url)
    debug('Found %d possible add-to-cart buttons' % len(results))
    for i in range(len(results)):
        button, is_disabled = results[i]
        debug('Button %d: enabled=%s, button: %s' % (i, str(is_disabled), str(button)))
