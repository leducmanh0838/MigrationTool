import json
import re


def unflatten_json(flat_json, separator='.'):
    """
    Giải ngược JSON phẳng (unflatten) thành JSON phức tạp, lồng nhau.

    :param flat_json: Từ điển (dict) JSON đã được làm phẳng đầu vào.
    :param separator: Ký tự phân tách được sử dụng để nối các khóa (mặc định là '.').
    :return: Từ điển đã được xây dựng lại cấu trúc lồng nhau.
    """
    nested_json = {}

    # Biểu thức chính quy để tìm kiếm chỉ mục mảng (ví dụ: '[0]')
    array_pattern = re.compile(r'\[(\d+)\]')

    # Hàm để chuyển đổi giá trị chuỗi thành kiểu dữ liệu phù hợp
    def convert_value(value):
        if isinstance(value, str):
            # Cố gắng chuyển đổi chuỗi số/boolean thành kiểu dữ liệu gốc
            value = value.strip()
            if value.lower() == 'true':
                return True
            if value.lower() == 'false':
                return False
            if value.lower() == 'null' or value == '':
                return None

            # Xử lý các chuỗi có vẻ là list đã được nối
            if ',' in value:
                # Nếu có dấu phẩy, có thể là list giá trị đơn giản. Cố gắng phân tách và chuyển đổi
                # Các list giá trị đơn giản (ví dụ: "1873, 1874")
                try:
                    return [int(v.strip()) if v.strip().isdigit() else v.strip() for v in value.split(',')]
                except:
                    # Nếu thất bại, giữ nguyên là chuỗi
                    pass

            # Cố gắng chuyển đổi sang số nguyên hoặc số thực
            try:
                if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                    return int(value)
                if '.' in value:
                    return float(value)
            except ValueError:
                pass

        # Giữ nguyên nếu không chuyển đổi được (bao gồm cả giá trị không phải chuỗi)
        return value

    for flat_key, flat_value in flat_json.items():
        current_level = nested_json

        # 1. Tách key thành các thành phần dựa trên dấu chấm (separator)
        key_parts = flat_key.split(separator)

        for i, part in enumerate(key_parts):
            # 2. Xử lý các chỉ mục mảng (ví dụ: 'category_links[0]' -> 'category_links', '0')
            match = array_pattern.search(part)

            if match:
                # Key chứa chỉ mục mảng, ví dụ: 'category_links[0]'
                list_key = part[:match.start()]
                list_index = int(match.group(1))

                # Cập nhật cấp độ hiện tại:

                # a. Đảm bảo key list_key là một list
                if list_key not in current_level:
                    current_level[list_key] = []

                # b. Mở rộng list nếu chỉ mục chưa tồn tại
                while len(current_level[list_key]) <= list_index:
                    # Nếu là thành phần cuối cùng của khóa (i == len(key_parts) - 1)
                    # Hoặc phần tử tiếp theo là một dictionary (vì list[index].key)
                    if i < len(key_parts) - 1 or part.endswith(']'):
                        # Nếu phần còn lại của khóa sẽ tạo thành một dictionary (vd: list[0].key)
                        current_level[list_key].append({})
                    else:
                        # Nếu list chứa các giá trị đơn giản (đã được xử lý ở bước 3)
                        current_level[list_key].append(None)  # Đặt tạm là None

                # c. Cập nhật cấp độ hiện tại để chuẩn bị cho phần key tiếp theo
                # Nếu đây là phần tử cuối cùng trong chuỗi key_parts
                if i == len(key_parts) - 1:
                    # Gán giá trị vào vị trí trong list
                    current_level[list_key][list_index] = convert_value(flat_value)
                else:
                    # Nếu list[index] là dictionary (vd: category_links[0])
                    # Chuyển cấp độ hiện tại vào dictionary tại vị trí list_index
                    current_level = current_level[list_key][list_index]

            else:
                # Key đơn giản, không phải chỉ mục mảng

                # Nếu đây là phần tử cuối cùng trong chuỗi key_parts
                if i == len(key_parts) - 1:
                    # Gán giá trị đã chuyển đổi
                    current_level[part] = convert_value(flat_value)
                else:
                    # Nếu chưa phải là phần tử cuối cùng, đảm bảo cấp độ tiếp theo là dictionary
                    if part not in current_level:
                        current_level[part] = {}
                    # Chuyển cấp độ hiện tại vào dictionary con
                    current_level = current_level[part]

    return nested_json


# ------------------------------------------------
# Dữ liệu JSON phẳng mẫu của bạn
flat_data = {
    "id": 1875,
    "sku": "WP09",
    "name": "Carina Basic Capri",
    "attribute_set_id": 10,
    "price": 0,
    "status": 1,
    "visibility": 4,
    "type_id": "configurable",
    "created_at": "2025-11-26 18:21:45",
    "updated_at": "2025-11-26 18:21:45",
    "extension_attributes.website_ids": "1",  # Dùng separator '.'
    "extension_attributes.category_links[0].position": -63,
    "extension_attributes.category_links[0].category_id": "27",
    "extension_attributes.category_links[1].position": -219,
    "extension_attributes.category_links[1].category_id": "32",
    "extension_attributes.stock_item.item_id": 1875,
    "extension_attributes.stock_item.product_id": 1875,
    "extension_attributes.stock_item.qty": 0,
    "extension_attributes.stock_item.is_in_stock": True,
    "extension_attributes.configurable_product_options[0].id": 263,
    "extension_attributes.configurable_product_options[0].attribute_id": "93",
    "extension_attributes.configurable_product_options[0].label": "Color",
    "extension_attributes.configurable_product_options[0].position": 1,
    "extension_attributes.configurable_product_options[0].values[0].value_index": 50,
    "extension_attributes.configurable_product_options[0].values[1].value_index": 57,
    "extension_attributes.configurable_product_options[0].product_id": 1875,
    "extension_attributes.configurable_product_links": "1873, 1874",  # List giá trị đơn giản
    "product_links[0].sku": "WP09",
    "product_links[0].link_type": "upsell",
    "product_links[0].linked_product_sku": "WP12",
    "options": "[]",
    "media_gallery_entries[0].id": 3149,
    "media_gallery_entries[0].media_type": "image",
    "media_gallery_entries[0].label": "",
    "media_gallery_entries[0].position": 1,
    "media_gallery_entries[0].file": "/w/p/wp09-black_main_1.jpg",
    "tier_prices": "[]",
    "custom_attributes[0].attribute_code": "image",
    "custom_attributes[0].value": "/w/p/wp09-black_main_1.jpg",
    "custom_attributes[1].attribute_code": "category_ids",
    "custom_attributes[1].value": "27, 32, 2",  # List giá trị đơn giản
    "custom_attributes[2].attribute_code": "description",
    "custom_attributes[2].value": "<p>Perfect as workout pants..."
}

# Thực thi hàm
nested_data = unflatten_json(flat_data, separator='.')

# In kết quả đã được giải ngược
print(json.dumps(nested_data, indent=4))