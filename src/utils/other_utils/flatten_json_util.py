import json


def flatten_json(nested_json, separator='.', prefix=''):
    """
    Phẳng hóa JSON lồng nhau thành một từ điển một cấp.

    :param nested_json: Từ điển (dict) JSON đầu vào cần được làm phẳng.
    :param separator: Ký tự phân tách dùng để nối các khóa lồng nhau.
    :param prefix: Tiền tố hiện tại (dùng trong đệ quy).
    :return: Từ điển đã được làm phẳng.
    """
    flat_dict = {}

    for key, value in nested_json.items():
        # Tạo khóa mới
        new_key = f"{prefix}{separator}{key}" if prefix else key

        if isinstance(value, dict):
            # Nếu là dictionary lồng nhau, đệ quy
            flat_dict.update(flatten_json(value, separator, new_key))

        elif isinstance(value, list):
            # Nếu là list, chúng ta cần xử lý để tránh các cấu trúc lồng nhau.
            # Ta sẽ cố gắng trích xuất các giá trị đơn giản và bỏ qua các dict/list phức tạp.
            simple_values = []

            for index, item in enumerate(value):
                if isinstance(item, (str, int, float, bool, type(None))):
                    # Nếu phần tử là giá trị đơn giản, thêm vào danh sách
                    simple_values.append(str(item))
                elif isinstance(item, dict):
                    # Nếu là dict trong list, ta có thể làm phẳng nó và gán key là index.
                    # TUY NHIÊN, yêu cầu là KHÔNG có danh sách [] hay từ điển {}.
                    # Để đơn giản hóa, ta sẽ chỉ lấy các giá trị đơn giản từ dict này (nếu có)
                    # hoặc nối các giá trị đơn giản nhất lại.

                    # Cách tiếp cận: Trích xuất các giá trị đơn giản nhất từ dict con,
                    # nối chúng lại, hoặc bỏ qua nếu nó quá phức tạp.
                    sub_flat = flatten_json(item, separator, f"{new_key}[{index}]")
                    flat_dict.update(sub_flat)

                    # *Bỏ qua việc nối simple_values nếu đã làm phẳng dict con*

                # Bỏ qua list lồng trong list

            # Sau khi duyệt, nếu có các giá trị đơn giản, ta sẽ nối chúng lại.
            # Do đã xử lý trường hợp dict lồng, ta chỉ cần xử lý simple_values còn sót lại.
            if simple_values:
                # Nối các giá trị đơn giản thành một chuỗi
                flat_dict[new_key] = simple_values
            elif not simple_values and not any(isinstance(item, dict) for item in value):
                # Xử lý trường hợp list rỗng hoặc list chỉ chứa các cấu trúc phức tạp đã bị bỏ qua (vd: list lồng)
                flat_dict[new_key] = str(value)  # Có thể gán là chuỗi rỗng "" hoặc str(value)


        else:
            # Nếu là giá trị đơn giản (string, number, boolean, None), lưu vào từ điển phẳng
            flat_dict[new_key] = value

    return flat_dict


# ------------------------------------------------
# Dữ liệu JSON mẫu của bạn
nested_data = {
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
    "extension_attributes": {
        "website_ids": [
            1
        ],
        "category_links": [
            {
                "position": -63,
                "category_id": "27"
            },
            {
                "position": -219,
                "category_id": "32"
            }
        ],
        "stock_item": {
            "item_id": 1875,
            "product_id": 1875,
            "qty": 0,
            "is_in_stock": True,
        },
        "configurable_product_options": [
            {
                "id": 263,
                "attribute_id": "93",
                "label": "Color",
                "position": 1,
                "values": [
                    {
                        "value_index": 50
                    },
                    {
                        "value_index": 57
                    }
                ],
                "product_id": 1875
            }
        ],
        "configurable_product_links": [
            1873,
            1874
        ]
    },
    "product_links": [
        {
            "sku": "WP09",
            "link_type": "upsell",
            "linked_product_sku": "WP12",
        }
    ],
    "options": [],
    "media_gallery_entries": [
        {
            "id": 3149,
            "media_type": "image",
            "label": "",
            "position": 1,
            "file": "/w/p/wp09-black_main_1.jpg"
        }
    ],
    "tier_prices": [],
    "custom_attributes": [
        {
            "attribute_code": "image",
            "value": "/w/p/wp09-black_main_1.jpg"
        },
        {
            "attribute_code": "category_ids",
            "value": [
                "27",
                "32",
                "2"
            ]
        },
        {
            "attribute_code": "description",
            "value": "<p>Perfect as workout pants..."
        }
    ]
}

# Thực thi hàm
flat_data = flatten_json(nested_data)

# In kết quả đã được làm phẳng
print(json.dumps(flat_data, indent=4))