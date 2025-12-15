# src/common_validators.py

import numbers


# --- VALIDATORS CHUNG (Áp dụng cho mọi loại dữ liệu) ---

def not_null(value, **kwargs):
    """
    Kiểm tra giá trị có tồn tại (không phải None, không phải chuỗi rỗng) không.
    Thường áp dụng cho các trường bắt buộc.
    """
    print("validate not_null")
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    # Có thể thêm kiểm tra cho list rỗng, dict rỗng nếu cần
    return True


def is_not_self_referencing(parent_id, current_id):
    print("is_not_self_referencing")
    return parent_id != current_id


# --- VALIDATORS CHO CHUỖI (String) ---

def is_string_min_length(value, min_length, **kwargs):
    """
    Kiểm tra độ dài chuỗi có đạt mức tối thiểu không.
    Tham số: min_length (được truyền từ YAML params)
    """
    print("validate is_string_min_length")
    if not isinstance(value, str):
        # Nếu không phải chuỗi, coi là không hợp lệ cho quy tắc này
        return False

    return len(value.strip()) >= min_length


def is_string_max_length(value, max_length, **kwargs):
    """
    Kiểm tra độ dài chuỗi có vượt quá mức tối đa không.
    Tham số: max_length
    """
    print("validate is_string_max_length")
    if not isinstance(value, str):
        return True  # Nếu không phải chuỗi, coi là hợp lệ (hoặc False tùy logic mong muốn)

    return len(value) <= max_length


# --- VALIDATORS CHO SỐ (Numeric) ---

def is_integer(value, **kwargs):
    """
    Kiểm tra xem giá trị có thể chuyển đổi an toàn thành số nguyên không.
    """
    print("validate is_integer")
    if isinstance(value, int):
        return True

    # Xử lý trường hợp chuỗi số ('123')
    if isinstance(value, str):
        try:
            int(value)
            return True
        except ValueError:
            return False

    return False


def is_non_negative_integer(value, **kwargs):
    """
    Kiểm tra xem giá trị có phải là số nguyên không âm (>= 0) không.
    """
    print("validate is_non_negative_integer")
    if not is_integer(value):
        return False

    # Chuyển đổi về số nguyên để so sánh
    try:
        num = int(value)
        return num >= 0
    except ValueError:
        return False  # Trường hợp lỗi không thể xảy ra nếu đã qua is_integer


def is_max_value(value, max_value, **kwargs):
    """
    Kiểm tra xem giá trị số có nhỏ hơn hoặc bằng giá trị tối đa không.
    Tham số: max_value
    """
    print("validate is_max_value")
    # Chỉ hoạt động với các loại dữ liệu số
    if not isinstance(value, numbers.Number):
        # Nếu giá trị không phải số, hãy thử chuyển đổi nếu nó là chuỗi số
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return False  # Không phải số thì không thể so sánh
        else:
            return False

    return value <= max_value


# --- VALIDATOR KHÁC (Tùy chọn) ---

def is_valid_email(value, **kwargs):
    """
    Kiểm tra định dạng email cơ bản. (Cần thư viện regex trong thực tế)
    """
    print("validate is_valid_email")
    if not isinstance(value, str):
        return False

    # Kiểm tra đơn giản: phải có '@' và ít nhất một '.'
    return '@' in value and '.' in value
