import uuid
from datetime import date
from datetime import datetime
from dateutil.parser import parse

from lxml.html import fromstring
from lxml.html import HtmlElement

import db


class ArticleParser:
    def __init__(self):
        super().__init__()

        self.log_adapter = None

    def get_tree(self, post_file_path: str) -> HtmlElement:
        """
        Get tree from html

        Args:
            post_file_path: str

        Returns: lxml.html.HtmlElement

        """

        with open(post_file_path, "r") as file:
            html = file.read()

        tree = fromstring(html)

        return tree

    # ================ ALTNEWS HELPER FUNCTIONS BEGIN ====================

    def get_metadata_altnews(self, tree: HtmlElement) -> dict:
        headline = tree.xpath("//header/h1")[0].text
        datestr = tree.xpath(
            '//*[@id="content-outer"]/article/div[1]/div/div/div/div/div/header/div/span/time[2]/text()'
        )
        if not len(datestr):
            # fallback to date posted
            datestr = tree.xpath(
                '//*[@id="content-outer"]/article/div[1]/div/div/div/div/div/header/div/span/time/text()'
            )
        datestr = datestr[0]
        author = tree.xpath(
            '//*[@id="content-outer"]/article/div[2]/div/div/div[1]/span/span/a[2]'
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

    def get_content_altnews(self, tree: HtmlElement, body_elements) -> dict:
        # return body content in a dict from page tree
        content = {"text": [], "video": [], "image": [], "tweet": []}

        video = tree.xpath("//iframe")
        if video:
            for v in video:
                content["video"].append(v.get("src"))

        for i, x in enumerate(body_elements):
            text_content = x.text_content()
            if text_content:
                content["text"].append(text_content)

            image = x.xpath("img")
            if image:
                for im in image:
                    content["image"].append(im.get("src"))

        return content

    def get_post_altnews(
        self,
        page_url: str,
        post_file_path: str,
        langs: list = [],
        domain: str = None,
        body_div: str = None,
        img_link: str = None,
        header_div: str = None,
        log_adapter=None,
    ) -> dict:
        # from a page url, get a post dict ready for upload to mongo
        self.log_adapter = log_adapter
        tree = self.get_tree(post_file_path)
        metadata = self.get_metadata_altnews(tree)
        body_elements = tree.xpath(
            "//div[contains(@class, herald-entry-content)]/*[self::p or self::h2 or self::iframe or self::twitter-widget]"
        )
        content = self.get_content_altnews(tree, body_elements)

        # fields
        post_id = uuid.uuid4().hex
        # uniform date format
        now_date = date.today().strftime("%B %d, %Y")
        now_date_utc = datetime.utcnow()
        date_updated = parse(metadata["date_updated"]).strftime("%B %d, %Y")
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
                        orig_url=page_url,
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
            docs=docs,
        )

        return post

    # ================ ALTNEWS HELPER FUNCTIONS END ====================
