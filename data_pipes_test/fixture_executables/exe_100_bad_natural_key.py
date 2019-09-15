#!/usr/bin/env python3 -W error::Warning::0


stream_for_sync_is_alphabetized_by_key_for_sync = True


def stream_for_sync_via_stream(dcts):
    for dct in dcts:
        yield (dct['choo cha'], dct)


class open_traversal_stream:
    """(minimal example exhibiting bad human key)"""

    def __init__(self, listener, cache_path=None):
        pass

    def __enter__(self):
        yield {'choo cha': 'foo fa'}

    def __exit__(*_):
        return False  # no, we don't trap exceptions


if __name__ == '__main__':
    # .#todo
    import exe_150_json_stream_via_bernstein_html as _  # #[410.H]
    exit(_.execute_as_CLI_(open_diction_IN_FLUX))

# #history-A.1: no more metadata header
# #born.
