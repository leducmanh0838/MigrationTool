# src/database/session.py
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import AppConfig
from src.database.models import Base

# 2. Tạo Engine
engine = create_engine(AppConfig.SQLALCHEMY_DATABASE_URL)

# 3. Tạo SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Lệnh tạo bảng nên gom vào một hàm để gọi khi khởi động ứng dụng
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    """Hàm tiện ích để lấy session và tự động đóng"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()