from src.connectors.read_connectors.read_base_connector import ReadBaseConnector


# from src.models.magento_data_types import MagentoCategorySummaryData


class MagentoConnector(ReadBaseConnector):
    def __init__(self, base_url: str, token: str = None, api_version='V1'):
        base_api_url = f"{base_url.rstrip('/')}/{api_version.rstrip('/')}/"  # https://magento.test/rest/V1/
        super().__init__(base_api_url, token)

    def get_platform_name(self):
        return "magento"

    def get_products(self, page=1, page_size=50) -> list:
        """
        Lấy danh sách sản phẩm từ Magento
        Endpoint: /V1/products
        """
        endpoint = "products"

        # Magento searchCriteria parameters
        params = {
            "searchCriteria[pageSize]": page_size,
            "searchCriteria[currentPage]": page,
            # Có thể thêm filter nếu cần
        }

        return self._make_request("GET", endpoint, params=params)

    def get_all_products(self, page_size=50) -> list:
        """
        Hàm Generator để lấy TOÀN BỘ sản phẩm (tự động loop qua các trang)
        """
        current_page = 1
        products = []
        while True:
            data = self.get_products(page=current_page, page_size=page_size)
            if not data or not data.get('items'):
                break

            for item in data['items']:
                products.append(item)

            # Kiểm tra xem đã hết trang chưa
            if len(data['items']) < page_size:
                break

            current_page += 1
        return products

    def get_all_categories(self):
        """
        Lấy tất cả Category từ Magento API và trả về dưới dạng list các MagentoCategoryData.
        """
        endpoint = "categories/list"
        params = {
            "searchCriteria[pageSize]": 0,  # lấy hết
        }

        return self._make_request("GET", endpoint, params=params).get("items")

    def get_all_customers(self):
        """
        Lấy tất cả Category từ Magento API và trả về dưới dạng list các MagentoCategoryData.
        """
        endpoint = "customers/search"
        params = {
            "searchCriteria[pageSize]": 0,  # lấy hết
        }

        return self._make_request("GET", endpoint, params=params).get("items")