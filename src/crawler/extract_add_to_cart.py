#!/usr/bin/python

from selenium import webdriver
from time import sleep
from utils import close_dialog
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
# a boolean indicating whether the button is clickable or not (enabled, visible,
# etc.)
def get_add_to_cart_button(driver, url):
    debug('Opening url: %s' % url)
    driver.get(url)
    sleep(5)

    try:
        # Close possible dialogs
        count = close_dialog(driver)
        if count > 0:
            debug('Found %d possible dialog close button(s), clicked' % count)

        script = ''
        with open('extract_add_to_cart.js', 'r') as f:
            script = f.read()
        buttons = driver.execute_script(script)

        # Check if buttons are clickable
        return [(button, True) for button in buttons if button.is_displayed() and button.is_enabled()]
    except:
        return []

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
    # url = 'https://www.lordandtaylor.com/lord-taylor-essential-cashmere-crewneck-sweater/product/0500088498668?FOLDER%3C%3Efolder_id=2534374302023681&R=884558471723&P_name=Lord+%26+Taylor&N=302023681&PRODUCT%3C%3Eprd_id=845524442532790&bmUID=mpCvSb5'
    url = 'https://www.the-house.com/el3smo04dg18zz-element-t-shirts.html'
    # url = 'https://www.kohls.com/product/prd-3378151/womens-popsugar-love-your-life-striped-sweater.jsp?color=Red%20Stripe&prdPV=1'
    # url = 'https://www.spanx.com/leggings/seamless/look-at-me-now-seamless-side-zip-leggings'
    # url = 'https://www.rue21.com/store/jump/product/Blue-Camo-Print-Super-Soft-Fitted-Crew-Neck-Tee/0013-002100-0008057-0040'
    # url = 'https://www.harmonystore.co.uk/fun-factory-stronic-g'
    # url = 'https://www.alexandermcqueen.com/us/alexandermcqueen/coat_cod41822828kr.html'
    # url = 'https://www.urbanoutfitters.com/shop/out-from-under-markie-seamless-ribbed-bra?category=womens-best-clothing&color=030'
    # url = 'http://www.aeropostale.com/long-sleeve-solid-lace-up-bodycon-top/80096859.html?dwvar_80096859_color=563&cgid=whats-new-girls-new-arrivals#content=HP_eSpot&start=1'
    # url = 'https://usa.tommy.com/en/men/men-shirts/lewis-hamilton-logo-shirt-mw08299'


    results = get_add_to_cart_button(driver, url)
    debug('Found %d possible add-to-cart buttons' % len(results))
    for i in range(len(results)):
        button, is_disabled = results[i]
        debug('Button %d: enabled=%s, button: %s' % (i, str(is_disabled), button.get_attribute('outerHTML')))
