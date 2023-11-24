import os
import requests
import logging

logger = logging.getLogger(__name__)


class Notifications:
    @staticmethod
    def send_file(endpoint: str, file_name: str, file_path: str):
        logger.info("Sending notifications")
        response = requests.post(
            url=endpoint,
            data={"body": file_name},
            files={"file": open(file_path, "rb")},
        )
        logger.info(response.text)
