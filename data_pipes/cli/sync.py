"""
description: for a given particular natural key field name, for each item

in the "near collection", see if you can pair it up with an item in the
"far collection" based on that natural key field name.

EDIT
(the natural key field name is "declared" by the far collection.)

for each given near item, when a corresponding far item exists by the above
criteria, the values of those components in the near item that exist in the
far item are clobbered with the far values.

(the near item can have field names not in the far item, but if the far item
has field names not in the near item, we express this as an error and halt
further processing.)

(after this item-level merge, the far item is removed from a pool).

at the end of all this, each far item that had no corresponding near item
(i.e. that did not "pair up") is simply appended to the near collection.

(this is a synopsis of an algorithm that is described [#447] more formally.)
"""
# #[#874.5] file used to be executable script and may need further changes


from data_pipes import common_producer_script
cli_lib = common_producer_script.common_CLI_library()
biz_lib = cli_lib


_desc = __doc__


def _my_parameters(o, param):

    o['near_collection'] = param(
            description='«help for near_collection»',
            )

    o['near_format'] = param(
            description=biz_lib.try_help_('«the near_format»'),
            argument_arity='OPTIONAL_FIELD',
            )

    biz_lib.common_parameters_from_the_script_called_stream_(o, param)

    # (the following option *should* come from the above function call but it
    # is rarely used and probably not covered in scripts other than this one)
    o['far_format'] = param(
            description=biz_lib.try_help_('«the far_format»'),
            argument_arity='OPTIONAL_FIELD',
            )

    def diff_desc():  # be like [#511.3]
        yield "show only the changed lines as a diff"

    o['diff'] = param(
            description=diff_desc,
            argument_arity='FLAG',
            )


def _pop_property(self, prop):
    from data_pipes import pop_property
    return pop_property(self, prop)


class _CLI:  # #open [#607.4] de-customize this custom CLI

    def __init__(self, *_four):
        # (Case3061)
        self.stdin, self.stdout, self.stderr, self.ARGV = _four  # #[#608.6]
        self.exitstatus = 5  # starts as guilty til proven innocent
        self.OK = True

    def execute(self):
        cl = cli_lib
        cl.must_be_interactive_(self)
        self.OK and cl.parse_args_(self, '_namespace', _my_parameters, _desc)
        self.OK and self.__init_normal_args_via_namespace()
        self.OK and biz_lib.maybe_express_help_for_format_(
                self, self._normal_args['near_format'])
        self.OK and biz_lib.maybe_express_help_for_format_(
                self, self._normal_args['far_format'])
        self.OK and setattr(self, '_listener', cl.listener_for_(self))
        self.OK and self.__call_over_the_wall()
        return self._pop_property('exitstatus')

    def __call_over_the_wall(self):

        self.exitstatus = 0  # now that u made it this far innocent til guilty

        _d = self._pop_property('_normal_args')
        _context_manager = open_new_lines_via_sync_(
                **_d,
                listener=self._listener,
                )

        if self._do_diff:
            line_consumer = self.__build_line_consumer_for_dyff_lyfe()
        else:
            line_consumer = _LineConsumer_via_STDOUT(self.stdout)

        with _context_manager as lines, line_consumer as receive_line:
            for line in lines:
                receive_line(line)

    def __build_line_consumer_for_dyff_lyfe(self):
        return _FancyDiffLineConsumer(
                stdout=self.stdout,
                near_collection_path=self._near_collection,
                tmp_file_path='z/tmp',  # #todo
                )

    def __init_normal_args_via_namespace(self):
        ns = self._pop_property('_namespace')

        near_collection = getattr(ns, 'near-collection')
        self._near_collection = near_collection

        self._do_diff = ns.diff
        self._normal_args = {
                'near_collection': near_collection,
                # ^ #open [#459.M]: dashes to underscores is getting annoying
                'far_collection': getattr(ns, 'far-collection'),
                'near_format': ns.near_format,
                'far_format': ns.far_format,
                }

    _pop_property = _pop_property


def open_new_lines_via_sync_(  # #testpoint
        producer_script_path,
        near_collection,
        listener,
        near_format=None,  # gives a hint, if filesystem path extension ! enuf
        cached_document_path=None,  # for tests
        ):

    # resolve the function for syncing from the near collection reference
    near_coll_ref = biz_lib.collection_reference_via_(
            near_collection, listener, near_format)
    if near_coll_ref is None:
        return _empty_context_manager()

    def ew():
        yield ('CLI', 'modality functions')
        yield ('new_document_lines_via_sync', 'CLI modality function')

    new_lines_via = near_coll_ref.format_adapter.DIG_HOI_POLLOI(ew(), listener)
    if new_lines_via is None:
        return _empty_context_manager()

    # resolve the producer script from the far collection reference (for now)

    if hasattr(producer_script_path, 'HELLO_I_AM_MOCK_PRODUCER_SCRIPT'):
        ps = producer_script_path
    else:
        from kiss_rdb.cli.LEGACY_stream import module_via_path
        ps = module_via_path(producer_script_path, listener)

        if ps is None:
            return _empty_context_manager()

    # money

    class ContextManager:

        def __enter__(self):
            self._exit_me = ps.open_traversal_stream(
                    listener, cached_document_path)
            _dictionaries = self._exit_me.__enter__()
            return new_lines_via(
                    stream_for_sync_is_alphabetized_by_key_for_sync=ps.stream_for_sync_is_alphabetized_by_key_for_sync,  # noqa: E501
                    stream_for_sync_via_stream=ps.stream_for_sync_via_stream,
                    dictionaries=_dictionaries,
                    near_collection_reference=near_coll_ref,
                    DO_ENTITY_SYNC_WHEN_FAR_DICTIONARY_IS_LENGTH_ONE=ps.DO_ENTITY_SYNC_WHEN_FAR_DICTIONARY_IS_LENGTH_ONE,  # noqa: E501
                    near_keyerer=ps.near_keyerer,
                    filesystem_functions=None,
                    listener=listener)

        def __exit__(self, *_3):
            em = self._exit_me
            del self._exit_me
            return em.__exit__(*_3)

    return ContextManager()


class _FancyDiffLineConsumer:

    def __init__(self, stdout, near_collection_path, tmp_file_path):
        self._tmp_file = open(tmp_file_path, 'w+')
        self._sout = stdout
        self._near_collection_path = near_collection_path

    def __enter__(self):
        return self._receive_line

    def _receive_line(self, line):  # (Case3070)
        self._tmp_file.write(line)

    def __exit__(self, ex, *_):

        if ex is None:
            self._close_normally()
        return False

    def _close_normally(self):

        sout = self._sout

        from_path = self._near_collection_path

        use_fromfile = 'a/%s' % from_path
        use_tofile = 'b/%s' % from_path

        # (the thing doesn't output this line but we need it to use gitx)
        sout.write("diff %s %s\n" % (use_fromfile, use_tofile))

        to_IO = _pop_property(self, '_tmp_file')
        to_IO.seek(0)

        YUCK_to_lines = [x for x in to_IO]
        to_IO.close()

        with open(from_path) as lines:
            YUCK_from_lines = [x for x in lines]

        from difflib import unified_diff

        _lines = unified_diff(
                YUCK_from_lines,
                YUCK_to_lines,
                fromfile=use_fromfile,
                tofile=use_tofile,
                )

        for line in _lines:
            sout.write(line)

        # #todo - rm to_IO.name (currently kept for debugging)

        return False


class _LineConsumer_via_STDOUT:

    def __init__(self, sout):
        self._sout = sout

    def __enter__(self):
        return self._receive_line

    def _receive_line(self, line):
        self._sout.write(line)

    def __exit__(self, *_):
        return False


class _empty_context_manager:  # #todo
    def __enter__(self):
        return ()

    def __exit__(self, *_3):
        return False


def cli_for_production():
    import sys as o
    _exitstatus = _CLI(o.stdin, o.stdout, o.stderr, o.argv).execute()
    exit(_exitstatus)

# #history-A.2: map-for-sync abstracted out of this
# #history-A.1: replace hand-written argparse with agnostic modeling
# #born.
