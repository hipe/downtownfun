# #[#874.9] file is LEGACY

from kiss_rdb import (
        LEGACY_format_adapter_via_definition as _format_adapter)


def _new_doc_lines_via_sync(**kwargs):
    return __do_new_doc_lines_via_sync(**kwargs)


def __do_new_doc_lines_via_sync(
        stream_for_sync_is_alphabetized_by_key_for_sync,
        stream_for_sync_via_stream,
        dictionaries,
        near_collection_reference,
        near_keyerer,
        DO_ENTITY_SYNC_WHEN_FAR_DICTIONARY_IS_LENGTH_ONE,
        filesystem_functions,
        listener
        ):

    # #provision [#458.L.2] iterate empty on failure

    from .magnetics_.normal_far_stream_via_collection_reference import (
            OPEN_NEAR_SESSION, FAR_STREAM_FOR_SYNC_VIA)

    ns = OPEN_NEAR_SESSION(
            keyerer=near_keyerer,
            near_collection_path=near_collection_reference.collection_identifier_string,  # noqa: E501
            listener=listener)

    if not ns:
        raise Exception('where')  # #todo
        return _empty_context_manager()  # (Case1314DP)

    # something about version number: (Case1319DP)  # #todo

    far = FAR_STREAM_FOR_SYNC_VIA(
            stream_for_sync_is_alphabetized_by_key_for_sync,
            stream_for_sync_via_stream,
            dictionaries, listener)

    def open_out(near):
        _tagged_line_items = near.release_tagged_doc_line_item_stream()
        from .magnetics_.synchronized_stream_via_far_stream_and_near_stream import (  # noqa: E501
                OPEN_NEWSTREAM_VIA)
        return OPEN_NEWSTREAM_VIA(
                normal_far_stream=far,
                near_tagged_items=_tagged_line_items,
                near_keyerer=near.keyerer,
                DO_ENTITY_SYNC_WHEN_FAR_DICTIONARY_IS_LENGTH_ONE=DO_ENTITY_SYNC_WHEN_FAR_DICTIONARY_IS_LENGTH_ONE,  # noqa: E501
                listener=listener)

    line_via = _liner()

    with ns as near, open_out(near) as out:
        for k, v in out:
            line = line_via(k, v)
            if line is None:
                break  # (Case2664DP)
            yield line


def _liner():
    """eep track of state of whether you're in a part of the document where

    the line-items are strings or not. that is all.
    #todo: refactor to be shorter
    """

    o = ExpectedTagOrder_()

    class _Liner:

        def __init__(self):
            self._item_is_string = o.per_current_top_item_is_string()

        def __call__(self, tag, item):
            _yes = o.matches_top(tag)
            if _yes:
                ok = True
            else:
                if 'markdown_table_unable_to_be_synced_against_' == tag:
                    ok = False  # (Case2664DP)
                else:
                    o.pop_and_assert_matches_top(tag)
                    self._item_is_string = o.per_current_top_item_is_string()
                    ok = True
            if ok:
                if self._item_is_string:
                    result = item
                else:
                    result = item.to_line()
            else:
                result = None
            return result

    return _Liner()


def _open_filter_request(trav_req):
    return _open_trav_request('filter', **trav_req.to_dictionary())


def _open_trav_request(
        intention,
        cached_document_path,
        collection_identifier,
        format_adapter,
        datastore_resources,
        listener):

    assert(not cached_document_path)
    # markdown tables always live in the filesystem (at writing #history-A.1),
    # never from (internet) urls so, in this sense they are already "cached"
    # so they should never be literally cached. All of this is away soon.

    from .magnetics_ import open_traversal_request_via_path as _
    return _.OPEN_TRAVERSAL_REQUEST_VIA_PATH(
            mixed_collection_identifier=collection_identifier,
            format_adapter=format_adapter,
            intention=intention,
            modality_resources=datastore_resources,
            listener=listener)


class ExpectedTagOrder_:
    """
    so:
      - each item is either itself a string or it's an object that exposes
        a `to_string()`. know which. (implementing __str__ is cheating)

      - "for free" we sanity check our understanding of the state machine

      - the spirit of [#411] (state machine processor thing), but
        self-contained, simpler by way of being more purpose-built.

      - abstraced from inline code above for #history-A.1
    """

    def __init__(self):
        self._stack = [
            ('tail_line', True),
            ('business_object_row', False),
            ('table_schema_line_two_of_two', False),
            ('table_schema_line_one_of_two', False),
            ('head_line', True),
        ]

    def per_current_top_item_is_string(self):
        return self._stack[-1][1]

    def pop_and_assert_matches_top(self, tag):
        self._stack.pop()
        if not self.matches_top(tag):
            raise Exception(f'cover me: unexpected symbol here: {tag}')

    def matches_top(self, tag):
        return self._stack[-1][0] == tag


_functions = {
        'CLI': {
            'new_document_lines_via_sync': _new_doc_lines_via_sync,
            },
        'modality_agnostic': {
            'open_filter_stream': _open_filter_request,
            },
        }


def _empty_context_manager():
    from data_pipes import my_contextlib
    return my_contextlib.empty_iterator_context_manager()


# == in oldentimes, this file was __init__.py probably. then, #history-A.2
s = __name__
_use_name = s[0:s.rindex('.')]  # like "dirname"
# ==


FORMAT_ADAPTER = _format_adapter(
        functions_via_modality=_functions,
        associated_filename_globs=('*.md',),
        format_adapter_module_name=_use_name,
        )

# #history-A.2
# #history-A.1: markdown table as producer
# #born.
