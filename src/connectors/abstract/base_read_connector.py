from abc import ABC, abstractmethod

import requests

from src.connectors.abstract.base_connector import BaseConnector


# 1. Khai báo ReadBaseConnector là Lớp Trừu Tượng (Kế thừa từ ABC)
class BaseReadConnector(BaseConnector, ABC):
    def __init__(self, base_url: str, token: str = None, requester=requests):
        super().__init__(base_url, token, requester)
        self.entity_callables = {
            "product": self.get_all_products,
            "category": self.get_all_categories,
            "customer": self.get_all_customers,
            "order": self.get_all_orders,
        }

    @abstractmethod
    def get_all_products(self) -> list:
        pass

    @abstractmethod
    def get_all_categories(self) -> list:
        pass

    @abstractmethod
    def get_all_customers(self) -> list:
        pass

    @abstractmethod
    def get_all_orders(self) -> list:
        pass

    def get_all_entities(self, entity_name: str) -> list:
        entity_callable = self.entity_callables.get(entity_name)
        return entity_callable()
