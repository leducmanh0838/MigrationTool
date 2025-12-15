import os

import yaml


def load_yaml_mappings(current_path, target_dict):
    """
    Đệ quy đi qua thư mục và tải các file YAML vào dictionary.

    :param current_path: Đường dẫn hiện tại đang quét.
    :param target_dict: Dictionary hiện tại đang được gán dữ liệu.
    """

    # Lặp qua tất cả các mục (file và thư mục) trong đường dẫn hiện tại
    for item_name in os.listdir(current_path):
        item_path = os.path.join(current_path, item_name)

        # 1. Nếu là thư mục
        if os.path.isdir(item_path):

            # Tạo một dictionary mới cho thư mục con
            new_dict = {}
            target_dict[item_name] = new_dict

            # Gọi đệ quy để đi sâu vào thư mục con
            load_yaml_mappings(item_path, new_dict)

        # 2. Nếu là file YAML
        elif os.path.isfile(item_path) and item_name.endswith(('.yaml', '.yml')):

            # Lấy tên file mà không có phần mở rộng (.yaml)
            key_name = os.path.splitext(item_name)[0]

            try:
                with open(item_path, 'r', encoding='utf-8') as file:
                    # Tải nội dung YAML
                    data = yaml.safe_load(file)

                    # Gán nội dung file YAML vào dictionary với key là tên file
                    target_dict[key_name] = data if data is not None else {}

            except Exception as e:
                print(f"Lỗi khi đọc file YAML {item_path}: {e}")
                # Có thể chọn bỏ qua hoặc thoát tùy vào yêu cầu của hệ thống