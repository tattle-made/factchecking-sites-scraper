from pymongo import MongoClient
from pymongo.collection import Collection
import uuid
from datetime import datetime


def get_collection(scraping_url: str, db_name: str, coll_name: str) -> Collection:
    mongo_url = scraping_url
    cli = MongoClient(mongo_url)
    db = cli[db_name]
    collection = db[coll_name]

    return collection


# note: priorSchema uses postID as index, and DocSchema uses doc_id
def get_doc_schema(
    doc_id: str = None,
    post_id: str = None,
    domain: str = None,
    orig_url: str = None,
    s3_url: str = None,
    possible_lang: list = None,
    is_good_prior: list = [0, 0],
    media_type: str = None,
    content: str = None,
    now_date: str = None,
    now_date_utc: datetime = None,
) -> dict:
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
    post_id: str = None,
    post_url: str = None,
    domain: str = None,
    headline: str = None,
    date_accessed: str = None,
    date_accessed_utc: datetime = None,
    date_updated: str = None,
    date_updated_utc: datetime = None,
    author: dict = None,
    s3_url: str = None,
    post_category=None,  # TODO:
    claims_review=None,  # TODO:
    docs: list = [],
) -> dict:
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
        "s3URL": s3_url,
        "post_category": post_category,
        "claims_review": claims_review,
        "docs": docs,
    }

    return post


def update_coll_schema_change(key):
    """
    Updates all documents in collection when new key is added

    Args:
        key: key added to collection schema

    Returns: None

    """
    # TODO: added s3url (article), claims_review, post_category
    return None
