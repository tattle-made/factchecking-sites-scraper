import uuid
from datetime import date
from datetime import datetime
from typing import Callable

from lxml.html import HtmlElement

import db


def get_metadata_vishvasnews(tree):
    headline = tree.xpath("//h1")[0].text.strip("\r\n ")
    datestr = tree.xpath('//ul[@class="updated"]//li')[1].text.split("Updated: ")[-1]
    author = tree.xpath(
        '//div[@class="fact-approved"]//div[@class="author"]//ul[@class="author-details"]//li[@class="name"]/a'
    )
    author_name = author[0].text
    author_link = author[0].get("href")
    metadata = {
        "headline": headline,
        "author": author_name,
        "author_link": author_link,
        "date_updated": datestr,
    }

    return metadata


def get_content_vishvasnews(tree, body_elements, body_div=None):
    # return body content in a dict from page tree
    # english: body_div = 'div[@class="pf-content"]'
    # bengali: body_div = 'section[@id="mvp-content-main"]'
    # hindi: body_div = 'div[@class="pf-content"]'

    content = {
        "text": [],
        "video": [],
        "image": [],
        "tweet": [],
        "facebook": [],
        "instagram": [],
    }

    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    # video embed
    video_embed = tree.xpath(f"//{body_div}//video/source")
    for v in video_embed:
        content["video"].append(v.get("src"))
    # video youtube
    video_yt = tree.xpath(f"//{body_div}//iframe")
    for v in video_yt:
        content["video"].append(v.get("data-src"))
    # video fb
    fb = tree.xpath(
        '//figure[contains(@class, "wp-block-embed-facebook")]//div[@class="fb-video"]'
    )
    for f in fb:
        content["facebook"].append(f.get("data-href"))
    fb = tree.xpath('//figure[contains(@class, "wp-block-embed")]//a')
    # TODO: video_fb = tree.xpath('//figure[contains(@class, "wp-block-embed")]//a')
    """
    # first one is link, second is superfluous
    try:
        content["facebook"].append(video_fb[0].get("href"))
    except:
        pass
    """

    # images
    images = tree.xpath(f"//{body_div}/div/img")
    for i in images:
        if i.get("src"):
            content["image"].append(i.get("src"))
    images = tree.xpath(f"//{body_div}//figure/img")
    for i in images:
        if i.get("data-src"):
            content["image"].append(i.get("data-src"))

    # tweet
    tweets = tree.xpath('//blockquote[@class="twitter-tweet"]//a')
    for t in tweets:
        if t.text and any(m in t.text for m in months):
            content["tweet"].append(t.get("href"))

    # instagram
    insta = tree.xpath(
        '//figure[contains(@class, "wp-block-embed-instagram")]//blockquote'
    )
    for i in insta:
        content["instagram"].append(i.get("data-instgrm-permalink"))

    for i, x in enumerate(body_elements):
        text_content = x.text_content()
        if text_content:
            content["text"].append(text_content)

    return content


def get_post_vishvasnews(
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
    metadata = get_metadata_vishvasnews(tree)
    body_elements = tree.xpath(f"//{body_div}/*[self::p or self::h2]")
    content = get_content_vishvasnews(tree, body_elements, body_div=body_div)

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
