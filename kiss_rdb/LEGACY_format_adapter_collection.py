from sakin_agac import (
        cover_me,
        )
from modality_agnostic.memoization import lazy


def procure_format_adapter(**kwargs):
    return _ProcureFormatAdapter(**kwargs).execute()


class _ProcureFormatAdapter:
    """"procure" is an essential part of [#505] our collections API.

    this is a specialization of it: given a filesystem path (a filename)
    and possibly a format name, we result in a name-value pair for a format
    adapter (where the name is a string like 'markdown_table' and the value
    is the platform module, loaded).
    """

    def __init__(
            self,
            collection_identifier,
            format_identifier,
            listener,
            ):

        self._collection_identifier = collection_identifier
        self._format_identifier = format_identifier
        self._listener = listener
        self.__these = None

    def execute(self):

        if self._format_identifier is None:
            x = self.__when_via_collection_identifier()
        else:
            x = self.__when_via_format_identifier()
        return x

    def __when_via_collection_identifier(self):
        if isinstance(self._collection_identifier, str):
            return self.__when_via_collection_identifier_as_string()
        else:
            return self.__when_in_memory()

    def __when_in_memory(self):
        # arrived in #history-A.2. begin #track [#410.L]. #coverpoint5.3
        import sakin_agac_test.format_adapters.in_memory_dictionaries as lib
        return ('in_memory_dictionaries', lib)

    def __when_via_collection_identifier_as_string(self):
        import os
        _stem, ext = os.path.splitext(self._collection_identifier)
        if ext == '':
            # #coverpoint13.1
            def f(o, _=None):  # #open #[#508]
                o("can't infer filename type from a file with no extension - %s" % self._collection_identifier)  # noqa: E501
            self._listener('error', 'expression', 'file_extension_required', f)
        else:
            return self.__do_when_via_collection_identifier(ext)

    def __do_when_via_collection_identifier(self, ext):

        import fnmatch
        path = self._collection_identifier

        def _subfeatures_via_item(_human_key, mod):
            return mod.FORMAT_ADAPTER.associated_filename_globs

        return self._procure(
            needle_function=lambda glob: fnmatch.fnmatch(path, glob),
            say_needle=lambda: repr(ext),
            subfeatures_via_item=_subfeatures_via_item,
            item_noun_phrase='format adapter that recognizes filename extension',  # noqa: E501
            channel_tail_component_on_not_found='file_extension_not_matched',
            )

    def __when_via_format_identifier(self):

        def _needle_function(human_key):
            return needle == human_key  # ..  we have to learn about rx esc for

        needle = self._format_identifier

        return self._procure(
            needle_function=_needle_function,
            say_needle=lambda: repr(needle),
            item_noun_phrase='format adapter',
            channel_tail_component_on_not_found='format_adapter_not_found',
            )

    def _procure(
            self,
            needle_function,
            say_needle,
            item_noun_phrase,
            channel_tail_component_on_not_found,
            subfeatures_via_item=None,
            ):

        kwargs = {}
        if subfeatures_via_item is not None:
            kwargs['subfeatures_via_item'] = subfeatures_via_item

        return _collection_lib().procure(
            human_keyed_collection=self._these(),
            needle_function=needle_function,
            say_needle=say_needle,
            item_noun_phrase=item_noun_phrase,
            channel_tail_component_on_not_found=channel_tail_component_on_not_found,  # noqa: E501
            listener=self._listener,
            **kwargs)

    def _these(self):
        if self.__these is None:
            self.__these = self.__build_this_thing()
        return self.__these

    def __build_this_thing(self):
        _pairs = to_name_value_pairs()
        _ = _collection_lib()
        return _.human_keyed_collection_via_pairs_cached(_pairs)


def to_name_value_pairs():
    for mod in EVERY_MODULE():  # (was gen ex before #historyA.3)
        fa = mod.FORMAT_ADAPTER
        if fa is not None:
            yield fa.format_name, mod


@lazy
def EVERY_MODULE():
    """result is an iterator over every such module.

    don't let the `lazy` fool you: this function is re-entrant:

    it can be called multiple times, and the filesystem is hit anew each
    time. (so if you weirdly add or remove filesystem nodes at runtime, it
    would get picked up.)
    """

        return modules_via_directory_and_mod_name(*main_module_tuple)

    def _ALTERNATE_FOR_REFERENCE():
        # (this worked when it was written.)
        # (it's "proof" that we can support multiple adapter dirs)
        for x in modules_via_directory_and_mod_name(*main_module_tuple):
            yield x
        for x in modules_via_directory_and_mod_name(*other_module_tuple):
    def main():
            yield x

    def modules_via_directory_and_mod_name(direc, mod_name):

        _this_glob = os_path.join(direc, '*')
        _entries = (os_path.basename(x) for x in glob_glob(_this_glob))

        def stems():
            # before #history-A.1 this used to be an elegant generator
            # expression, and could probably be made one again (a reduce)
            for entry in _entries:
                md = rx.search(entry)
                if md is not None:
                    yield md[1]

        _stems = stems()
        return (importlib.import_module('.%s' % x, mod_name) for x in _stems)

    from os import path as os_path
    dn = os_path.dirname
    import re

    main_dir = dn(__file__)

    main_module_tuple = (main_dir, __name__)

    if False:  # (see related test above)
        these = ('sakin_agac_test', 'format_adapters')
        other_module_tuple = (
                os_path.join(dn(dn(main_dir)), * these),
                '.'.join(these),
                )

    rx = re.compile(r'(^(?!_)[^\.]+)(?:\.py)?$')
    """
    such that:
      - don't match if it starts with an underscore
      - if it has an extension, the extension must be '*.py'
      - fnmatch might be more elegant, but we don't know it yet
    """

    import importlib
    from glob import glob as glob_glob
    return main


def _collection_lib():
    import sakin_agac.magnetics.via_human_keyed_collection as x
    return x


# #history-A.3: as referenced
# #history-A.2: as referenced
# #history-A.1: as referenced
# #born.
