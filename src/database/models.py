from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint, TEXT, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base

from src.database.types import PlatformType

Base = declarative_base()  # Base class cho các model


class Migration(Base):
    __tablename__ = 'migration'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_platform = Column(String(50), nullable=False)
    target_platform = Column(String(50), nullable=False)

    entity_path = Column(JSON, nullable=False)

    checkpoint_source_entity_id = Column(Integer, nullable=True)
    checkpoint_source_entity_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now())

    def __str__(self):
        return (f"<Migration(platform_id='{self.source_platform_id} -> {self.target_platform_id}', "
                f"checkpoint_source_entity_id='{self.checkpoint_source_entity_id}')>",
                f"checkpoint_source_entity_type='{self.checkpoint_source_entity_type}')>")


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


class DeadLetterQueue(Base):
    __tablename__ = 'dlq'
    # Trường Khóa chính
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Dữ liệu Thất bại
    entity_type = Column(String(50), nullable=False)
    source_entity_id = Column(Integer, nullable=False)
    # Thông tin Lỗi
    reason = Column(String(255), nullable=False)  # Lý do ngắn gọn
    error_details = Column(TEXT)  # Chi tiết lỗi đầy đủ (Exception trace)
    raw_data_json = Column(Text)  # Dữ liệu gốc từ Magento (JSON/Text)
    # Metadata
    attempted_at = Column(DateTime, default=func.now())

    migration_id = Column(Integer, ForeignKey(Migration.id, ondelete='RESTRICT'), nullable=False)

    def __str__(self):
        return f"<DLQ(entity='{self.entity_type}:{self.source_id}', reason='{self.reason}')>"


if __name__ == '__main__':
    from sqlalchemy import create_engine

    # SỬ DỤNG TÀI KHOẢN ROOT VÀ MẬT KHẨU ĐƠN GIẢN
    DATABASE_URL = "mysql+pymysql://root:my_root_password_123@localhost:3307/migration_db"

    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)  # Tạo các bảng nếu chúng chưa tồn tại
"""
docker exec -it migration_mysql_db mysql -u root -p

SHOW DATABASES;

-- Phiên 1: Migration từ Magento sang Woo, Checkpoint cuối cùng là Product ID 500
INSERT INTO migration (source_platform_id, target_platform_id, checkpoint_source_entity_id, checkpoint_source_entity_type) 
VALUES 
(1, 2, 500, 'product'); 

-- Phiên 2: Migration từ Magento sang Medusa, Checkpoint cuối cùng là Customer ID 100
INSERT INTO migration (source_platform_id, target_platform_id, checkpoint_source_entity_id, checkpoint_source_entity_type) 
VALUES 
(1, 3, 100, 'customer');

SELECT * FROM migration;
"""