from pymongo import MongoClient
from os import environ
from dotenv import load_dotenv
import requests
from time import sleep
from datetime import date
import json

load_dotenv()

def get_db():
    # setup db
    # replace with your own db
    mongo_url = environ['SCRAPING_URL']
    cli = MongoClient(mongo_url)
    db = cli.factcheck_sites.stories
    return db

def get_sample_docs(n, db):
    # get post request json
    pipeline = [
        {"$project": {"docs": "$docs", "url": "$postURL"}},
        {"$unwind": "$docs"},
        {"$match": {"docs.mediaType": "image", "docs.s3URL": {"$ne": None}}},
        {"$sample": {"size": n}},
        {"$project": {"_id": 0, "docId": "$docs.doc_id", "storyId": "$docs.postID", 
                      "type": "$docs.mediaType", "url": "$docs.s3URL", "filename": 
                      {"$arrayElemAt": [{"$split": ["$docs.s3URL", "/"]}, -1]}}},
        ]
    docs = list(db.aggregate(pipeline))
    
    return docs

def get_docs_not_on_portal(db):
    # test = db.find().limit(5)
    pipeline = [
        {"$project": {"docs": "$docs", "url": "$postURL"}},
        {"$unwind": "$docs"},
        {"$match": {"docs.mediaType": "image", "docs.s3URL": {"$ne": None}, "docs.onPortal": {"$ne": True}}},
       # {"$sample": {"size": 10}},
        {"$project": {"_id": 0, "docId": "$docs.doc_id", "storyId": "$docs.postID", 
                      "type": "$docs.mediaType", "url": "$docs.s3URL", "filename": 
                      {"$arrayElemAt": [{"$split": ["$docs.s3URL", "/"]}, -1]}}},
    ]

    docs = list(db.aggregate(pipeline))
   
    return docs
    
today = date.today()
print(today)    

# setup
n = 1
db = get_db()
token = ""  # CHANGE token
# docs = get_sample_docs(n, db)
docs = get_docs_not_on_portal(db)
print(docs)
# loop over all docs
for d in docs:
    try:
        # make the post request
        url = "https://archive-server-dev.tattle.co.in/api/fact-check-story"
        payload = d
        payload = json.dumps(payload)
        headers = {
            'token': token,
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            }
        r = requests.post(url, data=payload, headers=headers)
        if r.ok:
            db.update_one(
                {"docs.doc_id": d['docId']}, 
                {"$set": {"docs.$[elem].onPortal": True}},
                array_filters=[{"elem.doc_id": d['docId']}]
            )
            print(f'{d["docId"]}: {r}: {r.content}')
        else:
            print(f'{d["docId"]}: {r}: failed')
            break
        sleep(2)
                  
    except Exception as e:
        print(f'{d["docId"]}: {e}')
        break
                 
print('job complete')
