from abc import ABC
from typing import TypeVar, Generic, Type, List, Optional, Dict, Any

from sqlalchemy import exists
from sqlalchemy.orm import Session

T = TypeVar('T')


class _BaseMixin(Generic[T]):
    db: Session
    model: Type[T]


# 1. Nhóm các hàm chỉ đọc
class _ReadMixin(_BaseMixin, Generic[T]):
    def get_by_id(self, id: int) -> Optional[T]:
        return self.db.query(self.model).filter_by(id=id).first()

    def get_all(self) -> List[T]:
        return self.db.query(self.model).all()

    def filter_by(self, filters: Dict[str, Any] = None, sort_by: str = None, ascending: bool = True) -> List[T]:
        query = self.db.query(self.model)

        if filters:
            for field, value in filters.items():
                column = getattr(self.model, field, None)
                if column is not None:
                    # Kiểm tra nếu value là một list hoặc tuple thì dùng .in_()
                    if isinstance(value, (list, tuple)):
                        query = query.filter(column.in_(value))
                    else:
                        # Ngược lại dùng so sánh bằng như bình thường
                        query = query.filter(column.__eq__(value))

        if sort_by:
            column = getattr(self.model, sort_by, None)
            if column is not None:
                query = query.order_by(column.asc() if ascending else column.desc())

        return query.all()

    def find_one_by(self, **filters) -> Optional[T]:
        return self.db.query(self.model).filter_by(**filters).first()


# 2. Nhóm các hàm ghi dữ liệu
class _WriteMixin(_BaseMixin, Generic[T]):
    def create_record(self, **kwargs) -> T:
        record = self.model(**kwargs)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_record(self, id: int, commit: bool = True, **kwargs) -> Optional[T]:
        # record = self.get_by_id(id)
        record = self.db.query(self.model).filter_by(id=id).first()
        if record:
            try:
                for key, value in kwargs.items():
                    if hasattr(record, key):
                        setattr(record, key, value)

                if commit:
                    self.db.commit()
                    self.db.refresh(record)
                else:
                    self.db.flush()

                return record
            except Exception as e:
                self.db.rollback()
                raise e
        return None


# 3. Nhóm các hàm tìm kiếm/kiểm tra
class _QueryMixin(_BaseMixin, Generic[T]):
    def exists_by(self, **filters) -> bool:
        q = self.db.query(exists().where(
            *(getattr(self.model, key) == value for key, value in filters.items())
        ))
        return q.scalar()

    # ... find_by, find_one_by ...


# 4. Lớp Base hoàn chỉnh kết hợp các Mixins
class BaseDAO(_ReadMixin[T], _WriteMixin[T], _QueryMixin[T], ABC):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
