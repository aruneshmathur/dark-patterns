import requests
import logging
from social_proof_api_endpoints import ENDPOINTS
from urlparse import urlparse

logger = logging.getLogger(__name__)
lf_handler = logging.FileHandler('social_proof_monitoring.log')
lf_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
lf_handler.setFormatter(lf_format)
logger.addHandler(lf_handler)
logger.setLevel(logging.INFO)


def remove_new_lines(_str):
    return _str.replace("\r\n", "").replace("\r", "").replace("\n", "")


UA_STRING = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"  # noqa


def build_headers(url, product_url="", custom_headers={}):
    headers = {
        "Host": urlparse(url).hostname,
        "User-Agent": UA_STRING,
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": url,
        "Content-Type": "text/plain",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0"
    }
    if custom_headers:
        headers.update(custom_headers)
    if product_url:
        headers["Origin"] = urlparse(product_url).scheme + "://" +\
            urlparse(product_url).hostname
    return headers


def main():
    for endpoint in ENDPOINTS:
        monitor_name = endpoint["name"]
        logger.info("Will check %s" % monitor_name)
        url = endpoint["url"]
        params = endpoint.get("params")
        data = endpoint.get("body")
        product_url = endpoint.get("product_url")
        headers = build_headers(url, product_url, endpoint.get("headers"))
        try:
            if endpoint.get("method") == "GET":
                r = requests.get(url, params=params, data=data,
                                 headers=headers)
            else:  # if not method is provided, do a POST
                r = requests.post(url, params=params, data=data,
                                  headers=headers)
            r.raise_for_status()
        except Exception:
            logger.exception("Exception while checking %s" % monitor_name)
        logger.info("API-Response:\t%s:\t%s\t%s" % (
            monitor_name, remove_new_lines(r.text), remove_new_lines(str(r.headers))))


if __name__ == '__main__':
    main()
