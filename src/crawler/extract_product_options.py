#!/usr/bin/python

from selenium import webdriver
from functools import reduce
import sys
import codecs

DEBUG = True

def debug(statement):
    if DEBUG:
        print statement

# Checks whether the HTML element has its height within the specified range
def check_if_height_within_bounds(element, lower_bound, upper_bound):
    height = element.value_of_css_property('height')

    if (height != 'auto' and float(height[:-2]) < upper_bound and
            float(height[:-2]) > lower_bound):
        return True
    else:
        return False

# Checks whether the HTML element has its width within the specified range
def check_if_width_within_bounds(element, lower_bound, upper_bound):
    width = element.value_of_css_property('width')

    if (width != 'auto' and float(width[:-2]) < upper_bound and
            float(width[:-2]) > lower_bound):
        return True
    else:
        return False

# Checks if all the HTML elements have the same height
def check_if_same_height(elements):
    heights = map(lambda x: x.value_of_css_property('height'), elements)
    if (len(set(heights)) > 1):
        return False
    else:
        return True

# Checks if any social media, signup text is in the provided list
def check_if_excluded_words(texts):
    for text in texts:
        if ('instagram' in text or 'youtube' in text or 'twitter' in text or
                'facebook' in text or 'login' in text or 'signup' in text or
                'share' in text or 'account' in text or 'sign up' in text or
                'add ' in text or 'review' in text or 'submit' in text or
                'related' in text or 'show ' in text or 'sign in' in text or
                'shop ' in text or 'upload ' in text or 'code ' in text or
                'view details' in text or 'choose options' in text or
                'cart' in text):
            return True

    return False

# Checks if the given HTML element or its children have a border set
# Since some websites use pseudo-selectors to create borders, we perform that
# check too
def check_if_border(driver, element):
    children = element.find_elements_by_css_selector('*')

    for child in children + [element]:
        if (child.value_of_css_property('border-left-style').lower() !=
            'none' and
            child.value_of_css_property('border-right-style').lower() !=
                'none'):
            return True
        elif ((driver.execute_script(
                '''return window.getComputedStyle(arguments[0],':before')
                .getPropertyValue('border-left-style')''', child)) !=
                'none' and (driver.execute_script(
                '''return window.getComputedStyle(arguments[0],':before')
                .getPropertyValue('border-right-style')''', child)) !=
                'none'):
            return True
        elif ((driver.execute_script(
                '''return window.getComputedStyle(arguments[0],':after')
                .getPropertyValue('border-left-style')''', child)) !=
                'none' and (driver.execute_script(
                '''return window.getComputedStyle(arguments[0],':after')
                .getPropertyValue('border-right-style')''', child)) !=
                'none'):
            return True
        else:
            continue

    return False

# Checks if the given HTML element has anchor tags that follow a pattern
def check_if_anchor_specs(element):
    a_links = element.find_elements_by_tag_name('a')

    if len(a_links) == 0:
        return True
    elif len(a_links) == 1:
        href = a_links[0].get_attribute('href')

        if href is None:
            href = ''
        else:
            href = href.lower()

        text = a_links[0].text
        if text is None:
            text = ''
        else:
            text = text.lower()

        if check_if_excluded_words([href, text]):
            return False

        return True
    else:
        return False

# Checks if the given HTML element has button elements that follow a pattern
def check_if_button_specs(element):
    buttons = element.find_elements_by_tag_name('button')

    if len(buttons) == 0:
        return True
    elif len(buttons) == 1:

        text = buttons[0].text
        if text is None:
            text = ''
        else:
            text = text.lower()

        title = buttons[0].get_attribute('title')
        if title is None:
            title = ''
        else:
            title = title.lower()

        if check_if_excluded_words([text, title]):
            return False

        return True
    else:
        return False

# Checks if the given HTML element has excluded elements
def check_if_excluded_elements(element):

    select = element.find_elements_by_tag_name('select')
    if len(select) != 0:
        debug('Found select - excluded')
        return True

    form = element.find_elements_by_tag_name('form')
    if len(form) != 0:
        debug('Found form - excluded')
        return True

    input = element.find_elements_by_tag_name('input')
    for i in input:
        if i.get_attribute('type') not in ['radio', 'checkbox']:
            debug('Found input type ' + i.get_attribute('type') + ' - excluded')
            return True

    button = element.find_elements_by_tag_name('button')
    for b in button:
        if b.value_of_css_property('display') in ['flex', 'inline-flex']:
            debug('Found button with display ' +
                b.value_of_css_property('display') + ' - excluded')
            return True

    iframe = element.find_elements_by_tag_name('iframe')
    if len(iframe) != 0:
        debug('Found iframe - excluded')
        return True

    return False

# Checks if the HTML element is in the correct half of the HTML page
def check_if_page_range(driver, element):
    y = float(element.location['y'])
    totalHeight = float(driver.execute_script('''return window.innerHeight;'''))

    ratio = round(y/totalHeight, 1)
    debug('y: ' + str(y))
    debug('totalHeight: ' + str(totalHeight))
    debug('Page location: ' + str(ratio))

    if ratio >= 0.3 and ratio <= 1.4:
        return True
    else:
        return False


def get_toggle_product_attribute_elements(driver):

    element_types = ['div', 'li', 'label']

    result = []

    for element in element_types:
        elements = driver.find_elements_by_tag_name(element)

        for e in elements:
            try:
                if (e.value_of_css_property('display') == 'inline-block' or
                    e.value_of_css_property('float') == 'left' or
                    e.find_element_by_xpath('..')
                        .value_of_css_property('display') == 'flex'):

                    debug('Checking: ' + e.get_attribute('outerHTML').strip())

                    if not e.is_displayed():
                        debug('Element not displayed')
                        continue

                    # Ignore <div> elements that are floating left
                    if ((element == 'div') and
                        e.value_of_css_property('float') == 'left'):
                        debug('Ignored floating left div')
                        continue

                    # Ignore <li> that contain children <li>
                    if (element == 'li' and (len(e.find_elements_by_tag_name('ul'))
                            + len(e.find_elements_by_tag_name('ol'))) > 0):
                        debug('Ignoring list element with children list elements')
                        continue

                    if check_if_excluded_words([e.text.lower()]):
                        debug('Contains excluded words')
                        continue

                    if not check_if_height_within_bounds(e, 21, 80):
                        debug('Height not within bounds')
                        continue

                    if check_if_width_within_bounds(e, 0, 5):
                        debug('Width within bounds')
                        continue

                    if not check_if_anchor_specs(e):
                        debug('Anchor specs check failed')
                        continue

                    if not check_if_button_specs(e):
                        debug('Button specs check failed')
                        continue

                    if not check_if_border(driver, e):
                        debug('Contains no border')
                        continue

                    if check_if_excluded_elements(e):
                        debug('Contains excluded elements')
                        continue

                    if not check_if_page_range(driver, e):
                        debug('Not in the first half of the webpage')
                        continue

                    debug('Attribute found')
                    print '----------------'

                    result.append(e)

            except Exception as error:
                debug('Unable to check an element')
                debug('Exception: ')
                debug(error)
                pass

    # Remove parents from the list of results
    for r in result:
        debug('Examining ' + r.get_attribute('outerHTML'))
        node = r
        while(True):
            parent = node.find_element_by_xpath('..')
            if parent in result:
                result.remove(parent)
                debug('Removed parent ' + parent.get_attribute('outerHTML'))
                break
            elif parent.tag_name == 'body':
                debug('Reached body, parent not found')
                break
            else:
                node = parent

    # Add siblings of list elements that are not present
    result_corrected = result
    for r in result:
        if r.tag_name == 'li':
            parent = r.find_element_by_xpath('..')
            children = parent.find_elements_by_tag_name('li')

            checks = map(lambda x: x in result, children)

            if not all(x is True for x in checks):
                if check_if_same_height(children):
                    result_corrected.extend(filter(lambda x: x not
                        in result, children))
                else:
                    for x in children:
                        if x in result:
                            result_corrected.remove(x)
            else:
                continue
        else:
            continue

    # Final list:
    for r in result_corrected:
        debug('Found attribute: ' + r.get_attribute('outerHTML').strip())

    return result


def get_select_product_attribute_elements(driver):

    return None


def get_product_attribute_elements(url):
    driver = webdriver.Firefox()
    driver.get(url)

    toggle_elements = get_toggle_product_attribute_elements(driver)
    select_elements = get_select_product_attribute_elements(driver)

    driver.close()


if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf8')(sys.stderr)

    # Tests
    get_product_attribute_elements('https://www.harmonystore.co.uk/fun-factory-stronic-g')
    # get_product_attribute_elements('https://www.alexandermcqueen.com/us/alexandermcqueen/coat_cod41822828kr.html')
    # get_product_attribute_elements('https://www.urbanoutfitters.com/shop/out-from-under-markie-seamless-ribbed-bra?category=womens-best-clothing&color=030')
    # get_product_attribute_elements('http://www.aeropostale.com/long-sleeve-solid-lace-up-bodycon-top/80096859.html?dwvar_80096859_color=563&cgid=whats-new-girls-new-arrivals#content=HP_eSpot&start=1')
    # get_product_attribute_elements('https://usa.tommy.com/en/men/men-shirts/lewis-hamilton-logo-shirt-mw08299')
    # get_product_attribute_elements('https://www.calvinklein.us/en/mens-clothing/mens-featured-shops-calvin-klein-jeans/slim-fit-archive-western-shirt-22705235')
    # get_product_attribute_elements('https://www.amazon.com/Linksys-Tri-Band-Intelligent-bedrooms-Multi-Story/dp/B01N2NLNEH?ref_=Oct_DLandingS_PC_NA_NA&smid=ATVPDKIKX0DER')
    # get_product_attribute_elements('https://shop4reebok.com/#!product/CN8042_temposlipon')
    # get_product_attribute_elements('https://us.boohoo.com/high-shine-v-hem-bandeau/DZZ09839.html')
    # get_product_attribute_elements('https://www.prettylittlething.com/mustard-rib-button-detail-midi-skirt.html')
    # get_product_attribute_elements('https://www.jcpenney.com/p/the-foundry-big-tall-supply-co-quick-dry-short-sleeve-knit-polo-shirt-big-and-tall/ppr5007145724?pTmplType=regular&catId=cat100240025&deptId=dept20000014&urlState=/g/mens-shirts/N-bwo3yD1nohp5&productGridView=medium&selectedSKUId=58130901099&badge=fewleft')
    # get_product_attribute_elements('https://www.forever21.com/us/shop/Catalog/Product/F21/outerwear_coats-and-jackets/2000288425')
    # get_product_attribute_elements('https://www.target.com/p/boys-short-sleeve-t-shirt-cat-jack-153/-/A-53411710?preselect=53364661#lnk=sametab')
    # get_product_attribute_elements('http://www2.hm.com/en_us/productpage.0476583002.html')
    # get_product_attribute_elements('https://www.macys.com/shop/product/circus-by-sam-edelman-kirby-booties-created-for-macys?ID=6636316&CategoryID=13616') #plus/minus
    # get_product_attribute_elements('https://oldnavy.gap.com/browse/product.do?cid=1114941&pcid=72091&vid=1&pid=291300032')
