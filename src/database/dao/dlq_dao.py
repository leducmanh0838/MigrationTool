from sqlalchemy.orm import Session

from src.database.dao.abstract.base_dao import BaseDAO
from src.database.models import DeadLetterQueue
from src.database.session import get_db


class DeadLetterQueueDAO(BaseDAO[DeadLetterQueue]):
    def __init__(self, db: Session):
        super().__init__(db, DeadLetterQueue)


if __name__ == "__main__":
    # 2. Sử dụng Context Manager
    with get_db() as db:
        dao = DeadLetterQueueDAO(db)
        record = dao.create_record(
            entity_name="category",
            source_entity_id=1,
            reason="Sai định dạng",
            migration_id=1,
        )
        # record = dao.update_checkpoint(2, 50, "category")
        print("created.id: ", record.id)
"""
SELECT id, entity_name, source_entity_id, reason, migration_id FROM dlq;
"""