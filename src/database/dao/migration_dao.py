from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import AppConfig
from src.database.enums import MigrationPlatform
from src.database.models import Migration, Base
from src.database.session import get_db


class MigrationDAO:
    def __init__(self, db: Session):
        self.db = db

    # 1. Thêm mới (Create)
    def create_migration(self, source_platform: str, target_platform: str, entity_path) -> Migration:
        new_migration = Migration(
            source_platform=source_platform,
            target_platform=target_platform,
            entity_path=entity_path
        )
        self.db.add(new_migration)
        self.db.commit()
        self.db.refresh(new_migration)
        return new_migration

    # 2. Xem (Read)
    def get_by_id(self, migration_id: int) -> Migration | None:
        return self.db.query(Migration).filter_by(id=migration_id).first()

    def get_all(self):
        return self.db.query(Migration).all()

    # 3. Sửa (Update)
    def update_checkpoint(self, migration_id: int, entity_id: int, entity_type: str):
        migration = self.db.query(Migration).filter_by(id=migration_id).first()

        if migration:
            migration.checkpoint_source_entity_id = entity_id
            migration.checkpoint_source_entity_type = entity_type

            self.db.commit()
            self.db.refresh(migration)
        return migration

    # 4. Xóa (Delete)
    def delete_migration(self, migration_id: int) -> bool:
        migration = self.get_by_id(migration_id)
        if migration:
            self.db.delete(migration)
            self.db.commit()
            return True
        return False


if __name__ == "__main__":
    # 2. Sử dụng Context Manager
    with get_db() as db:
        dao = MigrationDAO(db)
        created = dao.create_migration("magento", "woo", ["category", "product", "customer"])
        print("created.id: ", created.id)
