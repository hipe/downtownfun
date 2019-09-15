from modality_agnostic.memoization import lazy
import os.path as os_path


def build_end_state_commonly(self):  # (stowaway - relevant to FA's only)

    import modality_agnostic.test_support.listener_via_expectations as lib

    exp = lib(self.expect_emissions())
    listener = exp.listener

    _d = self.given()

    _cm = _sync_context_manager_via(**_d, listener=listener)

    with _cm as lines:
        lines = tuple(lines)

    _ = exp.actual_emission_index_via_finish()
    return _EndState(lines, _)


class ProducerCaseMethods:

    def build_YIKES_SYNC_(self):

        _far_coll_id = _norm_path(self.far_collection_identifier())
        _near_coll_id = self.near_collection_identifier()
        _listener = self.use_listener()

        _cm = _sync_context_manager_via(
                far_collection=_far_coll_id,
                near_collection=_near_coll_id,
                near_format='markdown_table',
                listener=_listener)

        with _cm as lines:
            lines = tuple(x for x in lines)

        return lines

    def build_pair_list_for_inspect_(self):

        _cdp = self.cached_document_path()
        _ci = _norm_path(self.far_collection_identifier())
        _listener = self.use_listener()
        _ = _this_stream_lib()._traversal_stream_for_sync(
                cached_document_path=_cdp,
                collection_identifier=_ci,
                listener=_listener)
        return tuple(_)

    def build_dictionaries_tuple_from_traversal_(self):

        _cdp = self.cached_document_path()
        _ci = _norm_path(self.far_collection_identifier())
        _listener = self.use_listener()
        _ = _this_stream_lib().open_traversal_stream_TEMPORARY_LOCATION(
                cached_document_path=_cdp,
                collection_identifier=_ci,
                listener=_listener)
        with _ as dcts:
            return tuple(dcts)  # (much simplified at #history-A.2)

    def cached_document_path(self):
        return None

    def use_listener(self):
        from modality_agnostic import listening as _
        return _.throwing_listener

    def LISTENER_FOR_DEBUGGING(self):
        import modality_agnostic.test_support.listener_via_expectations as _
        return _.for_DEBUGGING


def _norm_path(path):
    return path  # ..


def _sync_context_manager_via(**kwargs):
    from data_pipes.cli.sync import open_new_lines_via_sync_
    return open_new_lines_via_sync_(**kwargs)


class _EndState:
    def __init__(self, outputted_lines, aei):
        self.outputted_lines = outputted_lines
        self.actual_emission_index = aei


def executable_fixture(stem):
    return os_path.join(_top_test_dir(), 'fixture_executables', stem)


def html_fixture(tail):
    return os_path.join(_fixture_files(), '500-html', tail)


def markdown_fixture(tail):
    return os_path.join(_fixture_files(), '300-markdown', tail)


@lazy
def _fixture_files():
    return os_path.join(_top_test_dir(), 'fixture-files')


@lazy
def _top_test_dir():
    return os_path.dirname(__file__)


def _this_stream_lib():
    from data_pipes import common_producer_script
    return common_producer_script.common_CLI_library()


def cover_me(s=None):
    msg = 'cover me'
    if s is not None:
        msg = '{}: {}'.format(msg, s)
    raise Exception(msg)


# #history-A.2: no more sync-side entity mapping
# #history-A.1: upgraded to python 3.7, things changed
# #born.
