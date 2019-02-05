import re
import sys

START_REGEX = '([^a-zA-Z]*) - MainProcess\[MainThread\] - FirefoxExtension     - DEBUG   : Visit Id: (\d+)'
PRODUCT_INTERACTION_START = '([^a-zA-Z]*) - MainProcess\[Thread\-\d+ ?\] - screen_capture       - INFO    : Will start product interaction Visit Id: (\d+)'
PRODUCT_INTERACTION_END = '([^a-zA-Z]*) - MainProcess\[Thread\-\d+ ?\] - screen_capture       - INFO    : Will end product interaction Visit Id: (\d+)'
ATC_REGEX =  '([^a-zA-Z]*) - MainProcess\[Thread\-\d+ ?\] - screen_capture       - INFO    : Clicked to add to cart Visit Id: (\d+)'
CART_REGEX = '([^a-zA-Z]*) - MainProcess\[Thread\-\d+ ?\] - screen_capture       - INFO    : Clicked to view cart Visit Id: (\d+)'
CHECKOUT_REGEX = '([^a-zA-Z]*) - MainProcess\[Thread\-\d+ ?\] - screen_capture       - INFO    : Clicked to checkout Visit Id: (\d+)'
END_REGEX = '([^a-zA-Z]*) - MainProcess\[Thread\-\d+ ?\] - screen_capture       - (INFO|ERROR)    : Will quit on [a-zA-Z:/]* Visit Id: (\d+)'

if __name__ == '__main__':
    sessions = {}

    with open(sys.argv[1]) as f:
        for line in f.readlines():

            match = re.search(START_REGEX, line)
            if match is not None:
                groups = match.groups()
                assert str(groups[1]) not in sessions.keys()

                sessions[str(groups[1])] = {'start': groups[0]}
                continue

            match = re.search(PRODUCT_INTERACTION_START, line)
            if match is not None:
                groups = match.groups()
                assert sessions[str(groups[1])] is not None

                sessions[str(groups[1])]['interaction_start'] = groups[0]
                continue

            match = re.search(PRODUCT_INTERACTION_END, line)
            if match is not None:
                groups = match.groups()
                assert sessions[str(groups[1])] is not None

                sessions[str(groups[1])]['interaction_end'] = groups[0]
                continue

            match = re.search(ATC_REGEX, line)
            if match is not None:
                groups = match.groups()
                assert sessions[str(groups[1])] is not None

                sessions[str(groups[1])]['add_to_cart'] = groups[0]
                continue

            match = re.search(CART_REGEX, line)
            if match is not None:
                groups = match.groups()
                assert sessions[str(groups[1])] is not None

                sessions[str(groups[1])]['view_cart'] = groups[0]
                continue

            match = re.search(CHECKOUT_REGEX, line)
            if match is not None:
                groups = match.groups()
                assert sessions[str(groups[1])] is not None

                sessions[str(groups[1])]['checkout'] = groups[0]
                continue

            match = re.search(END_REGEX, line)
            if match is not None:
                groups = match.groups()
                assert sessions[str(groups[1])] is not None

                sessions[str(groups[1])]['end'] = groups[0]
                continue

    for key in sessions.keys():
        print key, sessions[key]
