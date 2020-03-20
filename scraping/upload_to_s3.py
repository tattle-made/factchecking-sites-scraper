from factchecking_news_sites import get_db
from time import sleep
from wget import download
from datetime import date
from os import remove, environ, listdir
import requests
from tqdm import tqdm
from PIL import Image
from uuid import uuid4
from io import BytesIO
from pymongo import MongoClient
from mimetypes import guess_type
from sys import stdout
import json
from dotenv import load_dotenv
load_dotenv()

# 3000+ images have different S3 urls across databases

def aws_connection():
    import boto3
    ACCESS_ID = environ['ACCESS_ID']
    ACCESS_KEY = environ['ACCESS_KEY']

    s3 = boto3.client('s3', region_name='ap-south-1',
                      aws_access_key_id=ACCESS_ID, aws_secret_access_key=ACCESS_KEY)

    return s3

def get_db():
    # setup db
    mongo_url = environ['SCRAPING_URL']
    cli = MongoClient(mongo_url)
    db = cli.factcheck_sites.stories
    print(db)
    
    return db

def get_all_images(db):
    # get all image docs
    # get a list of urls and postIDs
    pipeline = [
        {"$project": {"_id": 0, "docs": "$docs"}},
        {"$unwind": "$docs"},
        {"$match": {"docs.mediaType": "image", "docs.s3URL": None}},
        {"$project": {"_id": 0, "postID": "$docs.postID", "doc_id": "$docs.doc_id", "url": "$docs.origURL"}},
#         {"$sample": {"size": 10}},
    ]
    query = (list(db.aggregate(pipeline)))
    print(len(query))

    return query

def get_good_images(db):
    # get a list of urls and postIDs
    bad_sites = ['altnews.in/hindi', 'altnews.in', 'boomlive.in', 'bangla.boomlive.in', 'hindi.boomlive.in']
    pipeline = [
        {"$project": {"_id": 0, "docs": "$docs"}},
        {"$unwind": "$docs"},
        {"$match": {"docs.mediaType": "image", "docs.domain": {"$nin": bad_sites}}},
        {"$project": {"_id": 0, "postID": "$docs.postID", "doc_id": "$docs.doc_id", "url": "$docs.origURL"}},
#         {"$sample": {"size": 1}},
    ]
    query = (list(db.aggregate(pipeline)))
    print(len(query))

    return query    
    
if __name__ == '__main__':
    # setup
    db = get_db()
    s3 = aws_connection()
    query = get_all_images(db) #get_all_images(db)
    # constants
    headers = {
        'User-Agent': 
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 
        'Content-Type': 'text/html'
    }
    bucket = 'tattle-story-scraper'
    region_name = 'ap-south-1'
    
    print(date.today())
    
    # try: download url + upload to s3
    for doc in tqdm(query, desc="images: ", file=stdout):
        # doc: postID, doc_id, url
        try:
            sleep(1)

            url = doc['url']
            r = requests.get(url, headers=headers)

            image = Image.open(BytesIO(r.content))

            # file params
            filename = url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]
            ContentType = guess_type(filename)[0]
            S3filename = str(uuid4())
            filepath = f'./dls/{filename}'

            # save
            image.save(filepath)

            # upload
            s3.upload_file(filepath, bucket, S3filename, ExtraArgs={
                'ContentType': ContentType
            })
            s3URL = f'https://{bucket}.s3.{region_name}.amazonaws.com/{S3filename}'

            remove(filepath)

            # update domain to something else
            # https://api.mongodb.com/python/current/api/pymongo/collection.html?highlight=update#pymongo.collection.Collection.update_one
            db.update_one(
                {"postID": doc['postID']},
                {"$set": {"docs.$[elem].s3URL": s3URL}},
                array_filters=[{"elem.doc_id": doc['doc_id']}],
            )

#             # make the post request
#             url = "http://13.233.84.78:3003/api/posts"
#             payload = {"type" : "image", "data" : "", "filename": S3filename, "userId" : 164}
#             payload = json.dumps(payload)
#             headers = {
#                 'token': "78a6fc20-fa83-11e9-a4ad-d1866a9a3c7b",
#                 'Content-Type': "application/json",
#                 'cache-control': "no-cache",
#                 }
#             r = requests.post(url, data=payload, headers=headers)

        except Exception as e:
                print(f'failed @{url}: {e}')
