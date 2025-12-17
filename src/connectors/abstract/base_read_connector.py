from abc import ABC, abstractmethod
from typing import Tuple, List

import requests

from src.connectors.abstract.base_connector import BaseConnector


# 1. Khai báo ReadBaseConnector là Lớp Trừu Tượng (Kế thừa từ ABC)
class BaseReadConnector(BaseConnector, ABC):
    def __init__(self, base_url: str, token: str = None, requester=requests):
        super().__init__(base_url, token, requester)
        self.entity_callables = {
            "product": self.get_product_batch,
            "category": self.get_category_batch,
            "customer": self.get_customer_batch,
            "order": self.get_order_batch,
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

    def get_entity_batch(self, entity_name: str, **kwargs) -> Tuple[List, bool]:
        entity_callable = self.entity_callables.get(entity_name)
        return entity_callable(**kwargs)
