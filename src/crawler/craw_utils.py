import ipaddress
import io
import json
from tld import get_fld
from urlparse import urlparse
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

MAX_FILENAME_LEN = 128


def dump_as_json(obj, json_path):
    with open(json_path, 'w') as f:
        json.dump(obj, f, indent=2)


def write_to_file(file_path, txt):
    with io.open(file_path, 'w', encoding='utf-8') as f:
        f.write(txt)


# https://stackoverflow.com/a/7406369
def safe_filename_from_url(url):
    keepcharacters = ('.', '_', '-')
    return "".join(c for c in url if c.isalnum() or
                   c in keepcharacters).rstrip()[:MAX_FILENAME_LEN]


def get_tld_or_host(url):
    if not url.startswith("http"):
        url = 'http://' + url

    try:
        return get_fld(url, fail_silently=False)
    except Exception:
        hostname = urlparse(url).hostname
        try:
            ipaddress.ip_address(hostname)
            return hostname
        except Exception:
            return None


def move_to_element(driver, element):
    try:
        ActionChains(driver).move_to_element(element).perform()
    except WebDriverException:
        pass
