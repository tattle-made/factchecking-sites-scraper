from time import time
from typing import Optional
import os
import logging
import json

from selenium import webdriver
from lxml.html import fromstring
import requests

import constants

from dotenv import load_dotenv

load_dotenv()

gecko_driver_path = os.environ["GECKO_DRIVER_PATH"]


class CustomAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return "[%s] %s" % (self.extra["entity"], msg), kwargs


def setup_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    logger = logging.getLogger(name)

    # Prevent multiple print statements
    # https://stackoverflow.com/questions/6729268/log-messages-appearing-twice-with-python-logging
    logger.propagate = False

    # Prevent multiple print statements
    # Handlers need to have different var names to prevent multiple print statements
    if not logger.hasHandlers():
        # create console handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # create file handler
        file_handler = logging.FileHandler(
            constants.LOG_FILE, "a", encoding=None, delay=True
        )
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_scraping_url(mode: str) -> Optional[str]:
    scraping_url = None
    if mode == constants.MODE_LOCAL:
        scraping_url = os.environ["SCRAPING_URL_LOCAL"]
    elif mode == constants.MODE_REMOTE:
        scraping_url = os.environ["SCRAPING_URL_REMOTE"]
    else:
        scraping_url = None

    return scraping_url


def get_local_time(url: str) -> Optional[str]:
    """
    Get time when url was last scraped locally

    Args:
        url: domain to be scraped

    Returns: time in millis

    """
    time = None

    if os.path.exists(constants.SCRAPE_TIME_FILEPATH):
        # open file
        log_file = open(constants.SCRAPE_TIME_FILEPATH, "r")

        scrape_time_dict = json.load(log_file)

        if url in scrape_time_dict:
            time = scrape_time_dict[url]

        log_file.close()

    return time


def get_remote_time(url: str) -> Optional[str]:
    """
    Get time when url was last scraped on remote

    Args:
        url: domain to be scraped

    Returns: time in millis

    """
    # TODO: implement function
    time = None

    return time


def save_crawl_time(url: str) -> None:

    with open(constants.SCRAPE_TIME_FILEPATH, "w+") as log_file:
        if not os.path.getsize(constants.SCRAPE_TIME_FILEPATH):
            # file empty
            scrape_time_dict = {}
        else:
            scrape_time_dict = {json.load(log_file)}
            print(scrape_time_dict)

        current_time = int(time() * 1000)
        scrape_time_dict[url] = current_time

        json.dump(scrape_time_dict, log_file)

    return None


def get_last_crawl_time(mode: str, url: str) -> str:
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


def get_tree(url: str):
    # get the tree of each page
    # TODO: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        "Content-Type": "text/html",
    }
    html = None
    while True:
        try:
            html = requests.get(url, headers=headers)
            break
        except Exception as e:
            print(f"failed request: {e}")
    if "boomlive" in url:
        html.encoding = "utf-8"

    tree = fromstring(html.text)

    return tree


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


# ================== SELENIUM HELPER FUNCTIONS END ==================
