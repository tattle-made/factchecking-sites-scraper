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

        # get list of files
        # Inspiration: https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
        img_files = [
            f
            for f in os.listdir(constants.IMAGE_DOWNLOAD_FILEPATH)
            if os.path.isfile(os.path.join(constants.IMAGE_DOWNLOAD_FILEPATH, f))
        ]

        for doc in tqdm(query_images, desc="images: ", file=stdout):
            # doc: postID, doc_id, url
            filename = ""
            try:
                sleep(1)

                url = doc["url"]

                if url is None:
                    # NOTE: issue due to bug in earlier code
                    self.log_adapter.info(
                        f"Media url is None. Setting s3URL as error..."
                    )
                    s3_url = constants.S3_MEDIA_ERR
                    self.coll.update_one(
                        {"postID": doc["postID"]},
                        {"$set": {"docs.$[elem].s3URL": s3_url}},
                        array_filters=[{"elem.doc_id": doc["doc_id"]}],
                    )
                else:
                    # file params
                    if url.endswith("://"):
                        # handle valid filename eg https://i0.wp.com/www.altnews.in/wp-content/uploads/2017/04/electrification-percentages.jpg?resize=696%2C141http://
                        filename = url.split("/")[-3] + "//"
                    else:
                        filename = url.split("/")[-1]
                    if "?" in filename:
                        filename = filename.split("?")[0]

                    if filename == "RDESController":
                        # handle files served by boomlive servlet
                        # eg - https://bangla.boomlive.in/content/servlet/RDESController?command=rdm.Picture&app=rdes&partner=boomlivebn&type=7&sessionId=RDWEBCM4UOT387MUCCO9K206WYURB7TIJPR0S&uid=5780889mysxCnqsjTKn5C4C0mXDHoqhwayM7B9087027
                        url_split = url.split("uid=")
                        filename = url_split[1]

                    # check if filename exists in path (extension may have been appended later!)
                    # this operation will not be expensive as there will be few downloaded files if
                    #   - db is updated
                    #   - and scraper pipeline is run frequently
                    filename_match = [filename in x for x in img_files]
                    # check if filename match
                    file_match_count = filename_match.count(True)
                    is_match = False  # is_match will be false if there was partial or no filename match
                    if file_match_count:
                        # get list of file indices (multiple may exist due to partial filename matches)
                        img_idx_list = [
                            i
                            for i in range(len(filename_match))
                            if filename_match[i] is True
                        ]
                        for img_idx in img_idx_list:
                            if filename == img_files[img_idx]:
                                # perfect filename match
                                is_match = True
                                break
                            elif filename == img_files[img_idx].split(".")[0]:
                                # TODO: handle possible collisions
                                #   - some filenames contain '.' apart from extension
                                #   eg WhatsApp-Image-2018-07-24-at-10.39.25-AM.jpeg
                                # TODO: add filename extension if required
                                #   - issue if running media downloader again and file extension has been appended
                                # filename perfect match without extension
                                is_match = True
                                break

                    if is_match:
                        self.log_adapter.info(
                            f"Skipping {filename} download. File already exists."
                        )
                    else:
                        self.log_adapter.debug(f"requesting image...")
                        r = requests.get(url, headers=headers)  # NOTE: THIS MAY FAIL
                        self.log_adapter.debug(f"opening image...")
                        image = Image.open(
                            BytesIO(r.content)
                        )  # NOTE: this  may fail - cannot identify image file (format)

                        # saving fails if there is no file extension
                        if len(filename.split(".")) == 1:
                            # TODO: handle possible filename without extensions
                            #   - some filenames contain '.' apart from extension
                            #   eg WhatsApp-Image-2018-07-24-at-10.39.25-AM.jpeg
                            # add image type extension
                            self.log_adapter.debug(
                                f"img format: {image.format.lower()}"
                            )
                            filename = f"{filename}.{image.format.lower()}"
                        self.log_adapter.debug(f"filename: {filename}")

                        filepath = os.path.join(
                            constants.IMAGE_DOWNLOAD_FILEPATH, filename
                        )
                        image.save(filepath)

                    # Save filenames for upload step
                    filename_dict[url] = [doc, filename]

            except Exception as e:
                self.log_adapter.error(f"Failed @{url}: {e}")
                failed_file_list.append(filename)
                # add to dict for processing during data upload
                filename_dict[url] = [doc, filename]

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
