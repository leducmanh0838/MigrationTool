# Lớp Enum của bạn (Không thay đổi)
from enum import unique, Enum


@unique
class MigrationPlatform(Enum):
    # (ID SỐ, TÊN CHUỖI)
    MAGENTO = (1, "magento")
    WOOCOMMERCE = (2, "woo")
    MEDUSA = (3, "medusa")

    def __init__(self, id_value, name_string):
        self.id_value = id_value
        self.name_string = name_string

    @classmethod
    def from_name(cls, name_string: str):
        """
        Tìm kiếm thành viên Enum dựa trên tên chuỗi (name_string).
        """
        # Duyệt qua tất cả các thành viên (member) trong Enum
        for member in cls:
            # So sánh tên chuỗi
            if member.name_string == name_string.lower():
                return member

        # Nếu không tìm thấy, bạn có thể ném ra một lỗi (Exception)
        # hoặc trả về None, tùy thuộc vào yêu cầu của bạn.
        raise ValueError(f"Tên nền tảng không hợp lệ: '{name_string}'")

# 1. Lấy ID để lưu vào DB:
# magento_id_to_save = MigrationPlatform.MAGENTO.id_value

# 2. Lấy Tên chuỗi để hiển thị:
# magento_name = MigrationPlatform.MAGENTO.name_string