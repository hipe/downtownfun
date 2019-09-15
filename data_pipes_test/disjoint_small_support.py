"""(abstracted.)"""


def build_state_the_bernstein_way(fixture_document_path, producer_module):
    """
    given a fixture document path and a producer module (usually script),

    produce an end-state of commonly tested-against summary information.

    we assume the provisions:
      - the human key field name of the formal record is called 'name'
      - the values (names) tha occur in this field look like markdown
        links (e.g "[Foo Bar 12](gopher://foo.edu)")

    the produced end state has as properties (at least):
      - a dictionary with every business record (dictionary, also)
        keyed to a lossy, simplified representation of the business
        item name.
    """

    from modality_agnostic import listening as _
    listener = _.throwing_listener

    # == BEGIN change for #history-A.1

    # (normally we would pass the below two arguments as named parameters but
    # in this case we can't because the parameter name will change based on
    # the format, so for once we must rely solely on parameter order. listener
    # is first b.c it makes (sans fixture) prod scripts read more smoothly.)

    _open_traversal_stream = producer_module.open_traversal_stream(
            listener,
            fixture_document_path,  # {html_document_path|markdown_path}, e.g
            )

    seen = {}
    objs = {}

    with _open_traversal_stream as dcts:
        _stream_for_sync = producer_module.stream_for_sync_via_stream(dcts)
        for key, dct in _stream_for_sync:
            for sub_key in dct.keys():
                seen[sub_key] = None
            objs[key] = dct

    # def fuzzy_key(dct):
    #   return simplified_key_via_markdown_link(dct['name'])

    # from data_pipes import common_producer_script as mod
    # _ = mod.LEGACY_markdown_lib().simplified_key_via_markdown_link_er
    # simplified_key_via_markdown_link = _()

    # with _open_traversal_stream as dcts:
    #    head_dct = next(dcts)
    #    objs = {fuzzy_key(dct): dct for dct in dcts}
    # #todo rid of all above

    # == END

    class EndState:  # #class-as-namespace
        sync_keys_seen = seen
        entity_dictionary_via_sync_key = objs

    return EndState


# #history-A.1
# #abstracted.
