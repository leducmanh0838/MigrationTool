import json
from typing import Tuple, List

from requests import RequestException

from config.settings import AppConfig
from src.connectors.abstract.base_read_connector import BaseReadConnector


# from src.models.magento_data_types import MagentoCategorySummaryData


class MagentoConnector(BaseReadConnector):
    def __init__(self, base_url: str, token: str = None, api_version='V1'):
        base_api_url = f"{base_url.rstrip('/')}/{api_version.rstrip('/')}/"  # https://magento.test/rest/V1/
        super().__init__(base_api_url, token)

    def check_connection(self) -> Tuple[bool, str | None]:
        endpoint = "store/storeConfigs"
        message = None
        try:
            response = self.requester.request('GET',
                                              f"{self.base_url}/{endpoint}",
                                              headers=self.headers,
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
        return "magento"

    def _get_entities_in_magento(self, endpoint, page=1, page_size=100, sort_field="entity_id", sort_dir="ASC",
                                 **kwargs) -> Tuple[List, bool]:
        params = {
            "searchCriteria[pageSize]": page_size,
            "searchCriteria[currentPage]": page,
            "searchCriteria[sortOrders][0][field]": sort_field,
            "searchCriteria[sortOrders][0][direction]": sort_dir
        }

        if kwargs:
            params.update(kwargs)

        response_data = self._make_request("GET", endpoint, params=params)
        items = response_data.get("items", [])
        total_count = response_data.get("total_count", 0)
        is_load_more = (page * page_size) < total_count
        return items, is_load_more

    def get_product_batch(self, **kwargs) -> Tuple[List, bool]:
        endpoint = "products"
        return self._get_entities_in_magento(endpoint, **kwargs)

    def get_category_batch(self, **kwargs) -> Tuple[List, bool]:
        endpoint = "categories/list"
        return self._get_entities_in_magento(endpoint, **kwargs)

    def get_customer_batch(self, **kwargs) -> Tuple[List, bool]:
        endpoint = "customers/search"
        return self._get_entities_in_magento(endpoint, **kwargs)

    def get_order_batch(self, **kwargs) -> Tuple[List, bool]:
        endpoint = "orders"
        return self._get_entities_in_magento(endpoint, **kwargs)
