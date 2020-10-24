import pickle
import os
from time import time
from time import sleep
from datetime import datetime
from numpy.random import randint
from tqdm import tqdm

from lxml.html import fromstring

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

import db
import constants
import utils

from dotenv import load_dotenv

load_dotenv()


class Crawler:
    def __init__(
        self,
        log_adapter: utils.CustomAdapter,
        mode: str,
        crawler_out_file_path: str,
        total_links_log: str,
        crawler_url: str,
        domain: str,
    ):
        self.log_adapter = log_adapter
        self.mode = mode
        self.crawler_out_file_path = crawler_out_file_path
        self.total_links_log = total_links_log
        self.crawler_url = crawler_url
        self.domain = domain

    def get_new_urls(self, url_list: list) -> list:
        """
        Get URLs that do not exist in db for scraping

        Args:
            url_list: list of crawled urls

        Returns: list of crawled urls not in db

        """
        self.log_adapter.info("Getting urls not in db...")

        new_urls_list = []

        scraping_url = utils.get_scraping_url(self.mode)
        coll = db.get_collection(
            scraping_url, constants.SCRAPING_DB_DEV, constants.SCRAPING_DB_COLL_STORIES
        )

        for url in url_list:
            if not coll.count_documents({"postURL": url}, {}):
                # URL not in DB
                new_urls_list.append(url)

        return new_urls_list

    def save_urls(self, url_list: list) -> None:
        """
        Save list of urls

        Args:
            url_list: list of urls to save

        Returns: None

        """

        if not os.path.exists(constants.TEMP_PIPELINE_FILEPATH):
            os.mkdir(constants.TEMP_PIPELINE_FILEPATH)

        with open(self.crawler_out_file_path, "wb") as fp:
            pickle.dump(url_list, fp)

        return None

    def update_log(self, url_count: int) -> None:
        """
        Update log file with number of links scraped for url and domain

        Args:
            url_count: int

        Returns: None

        """
        with open(self.total_links_log, "a") as f:
            f.write(f"\n{self.crawler_url},{self.domain},{url_count}")

        return None

    def get_scrape_days(self, scrape_date: int) -> int:
        """
        Get number of days to scrape urls
        # TODO: use this once scraping by date implemented

        Args:
            scrape_date: int

        Returns: int

        """
        time_sec = int(time())
        dt_obj = datetime.strptime(scrape_date, "%d.%m.%Y")
        scrape_date_sec = int(dt_obj.timestamp())
        day_count = int((((time_sec - scrape_date_sec) / 60) / 60) / 24)

        # day_count should be 1 if scrape_date is current date - need to scrape current day too
        day_count += 1

        return day_count

    # ======================== VISHVASNEWS HELPER FUNCTIONS BEGIN ========================

    def get_historical_links_vishvasnews(
        self, scrape_date: int, if_sleep: bool = True
    ) -> list:
        # NOTE: need to run this with a GUI session
        # lang = ['assamese', 'english', 'hindi', 'urdu', 'punjabi']

        driver = utils.setup_driver()
        driver = utils.get_driver(self.crawler_url, driver)

        count = 0
        cookie_accept_button = driver.find_elements_by_xpath(
            "/html/body/div[11]/button"
        )[0]

        scraping_url = utils.get_scraping_url(self.mode)
        coll = db.get_collection(
            scraping_url, constants.SCRAPING_DB_DEV, constants.SCRAPING_DB_COLL_STORIES
        )

        # scroll to end of document to get cookie accept button
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # wait for 5 seconds for cookie accept button to load
        driver.implicitly_wait(5)
        try:
            cookie_accept_button.click()
            self.log_adapter.info(f"Cookie accepted!")
        except Exception as e:
            self.log_adapter.warning(f"Error crawling vishvas news links: {e}")

        articles = None
        do_crawl = True
        more_posts_xpath = '//div[@class="nav-links"]/a'
        # TODO: remove page count once crawling by date implemented
        while do_crawl and count < constants.CRAWL_PAGE_COUNT:

            # wait until element loaded into view
            ignored_exceptions = (
                NoSuchElementException,
                StaleElementReferenceException,
            )
            _ = WebDriverWait(driver, 0.5, ignored_exceptions=ignored_exceptions).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, more_posts_xpath)
                )
            )

            # load element every time for new page
            more_posts_link = driver.find_elements_by_xpath(
                '//div[@class="nav-links"]/a'
            )[0]
            coordinates_dict = more_posts_link.location_once_scrolled_into_view

            # scroll to a little above element to prevent element being covered by
            # <div class="top-strip"> (top bar) from the top
            # and <div class="wpgdprc wpgdprc-consent-bar"> (cookie accept button) from the bottom
            driver.execute_script(
                "window.scrollTo({}, {});".format(
                    coordinates_dict["x"], coordinates_dict["y"] - 40
                )
            )
            # driver.execute_script("arguments[0].scrollIntoView();", more_posts_link)

            articles = driver.find_elements_by_xpath("//div/h3/a")

            for a in set(articles):
                # stop scrolling if link in
                link = a.get_attribute("href")
                if coll.count_documents({"postURL": link}, {}):
                    # post already in db - stop crawling
                    self.log_adapter.info("Found older posts. Stopping crawl...")
                    do_crawl = False

            try:
                more_posts_link.click()
                self.log_adapter.info(f"{count}: clicked!")
                count += 1
            except Exception as e:
                self.log_adapter.warning(f"Error crawling vishvas news links: {e}")
                break

            if if_sleep:
                sleep(0.5)

            try:
                more_posts_link = driver.find_elements_by_xpath(
                    '//div[@class="nav-links"]/a'
                )[0]
            except Exception as e:
                self.log_adapter.info(f"No more posts: {e}")
                break

        links = []
        for a in set(articles):
            links.append(a.get_attribute("href"))
        links = list(set(links))

        driver.close()

        return links

    # ======================== VISHVASNEWS HELPER FUNCTIONS END ========================

    # ======================== QUINT HELPER FUNCTIONS BEGIN ========================

    def get_historical_links_quint(
        self, scrape_date: int, if_sleep: bool = True
    ) -> list:
        # get story links based on url and page range
        url_list = []

        scraping_url = utils.get_scraping_url(self.mode)
        coll = db.get_collection(
            scraping_url, constants.SCRAPING_DB_DEV, constants.SCRAPING_DB_COLL_STORIES
        )

        # TODO: remove page count once crawling by date implemented
        # day_count = self.get_scrape_days(scrape_date)

        do_crawl = True
        for page in tqdm(range(constants.CRAWL_PAGE_COUNT), desc="pages: "):
            if do_crawl:
                page_url = f"{self.crawler_url}/{page}"
                tree = utils.get_tree(page_url)
                if if_sleep:
                    sleep(randint(1, 5))

                # 12 story layout
                # 1 link
                link = tree.xpath(
                    "/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/div[1]/a"
                )
                link = link[0].get("href") + "/"
                if coll.count_documents({"postURL": link}, {}):
                    # post already in db - stop crawling
                    self.log_adapter.info("Found older posts. Stopping crawl...")
                    do_crawl = False
                else:
                    url_list.append(link)
                # 5 links
                links = tree.xpath(
                    '//div[contains(@class,"custom-story-card-4")]/a[@href]'
                )
                for link in links:
                    link = link.get("href") + "/"
                    if coll.count_documents({"postURL": link}, {}):
                        # post already in db - stop crawling
                        self.log_adapter.info("Found older posts. Stopping crawl...")
                        do_crawl = False
                    else:
                        url_list.append(link)
                # 1 link
                link = tree.xpath(
                    "/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/div[3]/div[1]/a[2]"
                )
                link = link[0].get("href") + "/"
                if coll.count_documents({"postURL": link}, {}):
                    # post already in db - stop crawling
                    self.log_adapter.info("Found older posts. Stopping crawl...")
                    do_crawl = False
                else:
                    url_list.append(link)
                # 1 link
                link = tree.xpath(
                    "/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/div[3]/div[2]/a[2]"
                )
                link = link[0].get("href") + "/"
                if coll.count_documents({"postURL": link}, {}):
                    # post already in db - stop crawling
                    self.log_adapter.info("Found older posts. Stopping crawl...")
                    do_crawl = False
                else:
                    url_list.append(link)
                # 4 links
                links = tree.xpath(
                    '//div[contains(@class,"custom-story-card-5")]/a[@href]'
                )
                for link in links:
                    # append "/" to end of each url for article_downloader to function correctly
                    link = link.get("href") + "/"
                    if coll.count_documents({"postURL": link}, {}):
                        # post already in db - stop crawling
                        self.log_adapter.info("Found older posts. Stopping crawl...")
                        do_crawl = False
                    else:
                        url_list.append(link)

        # get unique urls
        url_list = list(set(url_list))

        return url_list

    # ======================== QUINT HELPER FUNCTIONS END ========================

    # ======================== ALTNEWS HELPER FUNCTIONS BEGIN ========================

    def get_historical_links_altnews(
        self, scrape_date: int, if_sleep: bool = True
    ) -> list:
        """
        Get post urls for altnews.in
        TODO: MODIFY this function if site changes

        Args:
            scrape_date: epoch millis
            if_sleep: bool

        Returns: list of urls

        """
        url_list = []

        # TODO: remove page_count once crawling by date implemented
        # day_count = self.get_scrape_days(scrape_date)

        # infinite scrolling
        driver = utils.setup_driver()
        driver = utils.get_driver(self.crawler_url, driver)
        # NOTE: "Recent Posts" start nearly 1 page down, hence scroll a page more

        scraping_url = utils.get_scraping_url(self.mode)
        coll = db.get_collection(
            scraping_url, constants.SCRAPING_DB_DEV, constants.SCRAPING_DB_COLL_STORIES
        )

        do_crawl = True
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in tqdm(range(constants.CRAWL_PAGE_COUNT), desc="links: "):
            if do_crawl:
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # check to stop scrolling
                url_list = self.get_post_links_from_page_altnews(driver.page_source)
                for link in url_list:
                    if coll.count_documents({"postURL": link}, {}):
                        # post already in db - stop crawling
                        self.log_adapter.info("Found older posts. Stopping crawl...")
                        do_crawl = False

                # Wait to load page
                if if_sleep:
                    sleep(randint(10, 20))

                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    # If heights are the same it will exit the function
                    break
                last_height = new_height

        # utils.infinite_scroll(driver, constants.CRAWL_PAGE_COUNT, if_sleep)
        url_list = self.get_post_links_from_page_altnews(driver.page_source)

        driver.close()

        return url_list

    def get_post_links_from_page_altnews(self, page_src: str) -> list:
        """
        Get list of post urls
        # TODO: MODIFY this function if site changes

        Args:
            page_src:

        Returns:

        """
        tree = fromstring(page_src)
        all_links = tree.xpath("//h4/a[@href]")
        links = []
        for _, x in enumerate(all_links):
            links.append(x.get("href"))

        return links

    # ======================== ALTNEWS HELPER FUNCTIONS END ========================
