from pymongo import MongoClient
from pymongo.collection import Collection
import uuid


def get_collection(scraping_url: str, db_name: str, coll_name: str) -> Collection:
    mongo_url = scraping_url
    cli = MongoClient(mongo_url)
    db = cli[db_name]
    collection = db[coll_name]

    return collection


# note: priorSchema uses postID as index, and DocSchema uses doc_id
def get_doc_schema(
    doc_id=None,
    post_id=None,
    domain=None,
    orig_url=None,
    s3_url=None,
    possible_lang=None,
    is_good_prior=[0, 0],
    media_type=None,
    content=None,
    now_date=None,
    now_date_utc=None,
):
    # schema for an individual doc inside a news article
    if doc_id is None:
        doc_id = uuid.uuid4().hex
    doc = {
        "doc_id": doc_id,  # unique id
        "postID": post_id,  # same as postID above
        "domain": domain,  # news site such as: altnews.in | factly.in, same as domain above
        "origURL": orig_url,  # orig scraped url, same as postURL
        "s3URL": s3_url,  # url in s3
        "possibleLangs": possible_lang,  # possible languages in media, user input from source of data
        "isGoodPrior": is_good_prior,  # no of [-ve votes, +ve votes]
        "mediaType": media_type,  # ['text', 'image', 'video', 'audio']
        "content": content,  # text, if media_type = text or text in image/audio/video
        "nowDate": now_date,  # date of scraping, same as date_accessed
        "nowDate_UTC": now_date_utc,
    }

    return doc


def get_story_schema(
    post_id=None,
    post_url=None,
    domain=None,
    headline=None,
    date_accessed=None,
    date_accessed_utc=None,
    date_updated=None,
    date_updated_utc=None,
    author=None,
    docs=[],
):
    # schema for a news story/article
    if post_id is None:
        post_id = uuid.uuid4().hex

    post = {  # a post is a unique article
        "postID": post_id,  # unique post ID
        "postURL": post_url,  # link that was scraped. This will NOT be unique if scraped again at a later date
        "domain": domain,  # domain such as altnews/factly
        "headline": headline,  # headline text
        "date_accessed": date_accessed,  # date scraped
        "date_accessed_UTC": date_accessed_utc,
        "date_updated": date_updated,  # later of date published/updated
        "date_updated_UTC": date_updated_utc,  # later of date published/updated
        "author": author,
        "docs": docs,
    }

    return post
