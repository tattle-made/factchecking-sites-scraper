import os
import pickle
import time
from datetime import date
from numpy.random import randint
from tqdm import tqdm

import constants
import utils
import crawler
import db
from article_downloader import ArticleDownloader
from article_parser import ArticleParser
from embedded_media_downloader import EmbeddedMediaDownloader


class Scraper:
    """
    Main functionality to start scraping sites
    """

    def __init__(
        self, crawl_site: str, mode: str, if_sleep: bool = True, scrape_from: str = ""
    ):
        super().__init__()

        # setup logger
        self.logger = utils.setup_logger(__name__)

        # get site info
        site = constants.SITES[crawl_site]
        self.crawler_url = site.get("url", None)
        self.domain = site.get("domain", None)
        self.lang = site.get("langs", None)
        self.get_links_fn = site.get("getLinks", None)
        self.get_post_fn = site.get("getPost", None)
        self.body_div = site.get("body_div", None)
        self.img_link = site.get("img_link", None)
        self.header_div = site.get("header_div", None)

        self.mode = mode
        self.scrape_from = scrape_from
        self.if_sleep = if_sleep

        # setup logs
        self.today = date.today().strftime("%Y%m%d")
        self.site_str = self.domain.replace("/", "_")

        # TODO: create and save in logs dir
        # storyScraper_date.log: number of links scraped by crawler
        self.total_links_log = f"{self.site_str}_storyScraper_{self.today}.log"
        with open(self.total_links_log, "w") as f:
            f.write(f'{"url,domain,new_links"}')

        # storyScraper_date.err: all failed links - not downloaded by article_downloader
        self.err_links_log = f"{self.site_str}_storyScraper_{self.today}.err"
        with open(self.err_links_log, "w") as f:
            f.write(f'{"link,status,error"}')

        # crawler pipeline out files
        self.crawler_out_file_name = f"{constants.CRAWLED_URLS_BEGIN_FILENAME}{self.site_str}{constants.CRAWLED_URLS_FILE_EXTENSION}"
        self.crawler_out_file_path = os.path.join(
            constants.TEMP_PIPELINE_FILEPATH, self.crawler_out_file_name
        )

        # article downloader pipeline out files
        self.article_dl_out_folder = os.path.join(
            constants.DATA_RAW_FILEPATH, self.site_str
        )
        self.article_dl_out_file_name = f"{constants.DOWNLOADED_ARTICLES_BEGIN_FILENAME}{self.site_str}{constants.DOWNLOADED_ARTICLES_FILE_EXTENSION}"
        self.article_dl_out_file_path = os.path.join(
            constants.TEMP_PIPELINE_FILEPATH, self.article_dl_out_file_name
        )

        # parser pipeline out files
        self.article_parser_out_file_name = f"{constants.PARSED_ARTICLES_BEGIN_FILENAME}{self.site_str}{constants.PARSED_ARTICLES_FILE_EXTENSION}"
        self.article_parser_out_file_path = os.path.join(
            constants.TEMP_PIPELINE_FILEPATH, self.article_parser_out_file_name
        )

    def crawler(self) -> None:
        """
        Crawl site and get list of urls to scrape

        Returns: None

        """
        entity = constants.LOG_TAG_CRAWLER
        log_adapter = utils.CustomAdapter(self.logger, {"entity": entity})

        if os.path.exists(self.crawler_out_file_path):
            # TODO: Pipeline failure. Load snapshot and run pipeline
            log_adapter.info(
                "Previous pipeline failed. Processing previous pipeline first..."
            )
            log_adapter.debug(
                "Snapshot processing not yet implemented. First run pipeline from article downloader!"
            )
            return None

        log_adapter.info(f"Crawling {self.crawler_url} ...")

        time_last_scrape = utils.get_last_crawl_time(self.mode, self.crawler_url)

        crawl = crawler.Crawler(
            log_adapter,
            self.mode,
            self.crawler_out_file_path,
            self.total_links_log,
            self.crawler_url,
            self.domain,
        )

        if time_last_scrape == constants.MODE_INVALID:
            log_adapter.error("Invalid scraping mode: %", self.mode)
            return None
        elif time_last_scrape is None:
            # url has never been scraped
            log_adapter.info(f"{self.crawler_url} has never been crawled")
            if not self.scrape_from:
                log_adapter.error(
                    "Please provide a past date until (and including) which to crawl (dd.mm.yyyy)!"
                )
                return None
            else:
                log_adapter.info(f"Crawling from date {self.scrape_from}")
                url_list = getattr(crawl, self.get_links_fn)(
                    self.scrape_from, self.if_sleep
                )
                if len(url_list) == 0:
                    log_adapter.info(f"No new URLs to crawl in {self.crawler_url}")
                else:
                    url_list = crawl.get_new_urls(url_list)
                    crawl.save_urls(url_list)
                    crawl.update_log(len(url_list))
                    utils.save_crawl_time(self.crawler_url)
                    log_adapter.info(f"{self.crawler_url} crawl succeeded!")
        else:
            log_adapter.info(f"Crawling since last crawl date {time_last_scrape}")
            url_list = getattr(crawl, self.get_links_fn)(
                self.scrape_from, self.if_sleep
            )
            if len(url_list) == 0:
                log_adapter.info(f"No new URLs in {self.crawler_url}")
            else:
                url_list = crawl.get_new_urls(url_list)
                crawl.save_urls(url_list)
                crawl.update_log(len(url_list))
                utils.save_crawl_time(self.crawler_url)
                log_adapter.info(f"{self.crawler_url} crawl succeeded!")

        # TODO: save snapshot (class-level variables?) in the event of pipeline failure to process saved self.article_dl_out_file_path

        return None

    def article_downloader(self) -> None:
        """
        Download and save all urls crawled for site

        Returns: None

        """
        entity = constants.LOG_TAG_ARTICLE_DOWNLOADER
        log_adapter = utils.CustomAdapter(self.logger, {"entity": entity})

        if os.path.exists(self.article_dl_out_file_path):
            # TODO: Pipeline failure. Load snapshot and run pipeline
            log_adapter.info(
                "Previous pipeline failed. Processing previous pipeline first..."
            )
            if os.path.exists(self.article_parser_out_file_path):
                log_adapter.info(
                    "Snapshot processing not yet implemented. Previous parsing was successful! First run the pipeline from embedded media downloader."
                )
            else:
                log_adapter.info(
                    "Snapshot processing not yet implemented. Previous parsing was NOT successful! First run the pipeline from article parser."
                )
            return None

        if not os.path.exists(self.crawler_out_file_path):
            log_adapter.error("Crawler output file does not exist! Run crawler first.")
            return None

        if not os.path.exists(self.article_dl_out_folder):
            os.makedirs(self.article_dl_out_folder)

        article_dl_out_dict = {}

        with open(self.crawler_out_file_path, "rb") as fp:
            url_list = pickle.load(fp)

        scraping_url = utils.get_scraping_url(self.mode)
        # TODO: dev vs. prod db
        coll = db.get_collection(
            scraping_url, constants.SCRAPING_DB_DEV, constants.SCRAPING_DB_COLL_STORIES
        )

        for url in tqdm(url_list, desc="links: "):
            if not coll.count_documents({"postURL": url}):
                # collection empty or url not in collection
                log_adapter.info(f"Saving post: {url}")

                article_dl = ArticleDownloader(log_adapter, self.article_dl_out_folder)
                file_path = article_dl.save_post(url, constants.RETRY_COUNT)

                article_dl_out_dict[url] = file_path

                time.sleep(randint(1, 5))
            else:
                log_adapter.info(f"skipping post: {url}, already in db")
                with open(self.err_links_log, "a") as f:
                    f.write(f"\n{url},failed,link in db")

        with open(self.article_dl_out_file_path, "wb") as fp:
            pickle.dump(article_dl_out_dict, fp)

        # NOTE: crawler output files no longer needed
        os.remove(self.crawler_out_file_path)

        # TODO: save snapshot (class-level variables?) in the event of pipeline failure to process saved self.article_dl_out_file_path

        log_adapter.info(f"{self.domain} article downloads succeeded!")

        return None

    def article_parser(self) -> None:
        """
        Parse downloaded posts

        Returns: None

        """
        entity = constants.LOG_TAG_ARTICLE_PARSER
        log_adapter = utils.CustomAdapter(self.logger, {"entity": entity})

        with open(self.article_dl_out_file_path, "rb") as fp:
            article_dl_out_dict = pickle.load(fp)

        parser = ArticleParser()

        scraping_url = utils.get_scraping_url(self.mode)
        # TODO: dev vs. prod db
        coll = db.get_collection(
            scraping_url, constants.SCRAPING_DB_DEV, constants.SCRAPING_DB_COLL_STORIES
        )

        for url in tqdm(article_dl_out_dict, desc="links: "):
            try:
                log_adapter.info(f"Parsing: {url}")

                file_name = article_dl_out_dict[url]
                # NOTE: this should match path of self.article_dl_out_file_path
                file_path = os.path.join(constants.TEMP_PIPELINE_FILEPATH, file_name)

                get_post = getattr(parser, self.get_post_fn)

                post = get_post(
                    url,
                    post_file_path=file_path,
                    langs=self.lang,
                    domain=self.domain,
                    body_div=self.body_div,
                    img_link=self.img_link,
                    header_div=self.header_div,
                    log_adapter=log_adapter,
                )

                coll.insert_one(post)

            except Exception as e:
                log_adapter.info(f"Failed: {url}: {e}")
                with open(self.err_links_log, "a") as f:
                    f.write(f"\n{url},failed,{e}")

        # NOTE: WE STILL NEED self.article_dl_out_file_path - DO NOT DELETE
        # TODO: save snapshot (class-level variables?) in the event of pipeline failure to process saved self.article_dl_out_file_path

        with open(self.article_parser_out_file_path, "wb") as fp:
            pickle.dump(constants.PARSE_SUCCESS, fp)

        log_adapter.info(f"{self.domain} article parsing succeeded!")

        return None

    def embedded_media_downloader(self):
        """
        Download embedded media from posts

        Returns: None

        """
        entity = constants.LOG_TAG_EMBEDDED_MEDIA_DOWNLOADER
        log_adapter = utils.CustomAdapter(self.logger, {"entity": entity})

        scraping_url = utils.get_scraping_url(self.mode)
        # TODO: dev vs. prod db
        coll = db.get_collection(
            scraping_url, constants.SCRAPING_DB_DEV, constants.SCRAPING_DB_COLL_STORIES
        )

        media_dl = EmbeddedMediaDownloader(coll, log_adapter)

        query_images = media_dl.get_all_images()
        media_dl.save_images(query_images)

        # TODO: enable video downloaded once decided whether it is appropriate to download videos
        # query_videos = media_dl.get_all_videos()
        # media_dl.save_videos(query_videos)

        # TODO: save snapshot (class-level variables?) in the event of pipeline failure to process saved self.article_dl_out_file_path

        return None

    def data_uploader(self):
        # TODO:
        # entity = constants.LOG_TAG_DATA_UPOADER
        # log_adapter = utils.CustomAdapter(self.logger, {"entity": entity})
        # TODO:
        #   - update in db - s3raw url after downloaded article upload
        #       - delete self.article_dl_out_file_path
        #       - delete self.article_parser_out_file_path
        #   - update in db - s3URL url after downloaded media upload
        #   - delete self.dl_image_out_file_path + video out file path
        return


site = "altnews.in"
# "altnews.in"
# "altnews.in/hindi"
# "thequint.com"
# "vishvasnews.com/hindi"
# "vishvasnews.com/english"
# "vishvasnews.com/punjabi"
# "vishvasnews.com/assamese"
scraper = Scraper(
    crawl_site=site, mode=constants.MODE_LOCAL, if_sleep=True, scrape_from="13.10.2020"
)
# scraper.crawler()
# scraper.article_downloader()
# scraper.article_parser()
scraper.embedded_media_downloader()
