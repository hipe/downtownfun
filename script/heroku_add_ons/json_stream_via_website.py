#!/usr/bin/env python3 -W error::Warning::0

"""generate a stream of JSON from the heroku page {url}

(this is the content-producer of the producer/consumer pair)
"""


"""about coverage: this is not covered. it is similar enough to khong
(which is covered excessively) that we held off on doing so here; but
if this script is ever broken, probably that means it's time to cover
"""


_domain = 'https://devcenter.heroku.com'

_url = _domain + '/categories/add-on-documentation'

_first_selector = ('ul', {'class': 'list-icons'})


def _my_CLI(listener, sin, sout, serr):

    _cm = open_dictionary_stream(None, listener)
    with _cm as lines:
        exitstatus = _lib().flush_JSON_stream_into(sout, serr, lines)
    return exitstatus


_my_CLI.__doc__ = __doc__


def open_dictionary_stream(html_document_path, listener):

    def my_generator(el, _emit):
        yield {'_is_sync_meta_data': True, 'natural_key_field_name': 'add_on'}
        for el in el.find_all('li', recursive=False):
            a_el = el.findChild('a')
            _href = a_el['href']
            _label = a_el.text
            # the old way:
            # yield {'href': _href, 'label': _label}

            _use_label = label_via_string(_label)
            _url = url_via_href(_href)
            _add_on = markdown_link_via(_use_label, _url)
            yield {'add_on': _add_on}

    o = _lib()
    markdown_link_via = o.markdown_link_via
    url_via_href = o.url_via_href_via_domain(_domain)
    label_via_string = o.label_via_string_via_max_width(70)
    del(o)

    _cm = _lib().OPEN_DICTIONARY_STREAM_VIA(
        url=_url,
        first_selector=_first_selector,
        second_selector=my_generator,
        html_document_path=html_document_path,
        listener=listener,
        )

    return _cm


def _lib():
    import script.json_stream_via_url_and_selector as lib
    return lib


if __name__ == '__main__':
    import sys as o
    o.path.insert(0, '')
    import script_lib as sl
    _exitstatus = sl.CHEAP_ARG_PARSE(
        cli_function=_my_CLI,
        std_tuple=(o.stdin, o.stdout, o.stderr, o.argv),
        help_values={'url': _url},
        )
    exit(_exitstatus)

# #born
