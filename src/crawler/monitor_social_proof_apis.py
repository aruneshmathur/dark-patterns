import requests
import logging
from social_proof_api_endpoints import ENDPOINTS


logger = logging.getLogger(__name__)
lf_handler = logging.FileHandler('social_proof_monitoring.log')
lf_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
lf_handler.setFormatter(lf_format)
logger.addHandler(lf_handler)
logger.setLevel(logging.INFO)


def remove_new_lines(_str):
    return _str.replace("\r\n", "").replace("\r", "").replace("\n", "")


def main():
    for endpoint in ENDPOINTS:
        monitor_name = endpoint["name"]
        logger.info("Will check %s" % monitor_name)
        url = endpoint["url"]
        params = endpoint.get("params")
        data = endpoint.get("body")
        headers = endpoint.get("headers")
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
        logger.info("API-Response:\t%s:\t%s" % (
            monitor_name, remove_new_lines(r.text)))


if __name__ == '__main__':
    main()
