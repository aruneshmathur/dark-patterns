import sys
from celery import Celery
from pyvirtualdisplay import Display
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded

from extract_links import logger, crawl, get_urls_from_csv, VIRT_DISPLAY_DIMS

MAX_SPIDERING_DURATION = 30*60  # in s
HARD_TIMEOUT = MAX_SPIDERING_DURATION + 30

app = Celery('celery_extract_links', broker='pyamqp://guest@localhost//')


@app.task(soft_time_limit=MAX_SPIDERING_DURATION, time_limit=HARD_TIMEOUT)
def call_crawl(url):
    try:
        display = Display(visible=False, size=VIRT_DISPLAY_DIMS)
        display.start()
        crawl(url)
    except SoftTimeLimitExceeded:
        logger.error("SoftTimeLimitExceeded while spidering %s" % url)
    except TimeLimitExceeded:
        logger.error("TimeLimitExceeded while spidering %s" % url)
    except Exception:
        logger.exception("Exception while crawling %s" % url)
    finally:
        if display:
            display.stop()


def main(csv_file):
    n_links = 0
    for url in get_urls_from_csv(csv_file):
        n_links += 1
        call_crawl.delay(url)
    logger.info("Finished adding %d URLs to celery queue" % n_links)


if __name__ == '__main__':
    main(sys.argv[1])
