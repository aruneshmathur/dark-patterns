# Takes a list of HTML elements and returns a list such that none of the
# elements have their parents (up to but excluding <body>) in the returned list
def parent_removal(elements, atomic_element=None):

    # Find an element in the HTML list that also has its parent (up to but
    # excluding <body>) in the list
    # Returns None if no such element exists
    def find_element_with_parent(elements):
        for element in elements:
            current_element = element

            while(True):
                # Fetch the immediate parent of current element
                parent = current_element.find_element_by_xpath('..')

                if parent.tag_name == 'body':
                    break

                if parent in elements:
                    return (element, parent)

                current_element = parent

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

    # Find a div with z-index set to discover close elements within
    script = ''
    with open('zindex.js', 'r') as jsfile:
        script = jsfile.read()

    div = driver.execute_script(script)

    result = []

    # Elements that might contain a 'close' option
    close_elements = ['button', 'img', 'span', 'a']

    for ce in close_elements:
        xpath = '//%s[@*[contains(.,\'close\')]]' % ce
        elements = div.find_elements_by_xpath(xpath)

        # Only consider those elements that are visible and
        # have a height set
        result.extend(filter(lambda x: x.is_displayed() and
                                x.value_of_css_property('display') != 'none' and
                                (x.value_of_css_property('height') != 'auto' or
                                 x.value_of_css_property('height') != 'auto'),
                                 elements))

    return parent_removal(result)


# Attempts to close a modal dialog if it succeeds in finding one, and returns
# a count of the number of elements clicked in the process
def close_dialog(driver):
    close_dialog_elements = get_close_dialog_elements(driver)

    if len(close_dialog_elements) == 0:
        return 0
    else:
        for ce in close_dialog_elements:
            try:
                print ce.get_attribute('outerHTML')
                ce.click()
            except:
                pass

    return len(close_dialog_elements)


# Return a list with no duplicates
def unique(element_list):
    return list(set(element_list))
