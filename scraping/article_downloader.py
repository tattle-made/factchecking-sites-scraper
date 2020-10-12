import os
import time
import requests

import utils


class ArticleDownloader:
    def __init__(self, log_adapter: utils.CustomAdapter, out_folder: str):
        super().__init__()

        self.log_adapter = log_adapter
        self.out_folder = out_folder

    def save_post(self, url: str, retry_count: int) -> str:
        """
        Save each post
        # TODO: currently assuming post does not have infinite scroll

        Args:
            url: str
            retry_count: int

        Returns:

        """
        # TODO: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Content-Type": "text/html",
        }

        count = 0
        while count < retry_count:
            try:
                response = requests.get(url, headers=headers)

                time_millis = int(time.time() * 1000)
                file_name = f'{time_millis}_{url.split("/")[-2]}.html'
                file_path = os.path.join(self.out_folder, file_name)

                with open(file_path, "w") as file:
                    file.write(response.text)

                return file_path
            except Exception as e:
                # TODO: add url to file for retry
                self.log_adapter.error(f"failed request: {e}")

            count += 1
