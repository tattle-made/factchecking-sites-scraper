import pickle
import os
from time import time
from time import sleep
from datetime import datetime
from numpy.random import randint
from tqdm import tqdm

from lxml.html import fromstring

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
        more_posts_link = driver.find_elements_by_xpath('//div[@class="nav-links"]/a')[
            0
        ]

        articles = None
        # TODO: remove page count once crawling by date implemented
        while True and count < constants.CRAWL_PAGE_COUNT:
            driver.execute_script("arguments[0].scrollIntoView();", more_posts_link)

            articles = driver.find_elements_by_xpath("//div/h3/a")
            print(len(set(articles)))

            try:
                more_posts_link.click()
                print(count, " clicked!")
                count += 1
            except Exception:
                break

            if if_sleep:
                sleep(0.5)

            try:
                more_posts_link = driver.find_elements_by_xpath(
                    '//div[@class="nav-links"]/a'
                )[0]
            except Exception as e:
                print(f"Failed: no more posts: {e}")
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

        # TODO: remove page count once crawling by date implemented
        # day_count = self.get_scrape_days(scrape_date)

        for page in tqdm(range(constants.CRAWL_PAGE_COUNT), desc="pages: "):
            page_url = f"{self.crawler_url}/{page}"
            tree = utils.get_tree(page_url)
            if if_sleep:
                sleep(randint(1, 5))

            # 12 story layout
            # 1 link
            link = tree.xpath(
                "/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/div[1]/a"
            )
            url_list.append(link[0].get("href"))
            # 5 links
            links = tree.xpath('//div[contains(@class,"custom-story-card-4")]/a[@href]')
            for link in links:
                url_list.append(link.get("href"))
            # 1 link
            link = tree.xpath(
                "/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/div[3]/div[1]/a[2]"
            )
            url_list.append(link[0].get("href"))
            # 1 link
            link = tree.xpath(
                "/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/div[3]/div[2]/a[2]"
            )
            url_list.append(link[0].get("href"))
            # 4 links
            links = tree.xpath('//div[contains(@class,"custom-story-card-5")]/a[@href]')
            for link in links:
                url_list.append(link.get("href"))

        # get unique urls
        url_list = list(set(url_list))
        # append "/" to end of each url for article_downloader to function correctly
        url_list = list(map(lambda url: f"{url}/", url_list))

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
        utils.infinite_scroll(driver, constants.CRAWL_PAGE_COUNT, if_sleep)
        url_list = self.get_post_links_from_page_altnews(driver.page_source)

        """
        for _ in tqdm(range(1), desc="page: "):
            # TODO: write parser to get post dates for urls + stop parsing + remove older urls
            cur_links = self.get_post_links_from_page_altnews()
            url_list += cur_links
            if if_sleep:
                sleep(randint(10, 20))
        """

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
