import re


def OPEN_UPSTREAM(stderr, arg_moniker, arg_value, stdin):
    # At #history-A.4 this shurnk to tiny,  re-written for API change.
    # At this same time, we sunsetted a whole redundant module (file).
    # Using stderr instead of listener is an experimental simplification..
    # Result value is experimental.

    typ = RESOLVE_UPSTREAM(stderr, arg_moniker, arg_value, stdin)
    if typ is None:
        return

    if 'stdin_as_argument' == typ:
        from contextlib import nullcontext
        return nullcontext(stdin)

    assert('path_as_argument' == typ)
    return open(arg_value)


def RESOLVE_UPSTREAM(stderr, arg_moniker, arg_value, stdin):
    # (see note at above function)

    def main():
        if stdin.isatty():
            if '-' == arg_value:
                return when_neither()
            return 'path_as_argument'
        if '-' == arg_value:
            return 'stdin_as_argument'
        return when_both()

    def when_both():
        whine(f'when piping from STDIN, {arg_moniker} must be "-"')

    def when_neither():
        whine(f'when {arg_moniker} is "-", STDIN must be pipe')

    def whine(msg):
        stderr.write(f'parameter error: {msg}\n')  # [#605.2] _eol

    return main()


def build_path_relativizer():
    def relativize_path(path):
        if head != path[0:leng]:
            raise RuntimeError(f'oops: (head, path): ({head}, {path})')
        tail = path[leng:]
        assert not isabs(tail)
        return tail
    from os import path as os_path, getcwd
    isabs = os_path.isabs
    head = os_path.join(getcwd(), '')
    leng = len(head)
    return relativize_path


def deindented_lines_via_big_string_(big_string):
    # convert a PEP-257-like string into an iterator of lines

    return _deindent(lines_via_big_string(big_string), _eol)


def deindented_strings_via_big_string_(big_string):
    # convert a PEP-257-like string into an iterator of strings

    return _deindent(_strings_via_big_string(big_string), '')


def _deindent(item_itr, empty_item):
    # (this should be in text_lib now, but we're leaving it here for now.)

    def peek():
        item = next(item_itr)  # ..
        peeked.append(item)
        return item
    peeked = []

    leading_ws_rx = re.compile('^([ ]+)[^ ]')

    item = next(item_itr)  # .., don't cache the throwaway item

    # if you requested to deindent a block of text but the first line is not bl
    if empty_item != item:
        assert(not leading_ws_rx.match(item))
        yield item
        for item in item_itr:
            yield item
        return

    # find the margin (the first nonzero length one in the first N lines)

    for _ in range(0, 3):
        item = peek()  # ..
        md = leading_ws_rx.match(item)
        if md is not None:
            break

    def f():
        for item in peeked:
            yield item
        for item in item_itr:
            yield item

    use_itr = f()

    if md is None:
        # cheap_arg_parse (at #history-A.5) wants to be able to use this w/o
        # knowing beforehand whether the big string has any margin anywhere
        # (some docstrings are flush-left with the whole file).

        for item in use_itr:
            yield item
        return

    margin = md[1]
    rx = re.compile(f'^[ ]{{{len(margin)}}}([^\\n]+{empty_item})\\Z')

    for item in use_itr:

        if empty_item == item:
            yield item
            continue

        md = rx.match(item)
        if md is None:
            # assume convention of """ is flush with content or 1 tab to the L
            if margin != item:
                assert(margin[0:-4] == item)

            assert(0 == len(tuple(use_itr)))
            return

        yield md[1]


def lines_via_big_string(big_string):  # #[#610]
    return (md[0] for md in re.finditer('[^\n]*\n|[^\n]+', big_string))


def _strings_via_big_string(big_string):
    if _eol not in big_string:
        if '' == big_string:
            return iter(())
        return iter((big_string,))
    return (md[1] for md in re.finditer('([^\n]*)\n', big_string))


# (buried `filesystem_functions` and justification documentation #history-B.4)


def xx(s):
    raise _exe('cover me: {}'.format(s))


_exe = Exception


class Exception(Exception):
    pass


# -- CONSTANTS

GENERIC_ERROR = 2
SUCCESS = 0


_eol = '\n'


# #history-B.4
# #history-A.5
# #history-A.4
# #history-A.3: "cheap arg parse" moves to dedicated file
# #history-A.1: as referenced
# #born: abstracted
