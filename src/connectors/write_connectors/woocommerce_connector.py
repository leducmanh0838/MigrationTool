import json
from typing import Tuple

import requests
from requests import RequestException

from config.settings import WordPressConfig, AppConfig
from src.connectors.abstract.base_write_connector import BaseWriteConnector


class WooCommerceConnector(BaseWriteConnector):
    def __init__(self, base_url, wq_username, wq_password, api_path: str = '/wp-json/wc/',
                 api_version: str = 'v3'):
        base_api_url = f"{base_url.rstrip('/')}{api_path.rstrip('/')}/{api_version.rstrip('/')}/"
        super().__init__(base_api_url)
        self.auth = (wq_username, wq_password)

    def check_connection(self) -> Tuple[bool, str | None]:
        endpoint = "system_status"
        message = None
        try:
            response = self.requester.request('GET',
                                              f"{self.base_url}/{endpoint}",
                                              headers=self.headers,
                                              auth=self.auth,
                                              verify=AppConfig.VERIFY_SSL)

            if response.status_code == 200:
                return True, message
            elif response.status_code == 401:
                message = "Error 401: The API Key (Token) is incorrect or has expired."
            elif response.status_code == 404:
                message = "Error 404: URL is incorrect."
            else:
                message = f"Error {response.status_code}: Unknown error"

        except RequestException as e:
            message = f"Connection error: {e}"

        return False, message

    def get_platform_name(self):
        return "woo"

    def create_product(self, product_data):
        """
        Tạo sản phẩm mới trên Woo
        Endpoint: /wp-json/wc/v3/products
        """
        endpoint = "products"
        return self._make_request("POST", endpoint, data=product_data, auth=self.auth)

    def create_category(self, category_data):
        """
        Tạo thể loại mới trên Woo
        Endpoint: /wp-json/wc/v3/products/categories
        """
        endpoint = "products/categories"
        return self._make_request("POST", endpoint, data=category_data, auth=self.auth)

    def create_customer(self, customer_data):
        """
        Tạo thể loại mới trên Woo
        Endpoint: /wp-json/wc/v3/products/categories
        """
        endpoint = "customers"
        return self._make_request("POST", endpoint, data=customer_data, auth=self.auth)

    def send_reset_password_email(self, email):
        url = WordPressConfig.BASE_URL
        endpoint = 'wp-json/my-custom/v1/reset-password'
        requests.request(
            "POST", f"{url}/{endpoint}",
            json={"email": email})

    def create_order(self, order_data):
        """
        Tạo thể loại mới trên Woo
        Endpoint: /wp-json/wc/v3/products/categories
        """
        endpoint = "orders"
        return self._make_request("POST", endpoint, data=order_data, auth=self.auth)
