"""Utils for the scaper v3 files"""

import logging
import os
import requests


def article_downloader(url, file_name):
    """If the file is present, it reads and returns the contents. If not, it
    downloads the URL and saves it in `file_name` then returns the contents

    Returns None and writes to the error log if the URl cannot be downloaded"""

    print("entered downloader")
    print(url)
    print(file_name)
    if os.path.exists(file_name):
        print("Article Already Downloaded. Loading from local.")
        with open(file_name, "rb") as thefile:
            html_text = thefile.read()
    else:
        try:
            response = requests.get(url)
            assert response.status_code % 100 == 2
            html_text = response.content
        except (requests.exceptions.ConnectionError, AssertionError) as exc:
            logging.exception(exc)
            logging.error("Article failed to download %s", url)
            return None
        with open(file_name, "wb") as thefile:
            thefile.write(html_text)

    return html_text
