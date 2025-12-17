from sqlalchemy.orm import Session

from src.database.dao.abstract.base_dao import BaseDAO
from src.database.models import Migration, Base
from src.database.session import get_db


class MigrationDAO(BaseDAO[Migration]):
    def __init__(self, db: Session):
        super().__init__(db, Migration)

    # def update_checkpoint(self, migration_id: int, entity_id: int, entity_name: str):
    #     migration = self.db.query(Migration).filter_by(id=migration_id).first()
    #
    #     if migration:
    #         migration.checkpoint_source_entity_id = entity_id
    #         migration.checkpoint_source_entity_name = entity_name
    #
    #         self.db.commit()
    #         self.db.refresh(migration)
    #     return migration


if __name__ == "__main__":
    # 2. Sử dụng Context Manager
    with get_db() as db:
        dao = MigrationDAO(db)
        # record = dao.create_record(
        #     source_platform="magento",
        #     target_platform="woo",
        #     entity_path=["category", "product"]
        # )
        record = dao.update_record(id=10,
                                   checkpoint_source_entity_id=5,
                                   checkpoint_source_entity_name="product",
                                   )
        # record = dao.update_checkpoint(2, 50, "category")
        print("record.id: ", record.id)
"""
SELECT id, source_platform, target_platform, entity_path, checkpoint_source_entity_id, checkpoint_source_entity_name FROM migration;
"""