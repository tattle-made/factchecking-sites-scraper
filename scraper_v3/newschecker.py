## Scraper Functions for Newsmeter
## 25 Feb 2021

from time import time, sleep
from datetime import date, datetime
from dateutil.parser import parse
from pyquery import PyQuery
import pytz
import json  #TODO: Discuss pickle vs json ; Decided JSON
from bson import json_util
from PIL import Image
from io import BytesIO
from tqdm import tqdm
from numpy.random import randint
from uuid import uuid4


from pymongo import MongoClient
from pymongo.collection import Collection

from selenium import webdriver
from lxml.html import fromstring
import requests
import boto3

import os
from dotenv import load_dotenv
load_dotenv()

## Decided: For Constants generate config file. Avoid domain specific functions in common config. 

# ============================== CONSTANTS  ===========================

MONGOURL = os.environ["SCRAPING_URL_REMOTE"] 
DB_NAME = os.environ["DB_NAME"]
COLL_NAME = os.environ["COLL_NAME"]
BUCKET = os.environ["BUCKET"]
REGION_NAME = os.environ["REGION_NAME"]

DEBUG = 1

CRAWL_PAGE_COUNT = 3
headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        "Content-Type": "text/html",
    }

FILE_PATH = "tmp/newschecker/"

newschecker_sites_dict = {
    "newschecker.in": {
        "url": "https://newschecker.in/fact-check",
        "langs": "english",
        "domain": "newschecker.in",
    },
    "newschecker.in/hi": {
        "url": "https://newschecker.in/hi/fact-check-hi",
        "langs": "hindi",
        "domain": "newschecker.in/hi",
    },
    "newschecker.in/bn": {
        "url": "https://newschecker.in/bn/fact-checks",
        "langs": "bengali",
        "domain": "newschecker.in/bn",
    },
    "newschecker.in/gu": {
        "url": "https://newschecker.in/gu/fact-checks-gu",
        "langs": "gujarati",
        "domain": "newschecker.in/gu",
    },
    "newschecker.in/mr": {
        "url": "https://newschecker.in/mr/fact-check-mr",
        "langs": "marathi",
        "domain": "newschecker.in/mr",
    },
    "newschecker.in/pa": {
        "url": "https://newschecker.in/pa/fact-check-pa",
        "langs": "punjabi",
        "domain": "newschecker.in/pa",
    },
    "newschecker.in/ta": {
        "url": "https://newschecker.in/ta/fact-check-ta",
        "langs": "tamil",
        "domain": "newschecker.in/ta",
    },
    "newschecker.in/ml": {
        "url": "https://newschecker.in/ml/fact-check-ml",
        "langs": "malayalam",
        "domain": "newschecker.in/ml",
    },
}



def get_collection(MONGOURL, DB_NAME, COLL_NAME):
    cli = MongoClient(MONGOURL)
    db = cli[DB_NAME]
    collection = db[COLL_NAME]

    return collection

def aws_connection():

    access_id = os.environ["ACCESS_ID"]
    access_key = os.environ["ACCESS_KEY"]

    s3 = boto3.client(
        "s3",
        region_name="ap-south-1",
        aws_access_key_id=access_id,
        aws_secret_access_key=access_key,
    )

    return s3
    
def get_tree(url):

    html = None                        
  
    try:
        html = requests.get(url)
    except Exception as e:
        print(f"failed request: {e}")

    html.encoding = "utf-8"
    tree = fromstring(html.content)
    return tree



def restore_unicode(mangled):
    return mangled.encode('latin1','ignore').decode('utf8', 'replace')


def crawler(crawl_url, lang_folder): 

    print("entered crawler")

    file_name = f'{lang_folder}url_list.json'
    if os.path.exists(file_name):
        print("site already been crawled. See ", file_name)
        with open(file_name, "r") as f:
            url_list = json.load(f)
    
    else:
        url_list = []

        coll = get_collection(MONGOURL, DB_NAME, COLL_NAME)

        for page in tqdm(range(CRAWL_PAGE_COUNT), desc="pages: "):
            page_url = f"{crawl_url}/page/{page+1}"
            print(page_url)
            tree = get_tree(page_url)
            
            if (tree == None):
                print("No HTML on Link")
                continue

            pq = PyQuery(tree)
            permalinks = pq.find("div.tdb_module_cat_grid_1>div.td-module-container>div.td-image-container>div.td-module-thumb>a")
            permalinks += pq.find("div.tdb_module_cat_grid_2>div.td-module-container>div.td-image-container>div.td-module-thumb>a")
            permalinks += pq.find("div.tdb_module_loop>div.td-module-container>div.td-image-container>div.td-module-thumb>a")   

            for pl in permalinks:
                link = pl.attrib['href']
                if 'javascript:void(0)' in link:   #these links should not be scraped
                    continue
                if coll.count_documents({"postURL": link}, {}):
                    print(link, "exists in collection")
                    continue
                else:
                    print(link, "new to collection")
                    url_list.append(link)
            sleep(randint(5,10))            
    
        url_list = list(set(url_list))
        with open(file_name, 'w') as f:
            json.dump(url_list,f)  
            
    return url_list



def article_downloader(url, sub_folder): 
    print("entered downloader")
    print(url)

    file = "file.html"
    file_name = os.path.join(sub_folder, file)
    print(file_name)  

    if os.path.exists(file_name):
        print("Article Already Downloaded. Loading from local.")
        with open(file_name, 'rb') as f:
            html_text = f.read()
    else:
        response = requests.get(url)
        html_text = response.content
        with open(file_name, "wb") as f:
            f.write(html_text)
    
    return html_text



def get_article_info(pq):

    headline = pq("h1.tdb-title-text").text()
    print(headline)
    datestr = pq("div.tdb-block-inner>time").attr['datetime']
    datestr = parse(datestr).astimezone(pytz.timezone('Asia/Calcutta')).strftime("%B %d, %Y")
    print(datestr)
    author_name = pq("div.tdb-author-name-wrap>a.tdb-author-name").text()
    print(author_name)
    author_link = pq("div.tdb-block-inner>a.tdb-author-photo")
    author_link = author_link.attr['href']
    print(author_link)
    article_info = {
        "headline": restore_unicode(headline),
        "author": author_name,
        "author_link": author_link,
        "date_updated": restore_unicode(datestr),
    }
    print(article_info)
    
    return article_info

def get_article_content(pq):
    
    content = {
        "text": [],
        "fb_post": [],
        "image": [],
        "tweet": [],
        "video": [],
        "youtube": [],
    }

    # text content
    content['text'] = restore_unicode(pq('div.tdb-block-inner>p').text())

    # images
    images = pq.find('div.td_block_wrap>div.tdb-block-inner>a>img.entry-thumb')
    images += pq.find('div.tdb-block-inner>figure.wp-block-gallery>ul.blocks-gallery-grid>li.blocks-gallery-item>figure>img')
    images += pq.find('div.tdb-block-inner>figure.wp-block-image>img')
    images += pq.find('div.wp-block-image>figure.aligncenter>img')
    images += pq.find('div.wp-block-media-text>figure.wp-block-media-text__media>img')
    images += pq.find('div.tdb-block-inner>p>img')
    for i in images:
            content["image"].append(i.attrib["src"])   
    
    #videos
    video = pq.find('div.tdb-block-inner>figure.wp-block-video>video')
    for v in video:
        content["video"].append(v.attrib["src"])
        
    #tweets
    tweets = pq.find('.twitter-tweet>a') 
    for t in tweets:
        content["tweet"].append(t.attrib['href'])
        
    #fb post
    fb = pq.find('.ose->iframe')
    for f in fb:
        content["fb_post"].append(f.attrib['src'])
        
    #youtube video
    yt = pq.find('.wp-block-embed__wrapper>iframe')
    for y in yt:
        content["youtube"].append(y.attrib['src'])
        
    return content
        
def convert_timestamp(item_date_object):
    if isinstance(item_date_object, (date, datetime)):
        return item_date_object.timestamp()

def article_parser(html_text, url, domain, lang, sub_folder):
    
    print("entered article_parser")
    file = "post.json"
    file_name = os.path.join(sub_folder, file)
    if os.path.exists(file_name):
        print("story has already been parsed.See ", file_name)
        with open(file_name, "r") as f:
            post = json.load(f)
    else:
        print("entered parser")
        pq = PyQuery(html_text)
        
        # generate post_id
        post_id = uuid4().hex

        article_info = get_article_info(pq)

        # uniform date format
        now_date = date.today().strftime("%B %d, %Y")
        now_date_utc = datetime.utcnow()
        date_updated = article_info["date_updated"]
        date_updated_utc = datetime.strptime(date_updated, "%B %d, %Y")

        author = {"name": article_info["author"], "link": article_info["author_link"]}  

        article_content = get_article_content(pq)
        docs = []
        for k, v in article_content.items():
            if not v:  # empty list
                continue
            
                        
            if k == "text":  
                doc_id = uuid4().hex
                doc = {
                    "doc_id": doc_id,
                    "postID": post_id,
                    "domain": domain,
                    "origURL": url, # for text content, URL is the URL of the story
                    "s3URL": None,
                    "possibleLangs": lang,
                    "mediaType": k,
                    "content": v,  # text, if media_type = text or text in image/audio/video
                    "nowDate": now_date,  # date of scraping, same as date_accessed
                    "nowDate_UTC": now_date_utc,
                    "isGoodPrior": None,  # no of [-ve votes, +ve votes] TODO: Discuss  Discussed: Look More
                }
                docs.append(doc)
            
            else:
                for media_url in v:
                    doc_id = uuid4().hex
                    print(doc_id)
                    doc = {
                        "doc_id": doc_id,
                        "postID": post_id,
                        "domain": domain,
                        "origURL": media_url,  # for images,videos URL is the URL of the media item.
                        "s3URL": None,
                        "possibleLangs": lang,
                        "mediaType": k,
                        "content": None,  # this field is specifically to store text content.
                        "nowDate": now_date,  # date of scraping, same as date_accessed
                        "nowDate_UTC": now_date_utc,
                        "isGoodPrior": None,  # no of [-ve votes, +ve votes] TODO: Discuss
                    }  
                    docs.append(doc)          

        post = {
            "postID": post_id,  # unique post ID
            "postURL": url,  
            "domain": domain,  # domain such as altnews/factly
            "headline": article_info["headline"],  # headline text
            "date_accessed": now_date,  # date scraped
            "date_accessed_UTC": now_date_utc,
            "date_updated": date_updated,  # later of date published/updated
            "date_updated_UTC": date_updated_utc,  # later of date published/updated
            "author": author,
            "post_category": None,
            "claims_review": None,
            "docs": docs,
        }

        print(post)


        json_data = json.dumps(post, default=convert_timestamp)
        with open(file_name, 'w') as f:
            f.write(json_data)

        
    return post 

def get_all_images(post,sub_folder):

    url = None
    filename_dict = {}

    for doc in post["docs"]:
        if (doc["mediaType"] == 'image'):
            url = doc["origURL"]
            if url is None:
                print("Media url is None. Setting s3URL as error...")
                doc["s3_url"] = "ERR"
            else:
                filename = url.split("/")[-1]
                
                r = requests.get(url)
                try:
                    image = Image.open(BytesIO(r.content)) 
                    if len(filename.split(".")) == 1:
                        filename = f"{filename}.{image.format.lower()}"
                    if image.mode in ("RGBA", "P"): 
                        image = image.convert("RGB")
                    imgfile=f'{sub_folder}/{filename}'
                    image.save(f'{sub_folder}/{filename}')
                    filename_dict.update({doc["doc_id"]: filename})
                except:
                    print("couldn't identify image file")
                
    print(filename_dict)
    return filename_dict


def media_downloader(post, sub_folder):
    print("entered media downloader")
    file_name = f'{sub_folder}/media_dict.json'
    
    if os.path.exists(file_name):
        print("media dictionary exists. Some media items may have been dowloaded. See ",file_name)
        with open(file_name, "r") as f:
            media_dict = json.load(f)
        
    else:    
        media_dict = get_all_images(post,sub_folder)
        json_data = json.dumps(media_dict, default=convert_timestamp)
        with open(file_name, 'w') as f:
            f.write(json_data)

    return media_dict

def data_uploader(post, media_dict, html_text, sub_folder):

    print("entered data uploader")

    coll = get_collection(MONGOURL, DB_NAME, COLL_NAME)
     
    if coll.count_documents({"postURL": post["postURL"]}, {}):
        print(post["postURL"], "already added to database. If you want to updatex media items, use separate script")
        return 1
                

    s3 = aws_connection()

    for doc in post["docs"]:
            if (doc["s3URL"] != None):
                print("Skipping upload. Doc has an existing s3_url:",doc["s3URL"])
                continue
            filename = media_dict.get(doc["doc_id"])
            if (filename != None):
                s3_filename = str(uuid4())
                res = s3.upload_file(
                            f'{sub_folder}/{filename}',
                            BUCKET,
                            s3_filename,
                            ExtraArgs={"ContentType": "unk_content_type"},
                        )
                s3_url = f"https://{BUCKET}.s3.{REGION_NAME}.amazonaws.com/{s3_filename}" 
                doc["s3URL"] = s3_url
                
            

            else:
                continue
    
  
    coll.insert_one(post)

    s3_html_name = post["postURL"]
    file = "file.html"
    res = s3.upload_file( os.path.join(sub_folder, file),
                          BUCKET,
                          s3_html_name,
                          ExtraArgs={"ContentType": "unk_content_type"},
                        )  

def main():
    print('Newschecker scraper initiated')
    
    newschecker_sites = ["newschecker.in","newschecker.in/hi","newschecker.in/bn","newschecker.in/gu","newschecker.in/mr","newschecker.in/pa","newschecker.in/ta","newschecker.in/ml"]

    
    
    for site in newschecker_sites:
        print(site)
        
        website = newschecker_sites_dict[site]
        print(website.get("domain"))
        lang_folder = f'newschecker_{website.get("langs")}/'
        if not os.path.exists(lang_folder):
            os.mkdir(lang_folder)
        links = crawler(website.get("url"), lang_folder)

        print(links)

    
        for link in links:
            sub_folder = f'{lang_folder}{link.split("/")[-1].split(".")[0]}'
            print(sub_folder)
        
            if not os.path.exists(sub_folder):
                os.mkdir(sub_folder)
            html_text = article_downloader(link, sub_folder)
            post = article_parser(html_text, link, website.get("domain"), website.get("langs"), sub_folder)
            media_dict = media_downloader(post, sub_folder)
            data_uploader(post, media_dict, html_text, sub_folder)
            if (DEBUG==0):
                shutil.rmtree  
            
        if (DEBUG==0):
            os.remove(f'{lang_folder}url_list.json')
            
if __name__ == "__main__":
    main()

