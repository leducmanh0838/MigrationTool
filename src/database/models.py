from enum import Enum, unique

from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint, TEXT, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # Base class cho các model


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

class Migration(Base):
    __tablename__ = 'migration'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_platform_id = Column(Integer, nullable=False)
    target_platform_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())

    def __str__(self):
        return f"{self.source_platform_id} - {self.target_platform_id}"


class IdMapping(Base):
    __tablename__ = 'id_mapping'
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False)  # Ví dụ: 'product', 'customer', 'order'

    source_entity_id = Column(Integer, nullable=False)
    target_entity_id = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=func.now())

    migration_id = Column(Integer, ForeignKey(Migration.id, ondelete='RESTRICT'), nullable=False)

    __table_args__ = (
        UniqueConstraint('migration_id', 'entity_type', 'source_entity_id', name='idx_source_entity'),
    )

    def __str__(self):
        return f"<IdMapping(source='{self.entity_type}:{self.source_entity_id}', target='{self.target_entity_id}')>"


class Checkpoint(Base):
    __tablename__ = 'wp_migration_checkpoint'
    id = Column(Integer, primary_key=True, autoincrement=True)
    checkpoint_key = Column(String(100), nullable=False, unique=True)  # Ví dụ: 'last_migrated_product_id'
    checkpoint_value = Column(String(255), nullable=False)  # Ví dụ: '10500'
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Checkpoint(key='{self.checkpoint_key}', value='{self.checkpoint_value}')>"


class DeadLetterQueue(Base):
    __tablename__ = 'wp_migration_dlq'
    # Trường Khóa chính
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Dữ liệu Thất bại
    entity_type = Column(String(50), nullable=False)
    source_id = Column(String(255), nullable=False)
    # Thông tin Lỗi
    reason = Column(String(255), nullable=False)  # Lý do ngắn gọn
    error_details = Column(TEXT)  # Chi tiết lỗi đầy đủ (Exception trace)
    raw_data_json = Column(Text)  # Dữ liệu gốc từ Magento (JSON/Text)
    # Metadata
    attempted_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<DLQ(entity='{self.entity_type}:{self.source_id}', reason='{self.reason}')>"


if __name__ == '__main__':
    from sqlalchemy import create_engine

    # SỬ DỤNG TÀI KHOẢN ROOT VÀ MẬT KHẨU ĐƠN GIẢN
    DATABASE_URL = "mysql+pymysql://root:my_root_password_123@localhost:3307/migration_db"

    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)  # Tạo các bảng nếu chúng chưa tồn tại
