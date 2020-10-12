from time import sleep
import os
import logging
import json
from numpy.random import randint
from tqdm import tqdm

from selenium import webdriver

import constants

from dotenv import load_dotenv

load_dotenv()

gecko_driver_path = os.environ["GECKO_DRIVER_PATH"]


class CustomAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return "[%s] %s" % (self.extra["entity"], msg), kwargs


def setup_logger(name):
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    logger = logging.getLogger(name)

    # create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create file handler
    handler = logging.FileHandler(constants.LOG_FILE, "a", encoding=None, delay=True)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_scraping_url(mode: str):
    scraping_url = None
    if mode == constants.MODE_LOCAL:
        scraping_url = os.environ["SCRAPING_URL_LOCAL"]
    elif mode == constants.MODE_REMOTE:
        scraping_url = os.environ["SCRAPING_URL_REMOTE"]
    else:
        scraping_url = None

    return scraping_url


def get_local_time(url):
    """
    Get time when url was last scraped locally

    Args:
        url: domain to be scraped

    Returns: time in millis

    """
    time = None

    if os.path.exists(constants.SCRAPE_TIME_FILEPATH):
        # open file
        log_file = open(constants.SCRAPE_TIME_FILEPATH)

        scrape_time_dict = json.load(log_file)

        if url in scrape_time_dict:
            time = scrape_time_dict[url]

        log_file.close()

    return time


def get_remote_time(url):
    """
    Get time when url was last scraped on remote

    Args:
        url: domain to be scraped

    Returns: time in millis

    """
    # TODO: implement function
    time = None

    return time


def get_last_scrape_time(mode, url):
    """
    Get stored time when url was last scraped

    Args:
        mode: local, remote or invalid
        url: domain to be scraped

    Returns: time in millis

    """
    time = None

    # TODO: config ???
    if mode == constants.MODE_LOCAL:
        time = get_local_time(url)
    elif mode == constants.MODE_REMOTE:
        time = get_remote_time(url)
    else:
        time = constants.MODE_INVALID

    return time


# ================== SELENIUM HELPER FUNCTIONS BEGIN ==================


def setup_driver():
    # selenium scrape
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")

    # firefox profile
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.manager.showWhenStarting", False)

    # using firefox gecko driver
    driver = webdriver.Firefox(
        executable_path=gecko_driver_path, firefox_profile=profile, options=options
    )

    return driver


def get_driver(url, driver, wait_time=1):
    driver.get(url)
    driver.implicitly_wait(wait_time)  # gives an implicit wait for n seconds
    while driver.execute_script("return document.readyState") != "complete":
        pass

    return driver


def infinite_scroll(driver, page_count, do_sleep=True):
    # Modified Source: https://dev.to/mr_h/python-selenium-infinite-scrolling-3o12

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in tqdm(range(page_count), desc="links: "):
        # while count < page_count+1:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        if do_sleep:
            sleep(randint(10, 20))

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height


# ================== SELENIUM HELPER FUNCTIONS END ==================
