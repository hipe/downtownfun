class open_dictionary_stream:
    """(minimal example exhibiting bad human key)"""

    def __init__(self, cache_path, listener):
        pass

    def __enter__(self):
        yield {'_is_sync_meta_data': True, 'natural_key_field_name': 'xyzz 01'}
        yield {'choo cha': 'foo fa'}

    def __exit__(*_):
        return False  # no, we don't trap exceptions


if __name__ == '__main__':
    raise Exception('(see [#410.H])')

# #pending-rename: probably bad_human_key_ETC now that it has a purpose
# #born.
