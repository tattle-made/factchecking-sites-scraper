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

        # NOTE: THESE PATHS SHOULD NOT BE DYNAMICALLY ASSIGNED BY VARIABLES
        # AS THEY ARE USED STATICALLY BY data_uploader.py
        self.dl_image_out_file_path = os.path.join(
            constants.TEMP_PIPELINE_FILEPATH, constants.MEDIA_DL_IMAGE_FILENAMES
        )
        # NOTE: THESE PATHS SHOULD NOT BE DYNAMICALLY ASSIGNED BY VARIABLES
        # AS THEY ARE USED STATICALLY BY data_uploader.py
        self.failed_dl_image_out_file_path = os.path.join(
            constants.TEMP_PIPELINE_FILEPATH, constants.MEDIA_DL_IMAGE_FAILED_FILENAMES
        )

    def get_all_images(self) -> list:
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

        return query

    def save_images(self, query_images: list) -> bool:
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
            return False

        if not os.path.exists(constants.IMAGE_DOWNLOAD_FILEPATH):
            os.makedirs(constants.IMAGE_DOWNLOAD_FILEPATH)

        url = None
        filename_dict = {}
        failed_file_list = []
        for doc in tqdm(query_images, desc="images: ", file=stdout):
            # doc: postID, doc_id, url
            filename = ""
            try:
                sleep(1)

                url = doc["url"]

                # file params
                if url.endswith("://"):
                    # handle valid filename eg https://i0.wp.com/www.altnews.in/wp-content/uploads/2017/04/electrification-percentages.jpg?resize=696%2C141http://
                    filename = url.split("/")[-3] + "//"
                else:
                    filename = url.split("/")[-1]
                if "?" in filename:
                    filename = filename.split("?")[0]
                filepath = os.path.join(constants.IMAGE_DOWNLOAD_FILEPATH, filename)

                # Save filenames for upload step
                filename_dict[url] = [doc, filename]

                if os.path.exists(filepath):
                    self.log_adapter.info(
                        f"Skipping {filename} download. File already exists."
                    )
                else:
                    r = requests.get(url, headers=headers)
                    image = Image.open(BytesIO(r.content))
                    # save
                    image.save(filepath)

            except Exception as e:
                self.log_adapter.error(f"Failed @{url}: {e}")
                failed_file_list.append(filename)

        with open(self.dl_image_out_file_path, "wb") as fp:
            pickle.dump(filename_dict, fp)

        with open(self.failed_dl_image_out_file_path, "wb") as fp:
            pickle.dump(failed_file_list, fp)

        return True

    def get_all_videos(self) -> list:
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

        return query

    def save_videos(self, query_images: list) -> bool:
        # TODO: save videos
        """
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
            return False

        if not os.path.exists(constants.IMAGE_DOWNLOAD_FILEPATH):
            os.makedirs(constants.IMAGE_DOWNLOAD_FILEPATH)

        url = None
        filename_dict = {}
        for doc in tqdm(query_images, desc="images: ", file=stdout):
            # doc: postID, doc_id, url
            try:
                sleep(1)

                url = doc["url"]

                # file params
                filename = ""
                if url.endswith("://"):
                    # handle valid filename eg https://i0.wp.com/www.altnews.in/wp-content/uploads/2017/04/electrification-percentages.jpg?resize=696%2C141http://
                    filename = url.split("/")[-3] + "//"
                else:
                    filename = url.split("/")[-1]
                if "?" in filename:
                    filename = filename.split("?")[0]
                filepath = os.path.join(constants.IMAGE_DOWNLOAD_FILEPATH, filename)

                if os.path.exists(filepath):
                    self.log_adapter.info(
                        f"Skipping {filename} download. File already exists."
                    )
                else:
                    r = requests.get(url, headers=headers)
                    image = Image.open(BytesIO(r.content))
                    # save
                    image.save(filepath)

                # Save filenames for upload step
                filename_dict[url] = [doc, filename]

            except Exception as e:
                self.log_adapter.error(f"Failed @{url}: {e}")

        with open(self.dl_image_out_file_path, "wb") as fp:
            pickle.dump(filename_dict, fp)
        """
        return True
