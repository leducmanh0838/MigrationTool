from sqlalchemy import Integer
from sqlalchemy.types import TypeDecorator  # Dùng để xử lý chuyển đổi phức tạp

from src.database.enums import MigrationPlatform


# --- ĐỊNH NGHĨA KIỂU DỮ LIỆU TÙY CHỈNH CHO SQLAlchemy ---
class PlatformType(TypeDecorator):
    """Ánh xạ đối tượng MigrationPlatform sang Integer và ngược lại."""

    # Kiểu dữ liệu mà cột sẽ dùng trong database (MySQL)
    impl = Integer

    # Định nghĩa lớp Enum mà chúng ta sẽ làm việc
    cache_ok = True

    def process_bind_param(self, value: MigrationPlatform | None, dialect):
        """Chuyển đổi từ Python (Enum object) sang Database (Integer)"""
        if value is None:
            return None
        # Khi lưu vào DB, chúng ta lấy giá trị ID số (1, 2, 3...)
        return value.id_value

    def process_result_value(self, value: int | None, dialect):
        """Chuyển đổi từ Database (Integer) sang Python (Enum object)"""
        if value is None:
            return None

        # Khi đọc từ DB, chúng ta tìm lại đối tượng Enum dựa trên ID số
        # (Đây là logic cần được tối ưu hóa)
        for member in MigrationPlatform:
            if member.id_value == value:
                return member
        raise ValueError(f"Giá trị ID nền tảng '{value}' không hợp lệ.")