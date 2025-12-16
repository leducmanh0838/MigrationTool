import json

import requests
from requests_oauthlib import OAuth1Session

from config.settings import WordPressConfig
from src.connectors.write_connectors._base_write_connector import BaseWriteConnector


class WooCommerceConnector(BaseWriteConnector):
    def __init__(self, base_url, wq_username, wq_password, api_path: str = '/wp-json/wc/',
                 api_version: str = 'v3'):
        base_api_url = f"{base_url.rstrip('/')}{api_path.rstrip('/')}/{api_version.rstrip('/')}/"
        super().__init__(base_api_url)
        self.auth = (wq_username, wq_password)
        # self.entity_callables = {
        #     "product": self.create_product,
        #     "category": self.create_category,
        # }

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
        print("order_data: ", json.dumps(order_data, indent=4))
        return self._make_request("POST", endpoint, data=order_data, auth=self.auth)
    #
    # def get_products(self):
    #     endpoint = "products"
    #     return self._make_request("GET", endpoint)

    # def create_entity(self, entity_name: str, data):
    #     # Lấy hàm tương ứng ra
    #     entity_callable = self.entity_callables.get(entity_name)
    #
    #     # Cải tiến 1: Kiểm tra sự tồn tại của hàm
    #     if not entity_callable:
    #         raise ValueError(f"Entity '{entity_name}' is not supported for creation by WooCommerceConnector.")
    #
    #     # Cải tiến 2: Gọi hàm đã được kiểm tra
    #     # Dòng này hoạt động tốt vì cả create_product và create_category đều nhận tham số 'data'
    #     return entity_callable(data)
