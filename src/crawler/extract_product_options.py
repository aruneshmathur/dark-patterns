#!/usr/bin/python

from selenium import webdriver
from functools import reduce
import sys
import codecs
from time import sleep
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from utils import get_close_dialog_elements, close_dialog, parent_removal
from utils import unique

DEBUG = True

# Debug statements
def debug(statement):
    if DEBUG:
        print statement
    else:
        pass

# Checks whether the HTML element's height is within the specified range
def check_if_height_within_bounds(driver, element, lower_bound, upper_bound):
    height = driver.execute_script('''return (function (element) {
        return element.offsetHeight;
    })(arguments[0]);''', element)
    debug('Height: ' + str(height))

    if height != 'auto' and lower_bound < float(height) < upper_bound:
        return True
    else:
        return False


# Checks whether the HTML element's width is within the specified range
def check_if_width_within_bounds(driver, element, lower_bound, upper_bound):
    width = driver.execute_script('''return (function (element) {
        return element.offsetWidth;
    })(arguments[0]);''', element)
    debug('Width: ' + str(width))

    if width != 'auto' and lower_bound < float(width) < upper_bound:
        return True
    else:
        return False


# Checks if all the HTML elements have the same height
def check_if_same_height(elements):
    heights = map(lambda x: x.value_of_css_property('height'), elements)
    return False if len(set(heights)) > 1 else True


# Checks if the provided list of texts have any excluded words
def check_if_excluded_words(texts):
    excluded_words = ['instagram', 'youtube', 'twitter', 'facebook', 'login'
                      'log in', 'signup', 'sign up', 'signin', 'sign in',
                      'share', 'account', 'add ', 'review', 'submit', 'related',
                      'show ', 'shop ', 'upload ', 'code ', 'view details',
                      'choose options', 'cart', 'loading', 'cancel', 'view all',
                      'description', 'additional information', 'ship ', '$']

    for text in texts:
        for word in excluded_words:
            if word in text:
                return True

    return False


# Checks if the given HTML element or its children (depending on the value of
# recurse_children) have a border
# Since some websites use pseudo-selectors to create borders, we perform that
# check too
def check_if_border(driver, element, recurse_children=True):
    elements = [element]

    # If recurse_children is True, add all the children of the current element
    if recurse_children:
        elements = elements + element.find_elements_by_css_selector('*')

    for child in elements:
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
        elif child.value_of_css_property('box-shadow') != 'none':
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
        href = '' if href is None else href.lower()

        text = a_links[0].text
        text = '' if text is None else text.lower()

        return False if check_if_excluded_words([href, text]) else True
    else:
        return False


# Checks if the given HTML element has button elements that follow a pattern
def check_if_button_specs(element):
    buttons = element.find_elements_by_tag_name('button')

    if len(buttons) == 0:
        return True
    elif len(buttons) == 1:

        text = buttons[0].text
        text = '' if text is None else text.lower()

        title = buttons[0].get_attribute('title')
        title = '' if title is None else title.lower()

        return False if check_if_excluded_words([text, title]) else True
    else:
        return False


# Checks if the given HTML element has excluded elements
# Depending on the require_visible flag, invisble excluded elements can be
# included/excluded from this decision
def check_if_excluded_elements(element, require_visible=False):

    # Returns False if all the elements are not visible
    def visibility(elements):
        visible = map(lambda x: x.is_displayed(), elements)
        if all(x == False for x in visible):
            return False
        else:
            debug('Found visible ' + ee + ' - excluded')
            return True

    excluded_elements = {'select': None,
                         'form': None,
                         'iframe': None,
                         'p': None,
                         'style': None,
                         'h1': None,
                         'input': (lambda x: x.get_attribute('type') not in
                                    ['radio', 'checkbox']),
                         'button': (lambda x: x.value_of_css_property('display')
                                    in ['flex', 'inline-flex']),
                         'dl': None}

    for ee, func in excluded_elements.items():
        ee_elements = element.find_elements_by_tag_name(ee)

        if func is not None:
            ee_elements = filter(func, ee_elements)

        if len(ee_elements) != 0:
            if require_visible:
                return visibility(ee_elements)
            else:
                debug('Found ' + ee + ' - excluded')
                return True

    return False


# Checks if the HTML element is in the correct half of the HTML page
def check_if_page_range(driver, element):
    coord = driver.execute_script('''return (function offset(el) {
        var rect = el.getBoundingClientRect(),
        scrollLeft = window.pageXOffset || document.documentElement.scrollLeft,
        scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        return { top: rect.top + scrollTop, left: rect.left + scrollLeft }
    })(arguments[0]);''', element)

    x = float(coord['left'])
    y = float(coord['top'])
    debug('coord: ' + str(x) + ',' + str(y))

    totalWidth = float(driver.execute_script('''return window.innerWidth;'''))
    totalHeight = float(driver.execute_script('''return window.innerHeight;'''))

    debug('Window dimension: ' + str(totalWidth) + ',' + str(totalHeight))

    x_ratio = round(x/totalWidth, 1)
    y_ratio = round(y/totalHeight, 1)


    debug('Page location: ' + str(x_ratio) + ',' + str(y_ratio))

    return True if (0.3 <= y_ratio <= 1.3) and (x_ratio >= 0.15 ) else False


# Checks whether the given element has direct visible siblings of the same type
def check_if_same_visible_siblings(e):
    parent = e.find_element_by_xpath('..')
    children = parent.find_elements_by_xpath('./*')
    visible_children = filter(lambda x: x.is_displayed() and x != e, children)

    if len(visible_children) == 0:
        return False
    else:
        match_children = map(lambda x: x.tag_name == e.tag_name, visible_children)

        return True if any(x is True for x in match_children) else False


# If <li> elements are in the list of HTML elements, then add their siblings
# assuming they are not present provided they are of the same height
# If not, remove these <li> elements
def validate_li_siblings(elements):
    result = list(elements)

    for element in result:
        if element.tag_name == 'li':
            parent = element.find_element_by_xpath('..')
            children = parent.find_elements_by_tag_name('li')

            checks = map(lambda x: x in result, children)

            if not all(x is True for x in checks):
                if check_if_same_height(children):
                    result.extend(filter(lambda x: x not
                        in result, children))
                else:
                    for x in children:
                        if x in result:
                            result.remove(x)
            else:
                continue
        else:
            continue

    return result


# Find toggle elements on the web page
def get_toggle_product_attribute_elements(driver):
    element_types = ['div', 'li', 'label', 'a']
    result = []

    debug('Beginning search for toggle product attributes')

    for element in element_types:
        elements = driver.find_elements_by_tag_name(element)
        debug('Count(' + element + '): ' + str(len(elements)))

        for e in elements:
            try:
                debug('Checking: ' + e.get_attribute('outerHTML').strip())

                if (e.value_of_css_property('display') != 'inline-block' and
                    e.value_of_css_property('float') != 'left' and
                    e.find_element_by_xpath('..')
                        .value_of_css_property('display') != 'flex' and
                    e.find_element_by_xpath('..')
                        .value_of_css_property('float') != 'left'):

                    debug('Not the required display or float')
                    continue

                # Ignore invisble elements
                if not e.is_displayed():
                    debug('Element not displayed')
                    continue

                # Ignore <li> that contain children <li>
                if (element == 'li' and (len(e.find_elements_by_tag_name('ul'))
                        + len(e.find_elements_by_tag_name('ol'))) > 0):
                    debug('Ignoring list element with children list elements')
                    continue

                # Ignore if the element contains excluded words
                if check_if_excluded_words([e.text.lower()]):
                    debug('Contains excluded words')
                    continue

                # Ignore if the element is not within the height bounds
                if not check_if_height_within_bounds(driver, e, 21, 80):
                    debug('Height not within bounds')
                    continue

                # Ignore if the element is within the width bounds
                if check_if_width_within_bounds(driver, e, 0, 5):
                    debug('Width within bounds')
                    continue

                # Ignore if the element fails the <a> element checks
                if not check_if_anchor_specs(e):
                    debug('Anchor specs check failed')
                    continue

                # Ignore if the element fails the <button> element checks
                if not check_if_button_specs(e):
                    debug('Button specs check failed')
                    continue

                # Ignore if the element fails the border check
                if not check_if_border(driver, e):
                    debug('Contains no border')
                    continue

                # Ignore if the element has excluded elements
                if check_if_excluded_elements(e):
                    debug('Contains excluded elements')
                    continue

                # Ignore if the element is not in the required page range
                if not check_if_page_range(driver, e):
                    debug('Not in the correct range of the webpage')
                    continue

                debug('Toggle candidate found')
                result.append(e)

            except Exception as error:
                debug('Unable to check an element')
                debug('Exception: ' + str(error))
                pass

    result = unique(result)

    debug('The list of toggle elements before pre-processing is:')
    for r in result:
        debug('Element: ' + r.get_attribute('outerHTML'))

    # Remove parents from the list of results
    result = parent_removal(result, 'li')

    debug('The list of toggle elements after parent correction is:')
    for r in result:
        debug('Element: ' + r.get_attribute('outerHTML'))

    # Add siblings of list elements that are not present
    result = unique(validate_li_siblings(result))

    # Final list:
    debug('The final list of toggle elements are:')
    for r in result:
        debug('Toggle attribute: ' + r.get_attribute('outerHTML').strip())

    debug('Concluding search for toggle product attributes')

    # TODO: Filter out those attributes that have negative margin set on
    # any one of the attributes or an opacity value of 0. See Macy's and Old
    # Navy for examples

    return result


# Find select elements on the web page
def get_select_product_attribute_elements(driver):
    result = []

    debug('Beginning search for select product attributes')

    # First, search for select elements and if found, return them
    select_elements = driver.find_elements_by_tag_name('select')

    for se in select_elements:
        try:
            debug('Count(select): ' + str(len(select_elements)))
            debug('Checking select: ' + se.get_attribute('outerHTML').strip())

            if not se.is_displayed():
                debug('Ignoring hidden select')
                continue

            if se.text is None or se.text.strip() == '':
                debug('Ignoring select with empty text')
                continue

            if not check_if_page_range(driver, se):
                debug('Select not in the correct range of the webpage')
                continue

            debug('Select candidate found')

            options = se.find_elements_by_tag_name('option')

            for option in options:
                debug('Option: ' + option.get_attribute('outerHTML'))
                result.append((se, option))

        except Exception as error:
            debug('Unable to check an element')
            debug('Exception: ' + str(error))
            pass

    if len(result) > 0:
        debug('Found traditional select products attributes, returning')
        debug('Concluding search for select product attributes')
        return result
    else:
        debug('Found no traditional select product attributes, continuing search')

    # Website does not use standard HTML selects, search for alternatives
    # Possible triggers
    element_types = ['div', 'span', 'a']
    triggers = []

    for element in element_types:
        elements = driver.find_elements_by_tag_name(element)
        debug('Count(' + element + '): ' + str(len(elements)))

        for e in elements:
            try:
                debug('Checking: ' + e.get_attribute('outerHTML').strip())

                if not e.is_displayed():
                    debug('Ignoring hidden element')
                    continue

                if e.text is None or e.text.strip() == '':
                    debug('Ignoring element with empty text')
                    continue

                # Ignore if the element contains excluded words
                if check_if_excluded_words([e.text.lower()]):
                    debug('Contains excluded words')
                    continue

                if not check_if_page_range(driver, e):
                    debug('Not in the correct range of the webpage')
                    continue

                if not check_if_border(driver, e, recurse_children=False):
                    debug('Element has no border')
                    continue

                if check_if_same_visible_siblings(e):
                    debug('Has a visible sibling of the same tag - ignoring')
                    continue

                if not check_if_anchor_specs(e):
                    debug('Anchor specs failed')
                    continue

                if check_if_excluded_elements(e, require_visible=True):
                    debug('Excluded elements found')
                    continue

                if e.value_of_css_property('position') == 'fixed':
                    debug('Fixed element found - ignoring')
                    continue

                # Ignore if the element is not within the height bounds
                if not check_if_height_within_bounds(driver, e, 10, 100):
                    debug('Height not within bounds')
                    continue

                debug('Trigger candidate found')
                triggers.append(e)

            except Exception as error:
                debug('Unable to check an element')
                debug('Exception: ' + str(error))
                pass

    triggers = unique(triggers)

    # TODO: Remove trigger if already in toggle element

    debug('The list of trigger elements before pre-processing is:')
    for t in triggers:
        debug('Element: ' + t.get_attribute('outerHTML'))

    # Remove parents from the list of results
    triggers = parent_removal(triggers)

    debug('The list of triggers after parent correction is:')
    for t in triggers:
        # t.click()
        debug('Element: ' + t.get_attribute('outerHTML'))

    debug('Concluding search for select product attributes')

    return None

def get_product_attribute_elements(url):
    profile = webdriver.FirefoxProfile()
    profile.set_preference('privacy.trackingprotection.enabled', False)
    profile.set_preference('dom.webnotifications.enabled', False)
    profile.set_preference('dom.push.enabled', False)
    profile.set_preference('network.cookie.cookieBehavior', 0)

    driver = webdriver.Firefox(executable_path=r'/usr/local/bin/geckodriver',
                               firefox_profile=profile)
    driver.get(url)
    sleep(5)

    count = close_dialog(driver)
    debug('Found ' + str(count) + ' close elements -- all of which were clicked')

    # toggle_elements = get_toggle_product_attribute_elements(driver)
    select_elements = get_select_product_attribute_elements(driver)

    driver.close()


if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf8')(sys.stderr)

    # Tests
    get_product_attribute_elements('https://www.the-house.com/el3smo04dg18zz-element-t-shirts.html')
    # get_product_attribute_elements('https://www.kohls.com/product/prd-3378151/womens-popsugar-love-your-life-striped-sweater.jsp?color=Red%20Stripe&prdPV=1')
    # get_product_attribute_elements('https://www.spanx.com/leggings/seamless/look-at-me-now-seamless-side-zip-leggings')
    # get_product_attribute_elements('https://www.rue21.com/store/jump/product/Blue-Camo-Print-Super-Soft-Fitted-Crew-Neck-Tee/0013-002100-0008057-0040')
    # get_product_attribute_elements('https://www.harmonystore.co.uk/fun-factory-stronic-g')
    # get_product_attribute_elements('https://www.alexandermcqueen.com/us/alexandermcqueen/coat_cod41822828kr.html')
    # get_product_attribute_elements('https://www.urbanoutfitters.com/shop/out-from-under-markie-seamless-ribbed-bra?category=womens-best-clothing&color=030')
    # get_product_attribute_elements('http://www.aeropostale.com/long-sleeve-solid-lace-up-bodycon-top/80096859.html?dwvar_80096859_color=563&cgid=whats-new-girls-new-arrivals#content=HP_eSpot&start=1')
    # get_product_attribute_elements('https://usa.tommy.com/en/men/men-shirts/lewis-hamilton-logo-shirt-mw08299')
    # get_product_attribute_elements('https://www.calvinklein.us/en/mens-clothing/mens-featured-shops-calvin-klein-jeans/slim-fit-archive-western-shirt-22705235')
    # get_product_attribute_elements('https://www.amazon.com/Linksys-Tri-Band-Intelligent-bedrooms-Multi-Story/dp/B01N2NLNEH?ref_=Oct_DLandingS_PC_NA_NA&smid=ATVPDKIKX0DER')
    # get_product_attribute_elements('https://shop4reebok.com/#product/CN8037_hurtleslipon')
    # get_product_attribute_elements('https://us.boohoo.com/high-shine-v-hem-bandeau/DZZ09839.html')
    # get_product_attribute_elements('https://www.prettylittlething.com/mustard-rib-button-detail-midi-skirt.html')
    # get_product_attribute_elements('https://www.jcpenney.com/p/the-foundry-big-tall-supply-co-quick-dry-short-sleeve-knit-polo-shirt-big-and-tall/ppr5007145724?pTmplType=regular&catId=cat100240025&deptId=dept20000014&urlState=/g/mens-shirts/N-bwo3yD1nohp5&productGridView=medium&selectedSKUId=58130901099&badge=fewleft')
    # get_product_attribute_elements('https://www.forever21.com/us/shop/Catalog/Product/F21/outerwear_coats-and-jackets/2000288425')
    # get_product_attribute_elements('https://www.target.com/p/boys-short-sleeve-t-shirt-cat-jack-153/-/A-53411710?preselect=53364661#lnk=sametab')
    # get_product_attribute_elements('http://www2.hm.com/en_us/productpage.0476583002.html')
    # get_product_attribute_elements('https://www.macys.com/shop/product/circus-by-sam-edelman-kirby-booties-created-for-macys?ID=6636316&CategoryID=13616')
    #plus/minus
    # get_product_attribute_elements('https://oldnavy.gap.com/browse/product.do?cid=1114941&pcid=72091&vid=1&pid=291300032') # drawer
    # get_product_attribute_elements('https://voe21.com/collections/all-products-1/products/2018-version-of-anti-theft-backpack?variant=12917366161471')
