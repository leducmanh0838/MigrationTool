def save_id_mapping(created_target_record, source_record, source_id_field, target_id_field, entity, context):
    # entity_id_maps[self.entity][record.get('id')] = category_target["id"]
    print("save_id_mapping:")
    # if not context:
    #     return
    # if not context.get('entity_id_maps'):
    #     return

    entity_id_maps = context.get('entity_id_maps')

    source_id = source_record.get(source_id_field)
    target_id = created_target_record.get(target_id_field)

    entity_id_maps[entity][source_id] = target_id


def send_reset_password_email(**kwargs):
    # entity_id_maps[self.entity][record.get('id')] = category_target["id"]
    print("send_reset_password_email:")
    if not kwargs:
        return
    if not kwargs.get('created_target_data'):
        return
    if not kwargs.get('write_connector'):
        return

    created_target_data = kwargs.get('created_target_data')
    write_connector = kwargs.get('write_connector')

    # email = created_target_data.get("email")
    # if email:
    #     write_connector.send_reset_password_email(email)
