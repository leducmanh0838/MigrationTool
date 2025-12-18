from abc import ABC, abstractmethod
from typing import Tuple, List

import requests

from src.connectors.abstract.base_connector import BaseConnector


# 1. Khai báo ReadBaseConnector là Lớp Trừu Tượng (Kế thừa từ ABC)
class BaseReadConnector(BaseConnector, ABC):
    def __init__(self, base_url: str, token: str = None, requester=requests):
        super().__init__(base_url, token, requester)
        self.entity_batch_callables = {
            "product": self.get_product_batch,
            "category": self.get_category_batch,
            "customer": self.get_customer_batch,
            "order": self.get_order_batch,
        }
        self.entity_count_callables = {
            "product": self.get_product_count,
            "category": self.get_category_count,
            "customer": self.get_customer_count,
            "order": self.get_order_count,
        }

    @abstractmethod
    def get_product_batch(self, **kwargs) -> Tuple[List, bool]:
        pass

    @abstractmethod
    def get_category_batch(self, **kwargs) -> Tuple[List, bool]:
        pass

    @abstractmethod
    def get_customer_batch(self, **kwargs) -> Tuple[List, bool]:
        pass

    @abstractmethod
    def get_order_batch(self, **kwargs) -> Tuple[List, bool]:
        pass

    @abstractmethod
    def get_product_count(self, **kwargs) -> int:
        pass

    @abstractmethod
    def get_category_count(self, **kwargs) -> int:
        pass

    @abstractmethod
    def get_customer_count(self, **kwargs) -> int:
        pass

    @abstractmethod
    def get_order_count(self, **kwargs) -> int:
        pass

    def get_entity_batch(self, entity_name: str, **kwargs) -> Tuple[List, bool]:
        entity_callable = self.entity_batch_callables.get(entity_name)
        return entity_callable(**kwargs)

    def get_entity_count(self, entity_name: str, **kwargs):
        entity_callable = self.entity_count_callables.get(entity_name)
        return entity_callable(**kwargs)