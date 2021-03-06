"""A toolkit of functions to assist in making test cases for CUD+R.

- Most functions are oriented around producing or consuming a `run` function.
- A `run` function is simply a function that takes nothing but a listener.
- #open [#867.Z] not yet fully divorced from toml
"""

from modality_agnostic import throwing_listener as _throwing_listener
from modality_agnostic.test_support.common import lazy


# == functions (public & private because the boundary is plastic)

def expect_big_success(tc):
    mde = _MDE_given_body_lines(tc)
    run = _run_given_edit_tuples_and_MDE(tc, mde)
    result_value = run(_throwing_listener)
    tc.assertTrue(result_value is True)
    exp = tuple(_unindent(tc.expect_entity_body_lines()))
    blocks = mde.to_body_block_stream_as_MDE_()
    lines = (line for block in blocks for line in block.to_line_stream())
    act = tuple(lines)
    tc.assertSequenceEqual(act, exp)


def emission_payload_expecting_error_given_edit_tuples(tc, which):
    run = run_given_edit_tuples(tc)
    return _emission_payload_for(tc, run, which)


def emission_payload_expecting_error_given_run(tc, which):
    run = tc.given_run
    return _emission_payload_for(tc, run, which)


def _emission_payload_for(tc, run, which):
    listener, emissions = em().listener_and_emissions_for(tc, limit=1)
    tc.assertIsNone(run(listener))  # None not False (provision [#867.R])
    emi, = emissions
    tc.assertSequenceEqual(emi.channel, ('error', 'structure', which))
    return emi.payloader()


def run_given_edit_tuples(tc):
    return _run_given_edit_tuples_and_MDE(tc, _MDE_given_body_lines(tc))


def _run_given_edit_tuples_and_MDE(tc, mde):
    def run(listener):
        return req.mutate_created_document_entity__(mde, bs, listener)
    req = request_via_tuples(tc.given_request_tuples(), _throwing_listener)
    bs = _default_business_schema()
    return run


def filesystem_recordings_of(tc, verb, *args):
    coll = tc.given_collection()
    run = run_for(coll, verb, *args)
    result_value = run(_throwing_listener)
    # result value will vary depending on the edit. seems strange to toss it
    tc.assertIsNotNone(result_value)
    return coll.custom_functions._filesystem.FINISH_AS_HACKY_SPY()


def run_for(coll, verb, *args):
    def run(listener):
        return run_via_collection(coll, listener)
    run_via_collection = _run_via_collection_via_verb[verb](*args)
    return run


def _run_via_collection_for_update(id_s, cuds):
    def run_via_collection(coll, listener):
        return coll.update_entity(id_s, cuds, listener)
    return run_via_collection


def _run_via_collection_for_create(cuds):
    def run_via_collection(coll, listener):
        return coll.create_entity(cuds, listener)
    return run_via_collection


def _run_via_collection_for_delete(id_s):
    def run_via_collection(coll, listener):
        return coll.delete_entity(id_s, listener)
    return run_via_collection


def _run_via_collection_for_retrieve(id_s):
    def run_via_collection(coll, listener):
        return coll.retrieve_entity(id_s, listener)
    return run_via_collection


_run_via_collection_via_verb = {
        'update': _run_via_collection_for_update,
        'create': _run_via_collection_for_create,
        'delete': _run_via_collection_for_delete,
        'retrieve': _run_via_collection_for_retrieve,
        }


def _MDE_given_body_lines(tc):
    body_lines = _unindent(tc.given_entity_body_lines())
    _tslo = _same_TSLO_doesnt_matter()  # tslo = table start line object
    return _models_lib().MDE_via_lines_and_table_start_line_object(
        body_lines, _tslo, _throwing_listener)


def request_via_tuples(tuples, listener):
    from kiss_rdb.magnetics_ import CUD_attributes_request_via_tuples as lib
    return lib.request_via_tuples(tuples, listener)


# == memoized

@lazy
def _same_TSLO_doesnt_matter():  # tslo = table start line object
    return _models_lib().TSLO_via('A', 'meta')


@lazy
def _default_business_schema():
    from kiss_rdb.storage_adapters_.toml import (
            business_schema_via_definition as lib)
    return lib.DEFAULT_BUSINESS_SCHEMA


# == delegations

def filesystem_expecting_no_rewrites():
    return _fs_lib().filesystem_expecting_no_rewrites()


def build_filesystem_expecting_num_file_rewrites(expected_num):
    return _fs_lib().build_filesystem_expecting_num_file_rewrites(expected_num)


def _DEBUGGING_LISTENER():
    return em().debugging_listener()


def _unindent(big_string):
    from text_lib.magnetics.via_words import unindent
    return unindent(big_string)


# == libs

def _models_lib():
    from . import common_initial_state as _
    return _


def _fs_lib():
    import modality_agnostic.test_support.mock_filehandle as module
    return module


def em():
    import modality_agnostic.test_support.common as _
    return _

# ==

# #history-B.4
# #history-A.2
# #history-A.1 dissolved methods modules into a toolkit of functions
# #abstracted.
