#!/usr/bin/env python3 -W error::Warning::0

"""
stream of a pretty dump of every dictionary from every toml fellow.

currently this is for inspection (development & debugging) only.

arrangements could be made to make this more machine readable but currently
it is not very much so for practical purposes (with each JSON-like record
occupying possibly more than one line).
"""
# #[#410.1.2] this is a producer script (sort of)


from os import path as os_path


_my_desc = __doc__


def _my_parameters(o, param):

    o['themes_dir'] = param(  # ..
            description='«help for themes_dir»',
            )


class _CLI:

    def __init__(self, *_four):
        self.stdin, self.stdout, self.stderr, self._argv = _four
        self._exitstatus = 1
        self._OK = True

    def execute(self):
        import script.stream as cl  # cl = "CLI lib"
        o = self._accept_visitor
        self._OK and o(cl.must_be_interactive_)
        self._OK and o(cl.parse_args_, {'namespace': '_namespace'},
                       self._argv, _my_parameters, _my_desc)
        self._OK and setattr(self, '_listener', cl.listener_for_(self))
        self._OK and self._work()
        return self._exitstatus

    def _work(self):

        def visit(path, dct):
            sout.write(path)
            write_newline()
            pp(dct)

        def write_newline():
            sout.write('\n')
        sout = self.stdout
        import pprint
        pp = pprint.PrettyPrinter(indent=2, stream=sout).pprint
        self._exitstatus = 0
        except_first_time = _ExceptFirstTime(write_newline)
        _ = getattr(self._namespace, 'themes-dir')
        for path, dct in theme_toml_stream_via_themes_dir(_, self._listener):
            except_first_time()
            visit(path, dct)

    def _accept_visitor(self, f, settables=None, *args):
        reso = f(self, *args)
        if reso.OK:
            if settables is not None:
                self.__set_settables(reso.result_values, settables)
        else:
            self.stop_via_exitstatus_(reso.exitstatus)

    def __set_settables(self, actuals, settables):
        for (far_name, near_attr) in settables.items():
            setattr(self, near_attr, actuals[far_name])

    def stop_via_exitstatus_(self, es):
        self._exitstatus = es
        self._OK = False


def theme_toml_stream_via_themes_dir(themes_dir, listener):  # glue

    dictionary_via_toml_via_path = _make_toml_parser(listener)

    import script.SSGs.hugo_themes_deep.theme_directory_stream_via_themes_dir as _  # noqa: E501

    _ = _.open_theme_directory_stream_via_themes_dir(themes_dir, listener)
    with _ as paths:
        for path in paths:
            dct = dictionary_via_toml_via_path(path)
            if dct is not None:
                yield (path, dct)


def _make_toml_parser(listener):  # #testpoint
    import toml  # try to make this be the only place.
    # (toml dependency added at #born.)

    def dictionary_via_toml_via_path(theme_path):
        toml_path = os_path.join(theme_path, 'theme.toml')
        dct, e = parse_normally(toml_path)
        if dct is None and e is not None:
            dct = parse_try_again(e, toml_path)
        return dct

    def parse_normally(toml_path):
        dct = None
        e = None
        try:
            dct = toml.load(toml_path)
        except FileNotFoundError as e_:
            __say_not_found(listener, e_, toml_path)
        except ValueError as e_:
            e = e_
        return dct, e

    def parse_try_again(e, toml_path):
        if 'could not convert string to float' not in str(e):
            cover_me('what is the problem here')
        with open(toml_path) as fh:
            big_s = fh.read()

        import re
        use_big_s = re.sub(r'\b(min_version = )(\d\S*)', lambda md: f'{md[1]}"{md[2]}"', big_s)  # noqa: E501
        return toml.loads(use_big_s)

    return dictionary_via_toml_via_path


def __say_not_found(listener, e, toml_path):
    def f():
        yield f'skipping toml file not found: {str(e)}'
    listener('info', 'expression', 'toml_file_not_found', f)


class _ExceptFirstTime:
    def __init__(self, f):
        self._f = f
        self._yes = False

    def __call__(self):
        if self._yes:
            self._f()
        else:
            self._yes = True


def cover_me(s):
    raise Exception(f'cover me - {s}')


def woot(*_):
    raise Exception('woot')


if __name__ == '__main__':
    from relevant_themes_collection_metadata_via_themes_dir import normalize_sys_path_ as _  # noqa: E501
    _()
    import sys as o
    _exitstatus = _CLI(o.stdin, o.stdout, o.stderr, o.argv).execute()
    exit(_exitstatus)

# #born.
