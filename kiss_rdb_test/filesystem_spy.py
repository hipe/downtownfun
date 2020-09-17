from modality_agnostic.test_support.common import lazy


@lazy
def filesystem_expecting_no_rewrites():

    def inj(*_):
        assert(False)

    def finish():
        return 'hi there were no file rewrites'

    return _build_filesystem_via_two_funcs(inj, finish)


def build_filesystem_expecting_num_file_rewrites(expected_num):

    class my_state:  # #class-as-namespace
        _records = []

    self = my_state

    def INJECTED_FELLOW(from_fh, to_fh):

        if len(self._records) == expected_num:
            raise Exception('too many doo-hahs')

        from_fh.seek(0)  # necessary
        _new_lines = tuple(iter(from_fh))

        self._records.append(_RecordOfFileRewrite(
            path=to_fh.name,
            lines=_new_lines,))

    def finish():

        if len(self._records) != expected_num:
            _msg = ('expected there to be more file rewrites '
                    f'(needed {expected_num}, had {len(self._records)})')
            raise Exception(_msg)

        res = tuple(self._records)
        del(self._records)
        return res

    return _build_filesystem_via_two_funcs(INJECTED_FELLOW, finish)


def _build_filesystem_via_two_funcs(INJECTED_FELLOW, finish):
    from kiss_rdb.magnetics_ import filesystem as _

    fs = _.Filesystem_EXPERIMENTAL(INJECTED_FELLOW)

    fs.FINISH_AS_HACKY_SPY = finish

    return fs


class build_fake_filesystem:
    # (currently separate from the recording filesystem. just for reads)

    def __init__(self, *tups):
        self._tups = tups

    def open_file_for_reading(self, path):
        rec = self._lookup(path)
        if rec is None:
            raise self._file_not_found_error(path)
        shape = rec[0]
        assert('file' == shape)  # we could cover etc but we don't plan on need

        _lines = _lines_via_strings_with_optimistic_peek(rec[2]())
        return _FakeFile(_lines, path)

    def stat_via_path(self, path):
        rec = self._lookup(path)
        if rec is None:
            raise self._file_not_found_error(path)
        shape = rec[0]
        if 'directory' == shape:
            return _fake_dir_stat
        assert('file' == shape)
        return _fake_file_stat

    def _file_not_found_error(self, path):
        return FileNotFoundError(
                2, f"No such file or directory: '{path}'", path)

    def _lookup(self, path):
        for rec in self._tups:
            if path == rec[1]:
                return rec

    @property
    def first_path(self):
        return self._tups[0][1]


# == model-ishes

class _FakeFile:  # :[#877.C]
    # basically [#877.B] pretend file but takes iterator, and modified
    # so that the object passed into the block has the `path` property
    # We want an excuse to unify the two.

    def __init__(self, lines, path):
        self._lines = lines
        self.name = path  # be like `_io.TextIOWrapper`
        self._is_opened_mutex = None

    def __enter__(self):
        return self

    def __exit__(self, typ, err, stack):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._lines)

    def close(self):
        del self._is_opened_mutex
        return None


class _RecordOfFileRewrite:

    def __init__(self, path, lines):
        self.path = path
        self.lines = lines


class _fake_dir_stat:  # #as-namespace-only
    st_mode = 16877


class _fake_file_stat:  # #as-namespace-only
    st_mode = 33188


# == support functions


def _lines_via_strings_with_optimistic_peek(lines):
    """EXPERIMENTAL: allow the client to represent a stream of lines without

    newline terminating each one *optionally*. The first line is peeked at
    and it is used to determine whether or not this behavior is desired.
    """

    assert(hasattr(lines, '__next__'))  # if not, nasty bugs below #[#022]

    empty = True
    for line in lines:  # #once
        empty = False
        break

    if empty:
        return

    if len(line) and '\n' == line[-1]:  # ..
        yield line
        for line in lines:
            yield line
        return

    yield f'{line}\n'
    for line in lines:
        yield f'{line}\n'

# #history-A.1: introduce fake filesystem
# #abstracted.
