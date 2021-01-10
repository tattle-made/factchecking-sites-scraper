import utils
import constants
from scraper import Scraper

# setup logger
logger = utils.setup_logger(__name__)
log_adapter = utils.CustomAdapter(logger, {"entity": "SCRAPER"})

websites = [
    "altnews.in",
    "altnews.in/hindi",
    "thequint.com",
    "vishvasnews.com/hindi",
    "vishvasnews.com/english",
    "vishvasnews.com/punjabi",
    "vishvasnews.com/assamese",
]

for site in websites:
    scraper = Scraper(
        crawl_site=site,
        mode=constants.MODE_LOCAL,
        if_sleep=True,
        scrape_from="13.10.2020",
    )
    log_adapter.info(f"Scraping site: {site}")
    result = scraper.crawler()
    if result:
        result = scraper.article_downloader()
        if result:
            result = scraper.article_parser()
            if result:
                result = scraper.embedded_media_downloader()
                if result:
                    result = scraper.data_uploader()
                    if not result:
                        log_adapter.error("Data uploader failed!")
                else:
                    log_adapter.error("Embedded media downloader failed!")
            else:
                log_adapter.error("Article parser failed!")
        else:
            log_adapter.error("Article downloader failed!")
    else:
        log_adapter.error("Crawler failed!")
