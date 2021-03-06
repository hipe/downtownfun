#!/usr/bin/env python3 -W default::Warning::0

"""A sort of producer script sourced from kubernetes documentation.

At birth this scraped a url like:

{eg_url}

, turning it ☝️  into an entity stream presumably for use in generating
a punchlist somehow.
"""

_doc = __doc__
_eg_url = 'https://kubernetes.io/docs/concepts/'


# (worked "visually" (mostly) at #history-A.2)


def _formals():
    yield '-h', '--help', 'this screen'
    yield 'url', 'example: https://some-k8s-site.com/docs/foo-bar/'


def _CLI(stdin, stdout, stderr, argv):
    kwargs = {'description_valueser': lambda: {'eg_url': _eg_url}}
    from script_lib.cheap_arg_parse import cheap_arg_parse as func
    return func(_do_CLI, stdin, stdout, stderr, argv, _formals(), **kwargs)


def _do_CLI(stdin, stdout, stderr, url, rscr):
    mon = rscr().monitor

    from kiss_rdb import dictionary_dumper_as_JSON_via_output_stream
    recv = dictionary_dumper_as_JSON_via_output_stream(stdout)

    _opened = open_traversal_stream(mon.listener, url)
    with _opened as dcts:
        for dct in dcts:
            recv(dct)

    stdout.write('\n')  # _eol
    return mon.exitstatus


_do_CLI.__doc__ = _doc


def multi_depth_value_dictionary_stream_via_traversal_stream(dcts):
    from kiss_rdb.storage_adapters.markdown import markdown_link_via
    for dct in dcts:
        if '_is_branch_node' in dct:
            yield dct
            continue
        yield {'document': markdown_link_via(**dct)}


def open_traversal_stream(listener, url, cache_path=None):
    from contextlib import nullcontext as func
    return func(_build_traversal_stream(listener, url, cache_path))


def _build_traversal_stream(listener, url, cached_path=None):

    if not _validate_url(url, listener):
        return

    from data_pipes.format_adapters.html.script_common import \
        cached_document_via as func
    doc = func(cached_path, url, 'html document', listener)
    if doc is None:
        return

    from bs4 import BeautifulSoup
    with open(doc.cache_path) as fh:
        soup = BeautifulSoup(fh, 'html.parser')

    toc, = soup.select('#docsToc')

    div, = _filter('div', toc)

    items = _direct_children(div)

    itr = iter(items)  # be explicit

    yield _object_via_first_anchor_tag_ONCE_ONLY(next(itr), url)

    for item in itr:
        name = item.name
        if 'a' == name:
            for dct in _objects_via_anchor_tag_up_top(item):
                yield dct
            continue
        assert('div' == name)
        for dct in _objects_via_div_tag(item):
            yield dct


def _validate_url(url, listener):
    f = None
    if _hardcoded_single_scheme != url[0:len(_hardcoded_single_scheme)]:  # meh
        def f():
            yield f"url scheme must be {_hardcoded_single_scheme} - {url}"
    elif '/' != url[-1]:
        def f():
            yield f"url must end in a slash meh - {url}"
    if f is None:
        return True
    listener('error', 'expression', 'abnormal_url', f)


_hardcoded_single_scheme = 'https://'


def _objects_via_div_tag(div):

    yield {
            _is_header_node: True,
            _header_level: 2,  # header level 2 is the headers before tables
            _label: div['data-title'],
            }

    container, = _direct_children(div)
    for a in _direct_children(container):
        name = a.name
        if 'a' == name:
            yield _object_via_anchor_tag_not_top(a)
        else:
            assert('div' == name)
            for dct in _recurse(a):
                yield dct


def _recurse(div):  # note ugly redundancy with above

    yield {
            _is_header_node: True,
            _header_level: 3,  # ..
            _label: div['data-title'],
            }

    container, = _direct_children(div)
    for a in _direct_children(container):
        name = a.name
        assert('a' == name)
        yield _object_via_anchor_tag_not_top(a)


def _objects_via_anchor_tag_up_top(a):
    """wat do if anchor tag (or "item-node") at toplevel of source document?

    one thing we tried it "promoting" it so that it gets rendered as a table
    with one element. but this had a feeling of being choppy with lots of
    orphans and redundancy (because we used the same label 2x, once to label
    the table and once to label the item in the table).

    this could be addressed at the consumer level by adding special metadata
    here to signal that this is a singleton, but still there's the noise
    problem.

    so rather, we emit a composite dictionary; one that is both header and
    item-node:
    """

    yield {
            _is_header_node: True,
            _header_level: 2,  # again, a would-be table label
            _label: a['data-title'],
            _url: a['href'],  # weird for a header, but not here
            '_is_composite_node': True,
            }


def _object_via_first_anchor_tag_ONCE_ONLY(a, url):
    return {
            _is_header_node: True,
            _header_level: 1,  # header level 1 is the title of a doc page
            _label: a['data-title'],
            _url: url,  # leap of faith that page url corresponds to this item
            }


def _object_via_anchor_tag_not_top(a):
    return {
            _label: a['data-title'],
            _url: a['href'],
            }


def _direct_children(node):  # #cp
    return _filter('*', node)  # omit strings


def _filter(sel, el):
    import soupsieve as sv
    return sv.filter(sel, el)


_header_level = 'header_level'
_is_header_node = '_is_branch_node'
_label = 'label'
_url = 'url'


if __name__ == '__main__':
    import sys as o
    exit(_CLI(o.stdin, o.stdout, o.stderr, o.argv))

# #history-B.2
# #history-A.3
# #history-A.2
# #history-A.1
# #born.
