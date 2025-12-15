import json

from config.settings import MagentoConfig
from src.connectors.read_connectors.magento_connector import MagentoConnector

magento = MagentoConnector(MagentoConfig.BASE_URL, token=MagentoConfig.ACCESS_TOKEN)

items = magento.get_all_products()
print(json.dumps(items, indent=2))

# woo = WooCommerceConnector(WooCommerceConfig.BASE_URL, WooCommerceConfig.CONSUMER_KEY, WooCommerceConfig.CONSUMER_SECRET)
#
# data={
#     "name": "Test thể loại 6",
#     "parent": 30,
#     "description": "Mô tả danh mục phụ kiện từ Magento.",
#     "meta_data": [
#         {
#             "key": "magento_category_id",
#             "value": "102"
#         }
#     ]
# }
# print(woo.create_category(data))