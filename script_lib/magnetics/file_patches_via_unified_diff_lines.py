# Parse unified diff files. In practice, just used in testing.
# If this gets too frustrating, consider using `unidiff` instead.

# Conceptually this was abstracted from [#873.23] a testing DSL we made
# in one file for asserting the content of file patches. See there for
# discussion of why we didn't complete the abstraction; hence this file
# only #began-as-abstraction.


def cli_for_production():
    from sys import stdin, stdout, stderr, argv
    exit(_CLI(stdin, stdout, stderr, argv))


def _CLI(sin, sout, serr, argv):
    from script_lib.cheap_arg_parse import cheap_arg_parse
    return cheap_arg_parse(
            _do_CLI, sin, sout, serr, argv,
            formal_parameters=(('file', 'zim zum'),),
            description_template_valueser=lambda: {})


def _do_CLI(mon, sin, sout, serr, path):
    "experiment. just for testing patch files"

    def work(lines):
        for fp in file_patches_via_unified_diff_lines(lines):
            for line in fp._to_debugging_lines():
                serr.write(line)

    if '-' == path:
        work(sin)
    else:
        with open(path) as lines:
            work(lines)
    return 0


# == no more CLI

def lazy(orig_f):
    def use_f():
        if not len(pointer):
            pointer.append(orig_f())
        return pointer[0]
    pointer = []
    return use_f


def file_patches_via_unified_diff_lines(lines):  # :[#606]
    # The parse is lazy/streaming across two axes: one, it chunks the input
    # lines in to "file patches" with the really coarse parsing below, rather
    # than parsing the whole "big patchfile" in to memory all at once.

    # (It may do similar lazy parsing/streaming things with the other plural
    # elements, like the hunks in a file patch, or the runs in hunk.)

    # The other axis of laziness is that we don't parse down in to deeper
    # level of detail until we need to (like the hunks of a file, or the
    # runs in a hunk). So when the file patch is first constructed, it is just
    # a flat tuple of raw lines, not an array of chunks; and similarly a
    # chunk with its runs.

    scn = _line_scanner_via_lines(lines)
    line_cache = []
    while not scn.is_empty:
        while True:
            first_char = scn.peek[0]
            if '@' == first_char:
                break
            assert(' ' != first_char)
            line_cache.append(scn.shift())
            assert(not scn.is_empty)

        while True:
            line_cache.append(scn.shift())
            if scn.is_empty:
                break  # this might let some invalid unidiffs thru
            first_char = scn.peek[0]
            if first_char in (' ', '+', '-', '@'):
                continue
            break

        file_patch_lines = tuple(line_cache)
        line_cache.clear()
        yield _FilePatch(file_patch_lines)


def requires_parse(orig_f):
    def use_f(self):
        if self._is_raw:
            self._is_raw = False
            self._parse()
        return orig_f(self)
    return use_f


class _FilePatch:

    def __init__(self, lines):
        self._lines = lines
        self._is_raw = True

    @requires_parse
    def _to_debugging_lines(self):
        for line in self.junk_lines:
            yield f"JUNK LINE: {line}"
        yield f"MMM LINE: {self.mmm_line}"
        yield f"PPP LINE: {self.ppp_line}"
        for hunk in self.hunks:
            for line in hunk._to_debugging_lines():
                yield line

    @property
    @requires_parse
    def junk_lines(self):
        return self._junk_lines

    @property
    @requires_parse
    def mmm_line(self):
        return self._mmm_line

    @property
    @requires_parse
    def ppp_line(self):
        return self._ppp_line

    @property
    @requires_parse
    def hunks(self):
        if self._hunks_is_raw:
            self._hunks_is_raw = False
            self._parse_hunks()
        return self._hunks

    def _parse_hunks(self):
        asts = self._hunk_ASTs
        del self._hunk_ASTs
        self._hunks = tuple(_Hunk(astt) for astt in asts)

    def _parse(self):
        lines = self._lines
        del self._lines
        ast = _parse_file_patch(lines)
        if 'junk_line' in ast:  # zero or more
            _ = tuple(md.string for md in ast.pop('junk_line'))
        else:
            _ = ()
        self._junk_lines = _
        self._mmm_line = ast.pop('minus_minus_minus_line').string
        self._ppp_line = ast.pop('plus_plus_plus_line').string
        self._hunk_ASTs = ast.pop('hunk')
        self._hunks_is_raw = True
        assert(not len(ast))


class _Hunk:
    def __init__(self, ast):
        self._at_at_line = ast.pop('at_at_line').string
        self._body_lines = tuple(md.string for md in ast.pop('body_line'))
        assert(not len(ast))
        self._is_raw = True

    def to_remove_lines_runs(self):
        return self._to_runs('remove_lines')

    def _to_runs(self, cat):
        for run in self.runs:
            if cat == run.category_name:
                yield run

    def _to_debugging_lines(self):
        yield f'HUNK: {self._at_at_line}'
        for run in self.runs:
            cat_name = run.category_name
            for line in run.lines:
                yield f'{cat_name}: {line}'

    @property
    @requires_parse
    def runs(self):
        return self._runs

    def _parse(self):
        lines = self._body_lines
        del self._body_lines
        _ = _partition(lines, lambda line: line[0], lambda cat, items: _Run(cat, items))  # noqa: E501
        self._runs = tuple(_)


def _partition(items, category_function, flush_chunk):
    itr = iter(items)
    for item in itr:
        previous_category = category_function(item)
        item_cache = [item]
        break
    for item in itr:
        current_category = category_function(item)
        if previous_category == current_category:
            item_cache.append(item)
            continue
        # there was a change
        yield flush_chunk(previous_category, tuple(item_cache))
        item_cache.clear()
        item_cache.append(item)
        previous_category = current_category
    assert(len(item_cache))
    yield flush_chunk(previous_category, tuple(item_cache))


class _Run:
    def __init__(self, char, lines):
        self.category_name = _run_category_via_character[char]
        self.lines = lines


_run_category_via_character = \
        {' ': 'context_lines', '-': 'remove_lines', '+': 'add_lines'}


def _parse_file_patch(lines):

    parser_builder = _parser_builder()
    p = parser_builder()

    lineno = 0
    reached_done = False
    itr = iter(lines)
    for line in itr:
        lineno += 1

        while True:
            direc = p.parse_line(line)
            if direc is None:
                direc = ('stop', None)

            direc_name, direc_data = direc

            if 'done_but_rewind' == direc_name:
                xx()

            break

        if 'stay' == direc_name:
            continue

        if 'stop' == direc_name:
            lines = parser_builder.THESE_LINES(line, lineno, p)
            xx(' '.join(lines))
            # listener('error', 'expression', 'expecting', lambda: lines)
            return

        if 'done' == direc_name:
            xx()
            reached_done = True
            ast = direc_data()
            xx(ast)
            break
        xx()

    assert(not reached_done)  # our grammar is such that, it globs on tail

    for unexpected_line in itr:
        xx()  # had more lines than we expected

    return p.receive_EOF()()


@lazy
def _parser_builder():
    from script_lib.magnetics.parser_via_grammar import \
        WIP_PARSER_BUILDER_VIA_DEFINITION as parser_builder_via, THESE_LINES

    parser_builder = parser_builder_via(_define_grammar)
    parser_builder.THESE_LINES = THESE_LINES
    return parser_builder


def _define_grammar(g):
    define = g.define
    sequence = g.sequence
    # alternation = g.alternation
    regex = g.regex

    define('file', sequence(
        ('between', 0, 'and', 3, 'junk_line', 'keep'),  # not implemented fully
        ('one', 'minus_minus_minus_line', 'keep'),
        ('one', 'plus_plus_plus_line', 'keep'),
        ('one_or_more', 'hunk', 'keep'),
    ))

    define('hunk', sequence(
        ('one', 'at_at_line', 'keep'),
        ('one_or_more', 'body_line', 'keep')
    ))

    define('junk_line', regex(r'^[a-z]'))  # ..
    define('minus_minus_minus_line', regex(r'^---[ ]'))
    define('plus_plus_plus_line', regex(r'^\+\+\+[ ]'))
    define('at_at_line', regex(r'^@@[ ]'))
    define('body_line', regex(r'^[- +]'))


def _line_scanner_via_lines(lines):  # #[#008.4] a scanner

    itr = iter(lines)
    del(lines)  # when this is a tuple and you think it's an io, bad time

    def advance():
        for line in itr:
            self.pos += 1
            self.peek = line
            return
        self.is_empty = True
        del self.peek

    class line_scanner:
        def __init__(self):
            self.pos = 0
            self.peek = None
            self.is_empty = False

        def shift(self):
            x = self.peek
            self.advance()
            return x

        def advance(_):
            advance()

    self = line_scanner()
    advance()
    return self


def xx(msg=None):
    raise RuntimeError(f"write me{f': {msg}' if msg else ''}")


if '__main__' == __name__:
    cli_for_production()

# #began-as-abstraction
