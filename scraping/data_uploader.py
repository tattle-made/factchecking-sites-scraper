import boto3
import os
from dotenv import load_dotenv
from tqdm import tqdm
from mimetypes import guess_type
from uuid import uuid4
import pickle

import db
import constants
import utils
from embedded_media_downloader import EmbeddedMediaDownloader

load_dotenv()


class DataUploader:
    def __init__(self, mode, log_adapter):
        super().__init__()

        self.mode = mode
        self.log_adapter = log_adapter

    def aws_connection(self):
        """
        Get AWS connection

        Returns:

        """
        access_id = os.environ["ACCESS_ID"]
        access_key = os.environ["ACCESS_KEY"]

        s3 = boto3.client(
            "s3",
            region_name="ap-south-1",
            aws_access_key_id=access_id,
            aws_secret_access_key=access_key,
        )

        return s3

    def upload_media(self) -> None:
        """
        Upload media to AWS S3 storage

        Returns: None

        """
        self.log_adapter.info(f"Uploading media...")

        # TODO: implement for videos++

        scraping_url = utils.get_scraping_url(self.mode)
        # TODO: dev vs. prod db
        coll = db.get_collection(
            scraping_url, constants.SCRAPING_DB_DEV, constants.SCRAPING_DB_COLL_STORIES
        )
        media_dl = EmbeddedMediaDownloader(coll, self.log_adapter)

        # get files to upload
        with open(media_dl.dl_image_out_file_path, "rb") as fp:
            filename_dict = pickle.load(fp)

        # get failed files list
        with open(media_dl.failed_dl_image_out_file_path, "rb") as fp:
            failed_filename_list = pickle.load(fp)

        # NOTE: handle bug for same multiple uploads
        # - www.factcrescendo.com/wp-content/uploads/2019/03/False.png?w=640&ssl=1
        # - www.factcrescendo.com/wp-content/uploads/2019/02/False-2.png?w=640&ssl=1
        # - https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/misleading-emoji.png
        # - https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/true-emoji.png
        # - https://www.vishvasnews.com/wp-content/themes/vishvasnews-advanced/images/false-emoji.png
        # - author images
        # TODO: update this list with change in websites or post authors
        img_bugs_list = [
            "False.png",
            "False-2.png",
            "misleading-emoji.png",
            "true-emoji.png",
            "false-emoji.png",
            "false-emoji.gif",
            "ashish.jpg",
            "urvashikapoor-150x150.jpg",
            "pallavi.jpg",
            "WhatsApp-Image-2018-07-24-at-10.39.25-AM.jpeg",
            "6a5dcaa7-6945-4866-bdac-d329f715e60c.jpeg",
            "abhishekprashar-150x150.jpg",
        ]

        img_bugs_dict = {}  # save s3 objects for reference

        s3 = self.aws_connection()
        for doc_idx in tqdm(filename_dict, desc="Uploading: "):
            # media_url = filename_dict[doc_idx][0]
            doc = filename_dict[doc_idx][1]
            filename = filename_dict[doc_idx][2]
            self.log_adapter.debug(f"Starting upload of file: {filename}")

            if filename in failed_filename_list:
                # file download had failed - update db s3url with error tag
                self.log_adapter.debug(f"failed file download. Updating s3url...")
                s3_url = constants.S3_MEDIA_ERR
                coll.update_one(
                    {"postID": doc["postID"]},
                    {"$set": {"docs.$[elem].s3URL": s3_url}},
                    array_filters=[{"elem.doc_id": doc["doc_id"]}],
                )
            else:
                content_type = guess_type(filename)[0]
                if not content_type:
                    # content type could not be determined
                    content_type = constants.UNK_CONTENT_TYPE

                # check if s3 object exists
                if filename in img_bugs_dict:
                    self.log_adapter.debug(
                        f"Updating collection with existing s3 object for file: {filename}"
                    )
                    s3_url = f"https://{constants.BUCKET}.s3.{constants.REGION_NAME}.amazonaws.com/{img_bugs_dict[filename]}"

                    # update domain to something else
                    self.log_adapter.debug(f"Updating s3url with uploaded image...")
                    res = coll.update_one(
                        {"postID": doc["postID"]},
                        {"$set": {"docs.$[elem].s3URL": s3_url}},
                        array_filters=[{"elem.doc_id": doc["doc_id"]}],
                    )
                    self.log_adapter.debug(
                        f"Mongo coll modified documents count:{res.modified_count}"
                    )
                else:
                    s3_filename = str(uuid4())

                    # save s3 object names
                    if filename in img_bugs_list:
                        img_bugs_dict[filename] = s3_filename

                    # NOTE: this should match the path in EmbeddedMediaDownloader.save_images()
                    filepath = os.path.join(constants.IMAGE_DOWNLOAD_FILEPATH, filename)

                    if os.path.exists(filepath):
                        # data not previously uploaded
                        res = s3.upload_file(
                            filepath,
                            constants.BUCKET,
                            s3_filename,
                            ExtraArgs={"ContentType": content_type},
                        )
                        self.log_adapter.debug(f"s3 file upload res: {res}")
                        s3_url = f"https://{constants.BUCKET}.s3.{constants.REGION_NAME}.amazonaws.com/{s3_filename}"

                        # update domain to something else
                        self.log_adapter.debug(f"Updating s3url with uploaded image...")
                        coll.update_one(
                            {"postID": doc["postID"]},
                            {"$set": {"docs.$[elem].s3URL": s3_url}},
                            array_filters=[{"elem.doc_id": doc["doc_id"]}],
                        )

                        os.remove(filepath)

        self.log_adapter.info(f"Media upload succeeded!")

        return None

    def upload_articles(self, article_dl_temp_out_file_path: str) -> None:
        self.log_adapter.info(f"Uploading articles...")

        scraping_url = utils.get_scraping_url(self.mode)
        # TODO: dev vs. prod db
        coll = db.get_collection(
            scraping_url, constants.SCRAPING_DB_DEV, constants.SCRAPING_DB_COLL_STORIES
        )

        # get files to upload
        with open(article_dl_temp_out_file_path, "rb") as fp:
            filepath_dict = pickle.load(fp)

        s3 = self.aws_connection()
        for article_url in tqdm(filepath_dict, desc="Uploading: "):
            filepath = filepath_dict[article_url]

            if os.path.exists(filepath):
                # data not previously uploaded
                s3_filename = str(uuid4())

                # upload
                s3.upload_file(filepath, constants.BUCKET, s3_filename, ExtraArgs={})
                s3_url = f"https://{constants.BUCKET}.s3.{constants.REGION_NAME}.amazonaws.com/{s3_filename}"

                os.remove(filepath)

                # update domain to something else
                coll.update_one(
                    {"postURL": article_url},
                    {"$set": {"s3URL": s3_url}},
                )

        self.log_adapter.info(f"Articles upload succeeded!")

        return None
