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

    def upload_media(self):
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

        s3 = self.aws_connection()
        for media_url in tqdm(filename_dict, desc="Uploading: "):
            doc = filename_dict[media_url][0]
            filename = filename_dict[media_url][1]

            content_type = guess_type(filename)[0]
            if not content_type:
                # content type could not be determined
                content_type = constants.UNK_CONTENT_TYPE
            s3_filename = str(uuid4())
            # NOTE: this should match the path in EmbeddedMediaDownloader.save_images()
            filepath = os.path.join(constants.IMAGE_DOWNLOAD_FILEPATH, filename)

            if os.path.exists(filepath):
                # data not previously uploaded
                s3.upload_file(
                    filepath,
                    constants.BUCKET,
                    s3_filename,
                    ExtraArgs={"ContentType": content_type},
                )
                s3_url = f"https://{constants.BUCKET}.s3.{constants.REGION_NAME}.amazonaws.com/{s3_filename}"

                # update domain to something else
                coll.update_one(
                    {"postID": doc["postID"]},
                    {"$set": {"docs.$[elem].s3URL": s3_url}},
                    array_filters=[{"elem.doc_id": doc["doc_id"]}],
                )

                os.remove(filepath)

        self.log_adapter.info(f"Media upload succeeded!")

        return None

    def upload_articles(self, article_dl_temp_out_file_path):
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
