def close_dialog(driver):

    # Elements that might contain a 'close' option
    close_elements = ['button']

    for ce in close_elements:
        elements = driver.find_elements_by_tag_name(ce)

        for e in elements:
            # Ignore elements that are not displayed
            if not e.is_displayed():
                continue

            # Click if close in text
            if e.text == 'close':
                e.click()
                return

            # Retrieve a key, value pair of HTML attributes for this element
            # See: https://stackoverflow.com/questions/27307131/selenium-webdriver-how-do-i-find-all-of-an-elements-attributes
            attributes = driver.execute_script('''var items = {};
            for (index = 0; index < arguments[0].attributes.length; ++index) {
                items[arguments[0].attributes[index].name] =
                    arguments[0].attributes[index].value
            };
            return items;''', e)

            if len(attributes) == 0:
                continue

            for key, val in attributes.items():
                # Collapse list into one string
                if isinstance(val, list):
                    val = ''.join(str(elem) for elem in val)

                val = val.lower()

                # Click if close in key or value
                if 'close' in key or 'close' in val:
                    e.click()
                    return
