from sqlalchemy.orm import Session

from src.database.dao.abstract.base_dao import BaseDAO
from src.database.models import IdMapping, Base
from src.database.session import get_db


class IdMappingDAO(BaseDAO[IdMapping]):
    def __init__(self, db: Session):
        super().__init__(db, IdMapping)


if __name__ == "__main__":
    # 2. Sử dụng Context Manager
    with get_db() as db:
        dao = IdMappingDAO(db)
        # record = dao.find_one_by(
        #     entity_name="product",
        #     source_entity_id=3,
        #     target_entity_id=1,
        # )
        # # record = dao.create_record(
        # #     entity_name="product",
        # #     source_entity_id=3,
        # #     target_entity_id=1,
        # #     migration_id=2
        # # )
        # # record = dao.update_checkpoint(2, 50, "category")
        # print("record.id: ", record.id)
        record = dao.find_one_by(
            entity_name="category",
            source_entity_id=20,
            migration_id=21
        )
        print("record.target_entity_id: ", record.target_entity_id)

"""
SELECT id, entity_name, source_entity_id, target_entity_id, migration_id FROM id_mapping;
"""