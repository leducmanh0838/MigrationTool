from src.database.dao.id_mapping_dao import IdMappingDAO
from src.database.session import get_db

with get_db() as db:
    dao = IdMappingDAO(db)
    records = dao.filter_by(filters={
        'migration_id': 1,
        'entity_name': 'product',
    })
    ids = [record.target_entity_id for record in records]
    print(ids)
