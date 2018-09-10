#!/usr/bin/python

from selenium import webdriver
from functools import reduce

# Checks if all the HTML elements have their heights within the range
def check_if_height_within_bounds(elements, lower_bound, upper_bound):
    height = map(lambda x: x.value_of_css_property('height'), elements)

    for h in height:
        if h != 'auto' and float(h[:-2]) < upper_bound and float(h[:-2]) > lower_bound:
            continue
        else:
            return False

    return True

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
                'share' in text or 'account' in text or 'sign up' in text):
            return True

    return False

# Checks if any of given HTML elements or its children have a border set
# Since some websites use pseudo-selectors to create borders, we perform that
# check too
def check_if_border(driver, elements):
    for ele in elements:
        children = ele.find_elements_by_css_selector('*')

        for child in children + [ele]:
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

# Checks whether the <li> elements are product attributes
def is_list_product_attribute(driver, li_elements):

    # Extract the <a> and <button> elements from within each <li>
    a_links = map(lambda x: x.find_elements_by_tag_name('a'), li_elements)
    buttons = map(lambda x: x.find_elements_by_tag_name('button'), li_elements)

    # If any of the <li> elements have more than one <a> or <button>,
    # probably False
    count_a_links = map(lambda x: len(x) <= 1, a_links)
    count_buttons = map(lambda x: len(x) <= 1, buttons)

    if all(x is True for x in count_a_links):
        hrefs = map(lambda x: x[0].get_attribute('href') if len(x) == 1 else
            None, a_links)
        hrefs = map(lambda x: '' if x is None else x.lower(), hrefs)
        if check_if_excluded_words(hrefs):
            return False

        texts = map(lambda x: x[0].text if len(x) == 1 else
            None, a_links)
        texts = map(lambda x: '' if x is None else x.lower(), texts)

        if check_if_excluded_words(texts):
            return False

    else:
        return False

    if all(x is True for x in count_buttons):
        texts = map(lambda x: x[0].text.lower() if len(x) == 1 else '', buttons)
        if check_if_excluded_words(texts):
            return False
    else:
        return False

    # Do all the elements have the same height? If not, probably False
    if not check_if_same_height(li_elements):
        return False

    # If the height is set automatically, if it is greater than 80, or less than
    # 20 then probably False
    if not check_if_height_within_bounds(li_elements, 21, 80):
        return False

    # The elements need to have a border
    border_check = check_if_border(driver, li_elements)

    # Are all the elements floating left (in-line/list-item and horizontal)? If
    # so, probably True
    display = map(lambda x: x.value_of_css_property('display'), li_elements)
    if (len(set(display)) == 1 and (list(set(display))[0] == 'inline-block' or
            list(set(display))[0] == 'list-item') and border_check):
        return True

    floating = map(lambda x: x.value_of_css_property('float'), li_elements)
    if (len(set(floating)) == 1 and list(set(floating))[0] == 'left' and
            border_check):
        return True

    return False


def parse_through_html_lists(driver, ul_ol_elements):
    product_attributes = []

    for element in ul_ol_elements:
        # Only look for visible list elements
        if element.is_displayed():

            ul_elements = element.find_elements_by_tag_name('ul')
            ol_elements = element.find_elements_by_tag_name('ol')

            # Ignore those <ul> and <ol> elements that have children <ul> and
            # <ol> elements
            if (len(ul_elements) != 0 or len(ol_elements) != 0):
                continue

            # Extract all <li> elements
            li_elements = element.find_elements_by_tag_name('li')

            if (len(li_elements) > 0 and
                    is_list_product_attribute(driver, li_elements)):
                print len(li_elements)
                for ele in li_elements:
                    print ele.text
                product_attributes.append(element)
            else:
                continue
        else:
            continue

    return product_attributes


def parse_through_divs(driver, div_elements):
    product_attributes = []

    div_flex_elements = filter(lambda x: x.is_displayed() == True and x.value_of_css_property('display') == 'flex', div_elements)

    for div in div_flex_elements:
        children = filter(lambda x: x.value_of_css_property('display') == 'flex', div.find_elements_by_tag_name('div'))

        if len(children) > 0:
            continue
        else:
            attrs = filter(lambda x: x.is_displayed() and
                x.value_of_css_property('display') == 'inline-block',
                div.find_elements_by_css_selector('*'))

            # Any excluded words? If so, False
            texts = map(lambda x: x.text.lower(), attrs)
            if check_if_excluded_words(texts):
                continue

            if not check_if_border(driver, attrs):
                continue

            # Do all the elements have the same height? If not, probably False
            if not check_if_same_height(attrs):
                continue

            # If the height is set automatically, if it is greater than 80, or less than
            # 20 then probably False
            if not check_if_height_within_bounds(attrs, 21, 80):
                continue

            print len(attrs)
            for attr in attrs:
                print attr.text

    return product_attributes


def get_product_attribute_elements(url):
    driver = webdriver.Firefox()
    driver.get(url)

    # Start by looking for ol, ul lists
    ul_elements = driver.find_elements_by_tag_name('ul')
    ol_elements = driver.find_elements_by_tag_name('ol')

    result = parse_through_html_lists(driver, ul_elements + ol_elements)

    div_elements = driver.find_elements_by_tag_name('div')
    result = parse_through_divs(driver, div_elements)

    driver.close()

    return result


if __name__ == '__main__':

    # Tests
    #get_product_attribute_elements('https://www.harmonystore.co.uk/fun-factory-stronic-g')
    #get_product_attribute_elements('https://www.alexandermcqueen.com/us/alexandermcqueen/coat_cod41822828kr.html')
    #get_product_attribute_elements('https://www.urbanoutfitters.com/shop/out-from-under-markie-seamless-ribbed-bra?category=womens-best-clothing&color=030')
    #get_product_attribute_elements('http://www.aeropostale.com/long-sleeve-solid-lace-up-bodycon-top/80096859.html?dwvar_80096859_color=563&cgid=whats-new-girls-new-arrivals#content=HP_eSpot&start=1')
    #get_product_attribute_elements('https://usa.tommy.com/en/men/men-shirts/lewis-hamilton-logo-shirt-mw08299')
    #get_product_attribute_elements('https://www.calvinklein.us/en/mens-clothing/mens-featured-shops-calvin-klein-jeans/slim-fit-archive-western-shirt-22705235')
    #get_product_attribute_elements('https://www.amazon.com/Linksys-Tri-Band-Intelligent-bedrooms-Multi-Story/dp/B01N2NLNEH?ref_=Oct_DLandingS_PC_NA_NA&smid=ATVPDKIKX0DER')
    #get_product_attribute_elements('https://shop4reebok.com/#!product/CN8042_temposlipon')
    #get_product_attribute_elements('https://us.boohoo.com/high-shine-v-hem-bandeau/DZZ09839.html')
    #get_product_attribute_elements('https://www.prettylittlething.com/mustard-rib-button-detail-midi-skirt.html')
    #get_product_attribute_elements('https://www.jcpenney.com/p/the-foundry-big-tall-supply-co-quick-dry-short-sleeve-knit-polo-shirt-big-and-tall/ppr5007145724?pTmplType=regular&catId=cat100240025&deptId=dept20000014&urlState=/g/mens-shirts/N-bwo3yD1nohp5&productGridView=medium&selectedSKUId=58130901099&badge=fewleft')
    #get_product_attribute_elements('https://www.forever21.com/us/shop/Catalog/Product/F21/outerwear_coats-and-jackets/2000288425')
    #get_product_attribute_elements('https://www.target.com/p/boys-short-sleeve-t-shirt-cat-jack-153/-/A-53411710?preselect=53364661#lnk=sametab')
    #get_product_attribute_elements('http://www2.hm.com/en_us/productpage.0476583002.html')
    #get_product_attribute_elements('https://www.macys.com/shop/product/circus-by-sam-edelman-kirby-booties-created-for-macys?ID=6636316&CategoryID=13616')
    get_product_attribute_elements('https://oldnavy.gap.com/browse/product.do?cid=1114941&pcid=72091&vid=1&pid=291300032')
