def is_new_content(source_post_id, existing_ids):
    """
    Check whether a source item is new.

    source_post_id:
        Unique ID from the source, e.g. PIB Release ID.

    existing_ids:
        IDs that have already been processed.
    """

    return str(source_post_id) not in {
        str(existing_id) for existing_id in existing_ids
    }