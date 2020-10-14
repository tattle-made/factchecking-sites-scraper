from sys import stdout
from time import sleep
import requests
from tqdm import tqdm
from PIL import Image
from io import BytesIO
import os
import pickle

import constants


class EmbeddedMediaDownloader:
    def __init__(self, coll, log_adapter):
        super().__init__()

        self.coll = coll
        self.log_adapter = log_adapter

        self.dl_image_out_file_path = os.path.join(
            constants.TEMP_PIPELINE_FILEPATH, constants.MEDIA_DL_IMAGE_FILENAMES
        )

    def get_all_images(self):
        # get all image docs
        # get a list of urls and postIDs
        pipeline = [
            {"$project": {"_id": 0, "docs": "$docs"}},
            {"$unwind": "$docs"},
            {"$match": {"docs.mediaType": "image", "docs.s3URL": None}},
            {
                "$project": {
                    "_id": 0,
                    "postID": "$docs.postID",
                    "doc_id": "$docs.doc_id",
                    "url": "$docs.origURL",
                }
            },
            #         {"$sample": {"size": 10}},
        ]
        query = list(self.coll.aggregate(pipeline))
        print(len(query))

        return query

    def save_images(self, query_images: list) -> None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Content-Type": "text/html",
        }

        if os.path.exists(self.dl_image_out_file_path):
            # TODO: Pipeline failure. Load snapshot and run pipeline
            self.log_adapter.info(
                "Previous pipeline failed. Processing previous pipeline first..."
            )
            self.log_adapter.debug(
                "Snapshot processing not yet implemented. First run pipeline from data uploader!"
            )
            return None

        if not os.path.exists(constants.IMAGE_DOWNLOAD_FILEPATH):
            os.makedirs(constants.IMAGE_DOWNLOAD_FILEPATH)

        url = None
        filename_dict = {}
        for doc in tqdm(query_images, desc="images: ", file=stdout):
            # doc: postID, doc_id, url
            try:
                sleep(1)

                url = doc["url"]
                r = requests.get(url, headers=headers)

                image = Image.open(BytesIO(r.content))

                # file params
                filename = url.split("/")[-1]
                if "?" in filename:
                    filename = filename.split("?")[0]
                filepath = os.path.join(constants.IMAGE_DOWNLOAD_FILEPATH, filename)

                # Save filenames for upload step
                filename_dict[url] = filename

                # save
                image.save(filepath)

            except Exception as e:
                self.log_adapter.error(f"Failed @{url}: {e}")

        with open(self.dl_image_out_file_path, "wb") as fp:
            pickle.dump(filename_dict, fp)

        return None

    def get_all_videos(self):
        # get all video docs
        # get a list of urls and postIDs

        pipeline = [
            {"$project": {"_id": 0, "docs": "$docs"}},
            {"$unwind": "$docs"},
            {"$match": {"docs.mediaType": "video", "docs.s3URL": None}},
            {
                "$project": {
                    "_id": 0,
                    "postID": "$docs.postID",
                    "doc_id": "$docs.doc_id",
                    "url": "$docs.origURL",
                }
            },
            #         {"$sample": {"size": 10}},
        ]
        query = list(self.coll.aggregate(pipeline))
        print(len(query))

        return query

    def save_videos(self, query_images: list) -> None:
        # TODO:
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Content-Type": "text/html",
        }

        # TODO: pipeline failure handling - see save_images() above

        url = None
        for doc in tqdm(query_images, desc="videos: ", file=stdout):
            # doc: postID, doc_id, url
            try:
                sleep(1)

                url = doc["url"]
                r = requests.get(url, headers=headers)

                image = Image.open(BytesIO(r.content))

                # file params
                filename = url.split("/")[-1]
                if "?" in filename:
                    filename = filename.split("?")[0]
                filepath = os.path.join(constants.MEDIA_DOWNLOAD_FILEPATH, filename)

                # save
                image.save(filepath)

            except Exception as e:
                print(f"failed @{url}: {e}")
        """

        return None
