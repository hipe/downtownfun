"""helper for testing CLI in a generic, magnetic-agnostic way
"""

import game_server_test.helper as helper


stream_via_memoized_array = helper.stream_via_memoized_array
shared_subject = helper.shared_subject
memoize = helper.memoize


def ARGV(f):
    """decorator to turn "short ARGVs" into "long ARGVs"

    :#here1: ARGV does or does not include PROGRAM_NAME:

    the system under test expects that the argument passed to `ARGV` will be
    structurally equivalent to `sys.argv`; by which we mean that it always
    has at least one element and that the first element is PROGRAM_NAME (or
    equivalent).

    however, neither the argument parser (from platform `argparse`) nor in
    our test stories is PROGRAM_NAME considered part of the ARGV.
    """

    def g(*args):
        a = f(*args)
        a.insert(0, PROGRAM_NAME)
        return a
    return g


class CLI_CaseMethods:

    # -- assertion methods

    def main_line_says_this_(self, wat):
        """insulate main body of test code from having to know ..

        ..whether the "main" line is the first or second line
        """
        _full_line = self.magnetic_call_.second_line
        _expected_line = '%s: error: %s%s' % (PROGRAM_NAME, wat, NEWLINE)
        self.assertEqual(_expected_line, _full_line)

    def magnetic_call_has_exitstatus_of_common_error_(self):
        self.assertEqual(2, self.magnetic_call_.exitstatus)

    def magnetic_call_results_in_failure_(self):
        self.assertFalse(self.magnetic_call_.OK)

    # magnetic_call_succeeds_ (track subscribers)

    def magnetic_call_happens_(self):
        self.assertIsNotNone(self.magnetic_call_)

    # -- these

    def invocation_when_expected_(self, num_lines, which):

        def f(sout, serr):
            interpretation_result = self._interpretation__CLI(sout, serr)
            self.assertTrue(interpretation_result.OK)
            _exe = interpretation_result.FLUSH_TO_EXECUTABLE()
            mixed_x = _exe()
            if mixed_x is None:
                return _OK_interpretation_result()
            else:
                cover_me('when execute results in a value')

        return self._same_when_expected(f, num_lines, which)

    def interpretation_when_expected_(self, num_lines, which):

        def f(sout, serr):
          return self._interpretation__CLI(sout, serr)

        return self._same_when_expected(f, num_lines, which)

    def _same_when_expected(self, f, num_lines, which):

        s_a, f_a = self._build_recording_list_and_expectation_list__CLI(num_lines)
        from game_server_test import expect_STDs

        _expectation = expect_STDs.expect_lines( (lambda: f_a), which )
        perf = _expectation.to_performance_under(self)

        _sout, _serr = self._appropriate_stdout_and_stderr__CLI(perf)

        interpretation_result = f(_sout, _serr)

        perf.finish()
        return _Invocation(interpretation_result, s_a)


    def result_when_expecting_no_output_or_errput_(self):

        return self._interpretation__CLI(None, None)


    def _interpretation__CLI(self, stdout, stderr):
        _argv = self.ARGV_()
        _command_st = self.command_stream_()

        _bldr = self.main_magnetic_().interpretation_builder_via_modality_resources(
          ARGV = _argv,
          stdout = stdout,
          stderr = stderr,
        )
        return _bldr.interpretation_via_command_stream(_command_st)

    def _appropriate_stdout_and_stderr__CLI(self, perf):
        if self.do_debug:
            # (below we assume the [#009.B] provision 2x)
            stdout = self._debugging_IO__CLI(perf.stdout, '%sohai stdout: %s')
            stderr = self._debugging_IO__CLI(perf.stderr, '%sohai stderr: %s')
        else:
            stdout = perf.stdout
            stderr = perf.stderr
        return stdout, stderr

    def _debugging_IO__CLI(self, upstream_IO, format):
        import sys
        return _MinimalIOTee(
          upstream_IO = upstream_IO,
          IO_for_debugging = sys.stderr,
          format = format,
        )


    def _build_recording_list_and_expectation_list__CLI(self, num_lines):
        """given an expected number of lines, result in two components:


        the "recording list" is an empty list that will be filled during
        the expected invocation with lines (strings).

        the "expectation list" models each expectation for each line..
        """
        s_a = []
        def f(line):
            s_a.append(line)

        _f_a = [ f for _ in helper.iterator_via_times(num_lines) ]
          # the above could just as soon be a generator expression (right?)

        return s_a, _f_a


    def main_magnetic_(self):
        import game_server._magnetics.interpretation_via_command_stream_and_ARGV as x  # noqa: E501
        return x

    # --

    @stream_via_memoized_array
    def stream_with_two_commands_(self):
      return [self._command_one__CLI(), self._command_two__CLI()]

    # --

    @shared_subject
    def _command_one__CLI(self):
        return _command_named('foo_bar')

    @shared_subject
    def _command_two__CLI(self):
        return _command_named('biff_baz')

    @property
    def do_debug(self):
        """#todo - there's no way this is the right way to do this..

        all we're trying to do is establish `do_debug` as a plain old
        attribute here that defaults to false-ish.

        the idiomatic way to do this seems to be to do
        `self.do_debug = False` from an `__init__` method BUT when we
        override `__init__` in our _CommonCase and call up to super by
        `super(self, unittest.TestCase).__init__(test_name)`, the number of
        parameters we arecalled with seems to vary?
        """
        if 'do_debug' in self.__dict__:
            return self.__dict__['do_debug']

    @do_debug.setter
    def do_debug(self, x):
        self.__dict__['do_debug'] = x


def _command_named(name):

    from modality_agnostic_test.public_support import empty_command_module as ecm  # noqa: E501
    import modality_agnostic.magnetics.command_via_parameter_stream as x
    return x.SELF(
            name=name,
            command_module=ecm(),
    )


class _Invocation:
    """simple delegator that wraps emitted lines, exitstatus, and OK"""

    def __init__(self, inter_res, s_a):
        self._interpretation_result = inter_res
        self._lines = s_a

    @property
    def second_line(self):
        return self._line(1)

    @property
    def first_line(self):
        return self._line(0)

    def _line(self, offset):
        return self._lines[offset]

    @property
    def number_of_lines(self):
        return len(self._lines)

    @property
    def exitstatus(self):  # assume failure result
        return self._interpretation_result.exitstatus

    @property
    def OK(self):
        return self._interpretation_result.OK


class _MinimalIOTee:  # TODO move this
    """a minimally simple multiplexer (muxer) for debug-tracing writes to IO"""

    def __init__(self, upstream_IO, IO_for_debugging, format):
        self._IO_for_debugging = IO_for_debugging
        self._upstream_IO = upstream_IO
        self._format = format

    def write(self, s):
        self._IO_for_debugging.write(self._format % (NEWLINE, s))
        return self._upstream_IO.write(s)


@memoize
def _OK_interpretation_result():
    class _OK_Result:
        def __init__(self):
          self.OK = True
    return _OK_Result()


@memoize
@ARGV
def the_empty_ARGV():
    return []  # EMPTY_A


NEWLINE = "\n"  #: it's not about saving memory, it's about tracking patterns

PROGRAM_NAME = 'DTF-app'


# #born.
