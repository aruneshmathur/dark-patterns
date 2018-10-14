# Flattens a list of sets
def flatten(elements):
    return [set_item for set_element in elements for set_item in set_element]

# Checks if element1 and element2 are siblings
def check_if_sibling(element1, element2):
    parent = element1.find_element_by_xpath('..')
    return True if element2 in parent.find_elements_by_xpath('./*') else False


# Checks whether element2 is in the parent tree of element1
def parent_of_another(element1, element2):
    if element1 is None or element2 is None:
        return False
    elif element1 == element2:
        return True
    elif element1.tag_name == 'body':
        return False
    else:
        return parent_of_another(element1.find_element_by_xpath('..'), element2)


# Given two elements, this function checks whether either one is in the parent
# tree of the others
def either_parent_of_another(element1, element2):
    return (parent_of_another(element1, element2) or
                parent_of_another(element2, element1))


# Takes a list of HTML elements and returns a list such that none of the
# elements have their parents (up to but excluding <body>) in the returned list
def parent_removal(elements, atomic_element=None):

    # Find an element in the HTML list that also has its parent (up to but
    # excluding <body>) in the list
    # Returns None if no such element exists
    def find_element_with_parent(elements):
        for i in range(0, len(elements)):
            current_element = elements[i]
            other_elements = elements[:i] + elements[i+1:]

            for oe in other_elements:
                if parent_of_another(current_element, oe):
                    return (current_element, oe)

        return None

    # Create a new list
    result = list(elements)

    while(True):
        ep = find_element_with_parent(result)

        if ep is None:
            break
        elif (atomic_element is not None and ep[1].tag_name == atomic_element
                    and ep[0].tag_name != ep[1].tag_name):
            result.remove(ep[0])
        else:
            result.remove(ep[1])

    return result


# Returns HTML elements that may correspond to a modal dialog 'close' button
def get_close_dialog_elements(driver):

    result = []

    # Find a div with z-index set to discover close elements within
    script = ''
    with open('zindex.js', 'r') as jsfile:
        script = jsfile.read()

    container = driver.execute_script(script)

    if container is not None:

        iframe = False
        if (container.tag_name.lower() == 'iframe'):
            driver.switch_to.frame(container)
            iframe = True

        # Elements that might contain a 'close' option
        close_elements = ['button', 'img', 'span', 'a', 'div']

        for ce in close_elements:
            xpath = './/%s[@*[contains(.,\'close\')]]' % ce

            if iframe:
                elements = driver.find_elements_by_xpath(xpath)
            else:
                elements = container.find_elements_by_xpath(xpath)

            # Only consider those elements that are visible and
            # have a height set
            result.extend(filter(lambda x: x.is_displayed() and
                                x.value_of_css_property('display') != 'none'
                                and (x.value_of_css_property('height') != 'auto'
                                or x.value_of_css_property('height') != 'auto'),
                                elements))

        if iframe:
            driver.switch_to.default_content()

    return (parent_removal(result), container, iframe)


# Attempts to close a modal dialog if it succeeds in finding one, and returns
# a count of the number of elements clicked in the process
def close_dialog(driver):
    (close_dialog_elements, container, iframe) = get_close_dialog_elements(driver)

    if len(close_dialog_elements) == 0:
        return 0
    else:
        for ce in close_dialog_elements:
            try:
                if iframe:
                    driver.switch_to.frame(container)

                print driver.current_url, "\t", ce.get_attribute('outerHTML')
                ce.click()

                if iframe:
                    driver.switch_to.default_content()

            except:
                pass

    return len(close_dialog_elements)


# Return a list with no duplicates
def unique(element_list):
    return list(set(element_list))
