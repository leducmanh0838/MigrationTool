def _find_default_address(addresses: list, is_billing: bool) -> dict | None:
    """
    Tìm địa chỉ mặc định (billing hoặc shipping) từ danh sách địa chỉ Magento.
    """
    # Dựa vào cờ default_billing hoặc default_shipping
    default_key = "default_billing" if is_billing else "default_shipping"

    for address in addresses:
        if address.get(default_key) is True:
            return address
    return None


def map_magento_addresses_to_woo_objects(magento_customer_data: dict, woo_customer_data: dict) -> dict:
    """
    Chuyển đổi danh sách địa chỉ Magento thành cấu trúc billing và shipping
    dạng đối tượng của WooCommerce.

    Args:
        magento_customer_data (dict): Đối tượng chứa key "addresses" (danh sách địa chỉ Magento).
        customer_email (str): Email của khách hàng (cần cho trường billing).

    Returns:
        dict: Từ điển chứa hai key chính: "billing" và "shipping" với dữ liệu đã ánh xạ.
    """

    addresses = magento_customer_data.get("addresses", [])

    # 1. Tìm các địa chỉ mặc định
    default_billing_address = _find_default_address(addresses, is_billing=True)
    default_shipping_address = _find_default_address(addresses, is_billing=False)

    if (default_billing_address is None) or (default_shipping_address is None):
        return

    # 2. Định nghĩa ánh xạ cơ bản (Magento Key : Woo Key)
    ADDRESS_MAP = {
        "firstname": "first_name",
        "lastname": "last_name",
        "city": "city",
        "postcode": "postcode",
        "country_id": "country",
        "telephone": "phone"  # Ánh xạ phone vào billing, shipping sẽ dùng lại nếu không có
    }

    def map_single_address(address: dict, is_billing: bool) -> dict:
        """ Ánh xạ một địa chỉ Magento đơn lẻ sang đối tượng Woo. """
        woo_address = {
            "first_name": "", "last_name": "", "company": "",
            "address_1": "", "address_2": "", "city": "",
            "postcode": "", "country": "", "state": "",
        }

        # Ánh xạ các trường cơ bản
        if address:
            for magento_key, woo_key in ADDRESS_MAP.items():
                if magento_key in address:
                    # Bỏ qua telephone nếu đang xử lý shipping, sẽ thêm sau
                    if woo_key == "phone" and not is_billing:
                        continue
                    woo_address[woo_key] = address[magento_key]

            # Xử lý trường Street (dạng list)
            street_list = address.get("street", [])
            woo_address["address_1"] = street_list[0] if len(street_list) > 0 else ""
            woo_address["address_2"] = street_list[1] if len(street_list) > 1 else ""

            # Xử lý trường Region/State
            region_data = address.get("region", {})
            if region_data and "region_code" in region_data:
                woo_address["state"] = region_data["region_code"]

        return woo_address

    # 3. Tạo đối tượng Billing
    billing_object = map_single_address(default_billing_address, is_billing=True)

    # Thêm trường email (Bắt buộc phải lấy từ dữ liệu Khách hàng gốc, không phải địa chỉ)
    billing_object["email"] = magento_customer_data.get("email")

    # 4. Tạo đối tượng Shipping
    shipping_object = map_single_address(default_shipping_address, is_billing=False)

    # 5. Xử lý trường Phone cho Shipping
    # WooCommerce không yêu cầu phone cho shipping, nhưng nếu có thể,
    # ta nên sử dụng lại phone từ billing nếu shipping không có.
    shipping_object["phone"] = default_shipping_address.get("telephone", billing_object.get("phone", ""))

    woo_customer_data["billing"] = billing_object
    woo_customer_data["shipping"] = shipping_object


magento_input_different_addresses = {
    "id": 3,
    "group_id": 1,
    "created_at": "2025-12-14 03:22:30",
    "updated_at": "2025-12-14 03:22:30",
    "created_in": "Default Store View",
    "dob": "1990-01-01",
    "email": "khachhangmoi@example.com",
    "firstname": "Nguyễn",
    "lastname": "Văn A",
    "store_id": 1,
    "website_id": 1,
    "addresses": [],
    "disable_auto_group_change": 0,
    "extension_attributes": {
        "is_subscribed": False
    }
}

woo_customer_data = {
    "first_name": "ten",
    "email": "customer_migrate_woo@example.com",
}
# Chạy hàm ánh xạ
map_magento_addresses_to_woo_objects(
    magento_input_different_addresses,
    woo_customer_data,
)

import json

print(json.dumps(woo_customer_data, indent=4))
