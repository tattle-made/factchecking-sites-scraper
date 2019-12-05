from os import environ
from sys import argv, exit
from datetime import date
from dotenv import load_dotenv
from factchecking_news_sites import get_db, get_live_links, scraping_site_links, setup_driver
from factchecking_news_sites import get_post_altnews, get_historical_links_altnews, get_post_boomlive, get_historical_links_boomlive
from factchecking_news_sites import get_post_factly, get_historical_links_factly, get_post_indiatoday, get_historical_links_indiatoday
from factchecking_news_sites import get_post_vishvasnews, get_historical_links_vishvasnews, get_post_quint, get_historical_links_quint

load_dotenv()

def aws_connection():
    import boto3
    ACCESS_ID = environ['ACCESS_ID']
    ACCESS_KEY = environ['ACCESS_KEY']

    s3 = boto3.client('s3', region_name='ap-south-1',
                      aws_access_key_id=ACCESS_ID, aws_secret_access_key=ACCESS_KEY)

    return s3

print(date.today())
##############################################################
# siteparams
sites = {"altnews.in": {"url": "https://www.altnews.in",
                        "langs": ["english"],
                        "domain": "altnews.in",
                        "getLinks": get_historical_links_altnews,
                        "getPost": get_post_altnews},
         "altnews.in/hindi": {"url": "https://www.altnews.in/hindi",
                              "langs": ["hindi"],
                              "domain": "altnews.in/hindi",
                              "getLinks": get_historical_links_altnews,
                              "getPost": get_post_altnews},
         "boomlive.in": {"url": "https://www.boomlive.in/fake-news",
                         "langs": ["english"],
                         "domain": "boomlive.in",
                         "body_div": 'div[@class="story"]',
                         "img_link": "src",
                         "getLinks": get_historical_links_boomlive,
                         "getPost": get_post_boomlive},
         "hindi.boomlive.in": {"url": "https://hindi.boomlive.in/fake-news",
                               "langs": ["hindi"],
                               "domain": "hindi.boomlive.in",
                               "body_div": 'div[@class="story"]',
                               "img_link": "src",
                               "getLinks": get_historical_links_boomlive,
                               "getPost": get_post_boomlive},
         "bangla.boomlive.in": {"url": "https://bangla.boomlive.in/fake-news",
                                "langs": ["bengali"],
                                "domain": "bangla.boomlive.in",
                                "body_div": 'div[@class="story"]',
                                "img_link": "src",
                                "getLinks": get_historical_links_boomlive,
                                "getPost": get_post_boomlive},
         "factly.in": {"url": "https://factly.in/category/fake-news",
                       "langs": ["english", "telugu"],
                       "domain": "factly.in",
                       "body_div": "div[@itemprop='articleBody']",
                       "getLinks": get_historical_links_factly,
                       "getPost": get_post_factly},
         "indiatoday.in": {"url": "https://www.indiatoday.in/fact-check",
                           "langs": ["english"],
                           "domain": "indiatoday.in",
                           "header_div": "div[contains(@class,'node-story')]",
                           "body_div": "div[contains(@itemprop,'articleBody')]",
                           "getLinks": get_historical_links_indiatoday,
                           "getPost": get_post_indiatoday},
         "vishvasnews.com/hindi": {"url": "https://www.vishvasnews.com",
                                   "langs": ["hindi"],
                                   "domain": "vishvasnews.com/hindi",
                                   "body_div": "div[@class='lhs-area']",
                                   "getLinks": get_historical_links_vishvasnews,
                                   "getPost": get_post_vishvasnews},
         "vishvasnews.com/english": {"url": "https://www.vishvasnews.com/english",
                                   "langs": ["english"],
                                   "domain": "vishvasnews.com/english",
                                   "body_div": "div[@class='lhs-area']",
                                   "getLinks": get_historical_links_vishvasnews,
                                   "getPost": get_post_vishvasnews},
         "vishvasnews.com/punjabi": {"url": "https://www.vishvasnews.com/punjabi",
                                   "langs": ["punjabi"],
                                   "domain": "vishvasnews.com/punjabi",
                                   "body_div": "div[@class='lhs-area']",
                                   "getLinks": get_historical_links_vishvasnews,
                                   "getPost": get_post_vishvasnews},
         "vishvasnews.com/assamese": {"url": "https://www.vishvasnews.com/assamese",
                                   "langs": ["assamese"],
                                   "domain": "vishvasnews.com/assamese",
                                   "body_div": "div[@class='lhs-area']",
                                   "getLinks": get_historical_links_vishvasnews,
                                   "getPost": get_post_vishvasnews},
          "thequint.com": {"url": "https://www.thequint.com/news/webqoof",
                   "langs": ["english"],
                   "domain": "thequint.com",
                   "getLinks": get_historical_links_quint,
                   "getPost": get_post_quint}
        }

# parse args: which site to run
if len(argv) > 2:
    print('Enter one site only \n Usage: python live_scraping_cmd.py site')
    exit()
site = argv[1]    
if site not in sites.keys():
    print(f'site not configured \n options: {sites.keys()} \n Usage: python live_scraping_cmd.py site')
    exit()
    
# params
bucket = 'tattle-logs'
region_name = 'ap-south-1'
db = get_db()
s3 = aws_connection()

# setup logs
today = date.today().strftime("%Y%m%d")
# storyScraper_date.log: number of links scraped
site_str = site.replace('/','_')
csvLog = f'{site_str}_storyScraper_{today}.log'
with open(csvLog, 'w') as f:
    f.write(f'url,domain,new_links')
    
# storyScraper_date.err: all failed links
csvErr = f'{site_str}_storyScraper_{today}.err'
with open(csvErr, 'w') as f:
    f.write(f'link,status,error')

# run one site
s = sites[site]
url = s.get('url', None)
langs = s.get('langs', None)
domain = s.get('domain', None)
body_div = s.get('body_div', None)
header_div = s.get('header_div', None)
img_link = s.get('img_link', None)
getLinks = s.get('getLinks', None)
getPost = s.get('getPost', None)

# get links
links, _ = get_live_links(getLinks=getLinks, url=url, db=db, domain=domain)
with open(csvLog, 'a') as f:
    f.write(f'\n{url},{domain},{len(links)}')

scraping_site_links(getPost=getPost, links=links, db=db, langs=langs, 
                    domain=domain, csvErr=csvErr, body_div=body_div, 
                    header_div=header_div, img_link=img_link)

###############################################################
# upload csv
# ContentType = 'text/plain'
s3.upload_file(csvLog, bucket, csvLog)
s3.upload_file(csvErr, bucket, csvErr)