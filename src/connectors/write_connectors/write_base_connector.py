from abc import ABC, abstractmethod

import requests

from src.connectors.base_connector import BaseConnector


class WriteBaseConnector(BaseConnector, ABC):
    def __init__(self, base_url: str, token: str = None, requester=requests):
        super().__init__(base_url, token, requester)
        self.entity_callables = {
            "product": self.create_product,
            "category": self.create_category,
            "customer": self.create_customer,
        }

    @abstractmethod
    def create_product(self, data):
        pass

    @abstractmethod
    def create_category(self, data):
        pass

    @abstractmethod
    def create_customer(self, data):
        pass

    @abstractmethod
    def send_reset_password_email(self, email):
        pass

    def create_entity(self, entity_name: str, data):
        # Lấy hàm tương ứng ra
        entity_callable = self.entity_callables.get(entity_name)

        if not entity_callable:
            raise ValueError(f"Entity '{entity_name}' is not supported for creation by WooCommerceConnector.")

        return entity_callable(data)
