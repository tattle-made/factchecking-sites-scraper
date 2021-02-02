import uuid
from datetime import date
from datetime import datetime
from dateutil.parser import parse
from typing import Callable
import json

from lxml.html import HtmlElement

import db


def get_metadata_quint(tree):
    data = tree.xpath('//script[@type="application/ld+json"]')[2].text
    json_data = json.loads(data)

    headline = json_data["headline"]
    datestr = parse(json_data["dateModified"]).strftime("%B %d, %Y")
    author = json_data["author"]
    author_name = author["name"]
    author_link = author["sameAs"]
    metadata = {
        "headline": headline,
        "author": author_name,
        "author_link": author_link,
        "date_updated": datestr,
    }

    return metadata


def get_content_quint(tree: HtmlElement):
    content = {
        "text": [],
        "video": [],
        "image": [],
        "tweet": [],
        "facebook": [],
        "instagram": [],
    }

    # videos
    videos = tree.xpath(
        '//div[@class="story-element story-element-youtube-video"]//iframe[@src]'
    )
    for v in videos:
        content["video"].append(v.get("src"))
    videos = tree.xpath(
        '//div[@class="story-element story-element-jsembed-dailymotion-video"]//iframe[@src]'
    )
    for v in videos:
        content["video"].append(v.get("src"))

    # images
    images = tree.xpath('//div[@class="story-element story-element-image"]/figure/img')
    for i in images:
        content["image"].append(i.get("data-src"))
        # content["image"].append("https:" + i.get_attribute("data-src"))

    body_elements = tree.xpath('//div[@class="story-element story-element-text"]//p')
    for i, x in enumerate(body_elements):
        text = x.text
        if text:
            content["text"].append(text)

    return content


def get_post_quint(
    get_tree: Callable[[str], HtmlElement],
    page_url: str,
    post_file_path: str,
    langs: list = [],
    domain: str = None,
    body_div: str = None,
    img_link: str = None,
    header_div: str = None,
    log_adapter=None,
):
    # from a page url, get a post dict ready for upload to mongo
    tree = get_tree(post_file_path)
    metadata = get_metadata_quint(tree)
    content = get_content_quint(tree)

    # fields
    post_id = uuid.uuid4().hex
    # uniform date format
    now_date = date.today().strftime("%B %d, %Y")
    now_date_utc = datetime.utcnow()
    date_updated = metadata["date_updated"]
    date_updated_utc = datetime.strptime(date_updated, "%B %d, %Y")

    author = {"name": metadata["author"], "link": metadata["author_link"]}

    docs = []
    for k, v in content.items():
        if not v:  # empty list
            continue
        if k == "text":
            content = "\n".join(v)
            doc = db.get_doc_schema(
                post_id=post_id,
                domain=domain,
                orig_url=page_url,
                possible_lang=langs,
                media_type=k,
                content=content,
                now_date=now_date,
                now_date_utc=now_date_utc,
            )
            docs.append(doc)
        else:
            content = None
            for url in v:
                doc = db.get_doc_schema(
                    post_id=post_id,
                    domain=domain,
                    orig_url=url,
                    possible_lang=langs,
                    media_type=k,
                    content=content,
                    now_date=now_date,
                    now_date_utc=now_date_utc,
                )
                docs.append(doc)

    post = db.get_story_schema(
        post_id=post_id,
        post_url=page_url,
        domain=domain,
        headline=metadata["headline"],
        date_accessed=now_date,
        date_accessed_utc=now_date_utc,
        date_updated=date_updated,
        date_updated_utc=date_updated_utc,
        author=author,
        s3_url=None,
        post_category=None,
        claims_review=None,
        docs=docs,
    )

    return post
