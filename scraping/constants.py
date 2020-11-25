"""
Set constants
"""
import os

# Output data directory
DIR_UP_PATH = ".."

# File names
SCRAPE_TIME_FILENAME = "scrape_time.json"
CRAWLED_URLS_BEGIN_FILENAME = "crawled_urls_"
DOWNLOADED_ARTICLES_BEGIN_FILENAME = "downloaded_articles_"
PARSED_ARTICLES_BEGIN_FILENAME = "parsed_articles_"
MEDIA_DL_IMAGE_FILENAMES = "media_dl_image_filename.pkl"
MEDIA_DL_IMAGE_FAILED_FILENAMES = "media_dl_image_failed_filename.pkl"

CRAWLED_URLS_FILE_EXTENSION = ".pkl"
DOWNLOADED_ARTICLES_FILE_EXTENSION = ".pkl"
PARSED_ARTICLES_FILE_EXTENSION = ".pkl"

# other dir
TEMP_PIPELINE_OUTPUT = "temp_pipeline_output"
LOGS_DIR = "logs"

# data dir
DATA_DIR = "data"
DATA_RAW_DIR = "raw"
IMAGE_DOWNLOAD_DIR = "image_dl"
VIDEO_DOWNLOAD_DIR = "video_dl"

# paths
SCRAPE_TIME_FILEPATH = os.path.join(DIR_UP_PATH, SCRAPE_TIME_FILENAME)
TEMP_PIPELINE_FILEPATH = os.path.join(DIR_UP_PATH, TEMP_PIPELINE_OUTPUT)
DATA_RAW_FILEPATH = os.path.join(DIR_UP_PATH, DATA_DIR, DATA_RAW_DIR)
IMAGE_DOWNLOAD_FILEPATH = os.path.join(DATA_RAW_FILEPATH, IMAGE_DOWNLOAD_DIR)
VIDEO_DOWNLOAD_FILEPATH = os.path.join(DATA_RAW_FILEPATH, VIDEO_DOWNLOAD_DIR)

# log tags
LOG_TAG_CRAWLER = "CRAWLER"
LOG_TAG_ARTICLE_DOWNLOADER = "ARTICLE_DOWNLOADER"
LOG_TAG_ARTICLE_PARSER = "ARTICLE_PARSER"
LOG_TAG_EMBEDDED_MEDIA_DOWNLOADER = "EMBEDDED_MEDIA_DOWNLOADER"
LOG_TAG_DATA_FORMATTER = "DATA_FORMATTER"
LOG_TAG_DATA_UPOADER = "DATA_UPLOADER"
LOG_TAG_TEST = "TEST"

# scraping mode for saving data
MODE_LOCAL = "local"
MODE_REMOTE = "remote"
MODE_INVALID = "mode_invalid"

# log file name
LOG_FILE = "scraper.log"

# parse success pipeline temp file tag
PARSE_SUCCESS = "Parse Success!"

# MongoDB
SCRAPING_DB_DEV = "factcheck_sites_dev"
SCRAPING_DB_COLL_STORIES = "stories"

# times to retry downloading article
RETRY_COUNT = 3

# TODO: crawl page count
CRAWL_PAGE_COUNT = 1000

# data uploader
UNK_CONTENT_TYPE = "unk_content_type"

# s3 data uploader
BUCKET = "tattle-story-scraper"
REGION_NAME = "ap-south-1"

# s3 media err tag
S3_MEDIA_ERR = "ERR"

# sites config
SITES = {
    "altnews.in": {
        "url": "https://www.altnews.in",
        "langs": ["english"],
        "domain": "altnews.in",
        "getLinks": "get_historical_links_altnews",
    },
    "altnews.in/hindi": {
        "url": "https://www.altnews.in/hindi",
        "langs": ["hindi"],
        "domain": "altnews.in/hindi",
        "getLinks": "get_historical_links_altnews",
    },
    "boomlive.in": {
        "url": "https://www.boomlive.in/fake-news",
        "langs": ["english"],
        "domain": "boomlive.in",
        "body_div": 'div[@class="story"]',
        "img_link": "src",
    },
    "hindi.boomlive.in": {
        "url": "https://hindi.boomlive.in/fake-news",
        "langs": ["hindi"],
        "domain": "hindi.boomlive.in",
        "body_div": 'div[@class="story"]',
        "img_link": "src",
    },
    "bangla.boomlive.in": {
        "url": "https://bangla.boomlive.in/fake-news",
        "langs": ["bengali"],
        "domain": "bangla.boomlive.in",
        "body_div": 'div[@class="story"]',
        "img_link": "src",
    },
    "factly.in": {
        "url": "https://factly.in/category/fake-news",
        "langs": ["english", "telugu"],
        "domain": "factly.in",
        "body_div": "div[@itemprop='articleBody']",
    },
    "indiatoday.in": {
        "url": "https://www.indiatoday.in/fact-check",
        "langs": ["english"],
        "domain": "indiatoday.in",
        "header_div": "div[contains(@class,'node-story')]",
        "body_div": "div[contains(@itemprop,'articleBody')]",
    },
    "vishvasnews.com/hindi": {
        "url": "https://www.vishvasnews.com",
        "langs": ["hindi"],
        "domain": "vishvasnews.com/hindi",
        "body_div": "div[@class='lhs-area']",
        "getLinks": "get_historical_links_vishvasnews",
    },
    "vishvasnews.com/english": {
        "url": "https://www.vishvasnews.com/english",
        "langs": ["english"],
        "domain": "vishvasnews.com/english",
        "body_div": "div[@class='lhs-area']",
        "getLinks": "get_historical_links_vishvasnews",
    },
    "vishvasnews.com/punjabi": {
        "url": "https://www.vishvasnews.com/punjabi",
        "langs": ["punjabi"],
        "domain": "vishvasnews.com/punjabi",
        "body_div": "div[@class='lhs-area']",
        "getLinks": "get_historical_links_vishvasnews",
    },
    "vishvasnews.com/assamese": {
        "url": "https://www.vishvasnews.com/assamese",
        "langs": ["assamese"],
        "domain": "vishvasnews.com/assamese",
        "body_div": "div[@class='lhs-area']",
        "getLinks": "get_historical_links_vishvasnews",
    },
    "thequint.com": {
        "url": "https://www.thequint.com/news/webqoof",
        "langs": ["english"],
        "domain": "thequint.com",
        "getLinks": "get_historical_links_quint",
    },
}
