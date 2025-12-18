import logging
import time
from abc import ABC, abstractmethod
from typing import Tuple

import requests

from config.settings import AppConfig


class BaseConnector(ABC):
    def __init__(self, base_url: str, token: str = None, requester=requests):
        self.requester = requester
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if token:
            self.headers['Authorization'] = f'Bearer {token}'

    @abstractmethod
    def check_connection(self) -> Tuple[bool, str | None]:
        pass

    def _make_request(self, method: str, endpoint: str, params=None, data=None, auth=None, retries=3):
        """
        General request sending function, handling Retry and Rate Limit (HTTP 429)
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        attempt = 0
        while attempt < retries:
            try:
                response = self.requester.request(method,
                                                  url,
                                                  headers=self.headers,
                                                  params=params,
                                                  json=data,
                                                  auth=auth,
                                                  verify=AppConfig.VERIFY_SSL)
                if 200 <= response.status_code < 300:
                    return response.json()

                if response.status_code == 429 or response.status_code >= 500:
                    logging.warning(f"Gặp lỗi {response.status_code}. Đang chờ để thử lại...")
                    time.sleep(2 ** attempt)  # Exponential Backoff (chờ 1s, 2s, 4s...)
                    attempt += 1
                    if attempt >= retries:
                        # Raise lỗi luôn nếu thử quá 3 lần
                        response.raise_for_status()
                    continue

                # Các lỗi khác (400, 401, 404...) -> Raise lỗi luôn
                response.raise_for_status()

            except requests.exceptions.HTTPError as e:
                # BẮT VÀ RAISE LẠI HTTPError (từ 400-410, 412-428, 430-499)\
                raise e

            except requests.exceptions.RequestException as e:
                raise e
                # attempt += 1
                # time.sleep(2 ** attempt)

        logging.error(f"Thất bại sau {retries} lần thử tại {url}")
        return None

    @abstractmethod
    def get_platform_name(self) -> str:
        pass