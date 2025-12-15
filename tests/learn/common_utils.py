# common_utils.py

# --- Context Manager Giả định (Mô phỏng lưu trữ ánh xạ ID) ---
class MockMappingManager:
    """Mô phỏng cơ sở dữ liệu lưu trữ ánh xạ ID nguồn -> ID đích."""

    def __init__(self):
        # Các ID đã được migrate: source_id: target_id
        self.id_map = {0: 0, 2: 50, 3: 51}

    def get_target_id(self, entity, source_id):
        try:
            # Đảm bảo source_id là số nguyên để tra cứu
            return self.id_map.get(int(source_id), None)
        except (ValueError, TypeError):
            return None


# --- Transformations ---
def map_id_to_target(source_value, entity, context):
    print("params: ",source_value, entity, context)
    # Thay đổi logic, không cần tham số 'source_id' vì nó đã là 'source_value'
    source_id = source_value
    if source_id is None:
        return 0

    # Tra cứu ID đích
    target_id = context.get_target_id(entity, source_id)

    # Nếu ID đích chưa có (chưa migrate), ta gán về ID gốc (0)
    return target_id if target_id is not None else 0


# --- Validators ---
def not_null(value):
    """Kiểm tra giá trị có phải là None hay chuỗi rỗng không."""
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


# LƯU Ý: Đổi tên tham số đầu tiên thành validated_value để tránh xung đột
def is_not_self_referencing(validated_value, current_id):
    """Kiểm tra parent_id không bằng ID của chính category đó (self-reference)."""
    try:
        # So sánh ID cha (giá trị được xử lý) với ID hiện tại
        return int(validated_value) != int(current_id)
    except (ValueError, TypeError):
        # Trả về True nếu không thể so sánh (ví dụ: một trong hai là None)
        return True