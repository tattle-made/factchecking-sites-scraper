import os
import shutil

import scraping.constants as constants
import scraping.utils as utils
from scraping.scraper import Scraper
import scraping.crawler as crawler


def test_article_parser():

    logger = utils.setup_logger(__name__)

    entity = constants.LOG_TAG_TEST
    log_adapter = utils.CustomAdapter(logger, {"entity": entity})

    site = "altnews.in"
    scraper = Scraper(
        crawl_site=site,
        mode=constants.MODE_LOCAL,
        if_sleep=True,
        scrape_from="13.10.2020",
    )

    crawl = crawler.Crawler(
        log_adapter,
        scraper.mode,
        scraper.crawler_temp_out_file_path,
        scraper.total_links_log,
        scraper.crawler_url,
        scraper.domain,
    )

    # TODO: add more urls to test parsing
    TEST_URL_LIST = [
        "https://www.altnews.in/video-from-romania-falsely-shared-as-muslims-spitting-inside-paris-metro-train/",
    ]

    # del previous test output folders: ".."
    if os.path.exists(constants.TEMP_PIPELINE_FILEPATH):
        shutil.rmtree(constants.TEMP_PIPELINE_FILEPATH)
    if os.path.exists(scraper.article_dl_out_folder):
        shutil.rmtree(scraper.article_dl_out_folder)

    # prep crawler output file
    crawl.save_urls(TEST_URL_LIST)

    # prep article download
    result = scraper.article_downloader()
    assert result is True
    if result:
        # test parser
        result = scraper.article_parser()
        assert result is True
        if result:
            contents = ""
            with open(scraper.err_links_log, "r") as f:
                contents = f.readlines()

            for link in TEST_URL_LIST:
                assert link not in contents
