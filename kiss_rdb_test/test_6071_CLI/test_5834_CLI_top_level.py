from kiss_rdb_test.common_initial_state import \
        functions_for, unindent
from kiss_rdb_test import CLI as CLI_support
from kiss_rdb_test.CLI import \
        build_filesystem_expecting_num_file_rewrites
from modality_agnostic.test_support.common import \
        dangerous_memoize as shared_subject, lazy
import unittest


class CommonCase(CLI_support.CLI_Test_Case_Methods, unittest.TestCase):

    def expect_requires_these_particular_arguments(self, *expect_these):

        # #here1
        import re
        _line = self.command_help_screen.usage_line
        md = re.match(r'^Usage: ohai-mami ([-a-z]+) \[OPTIONS\] (.+)$', _line)
        first, *actual_these = md[2].split(' ')

        # every one of these commands requires the collection (name)
        self.assertEqual(first, 'COLLECTION')

        # assert the zero or more other arguments that are required
        self.assertSequenceEqual(actual_these, expect_these)

    def expect_this_string_in_first_line_of_description(self, s):
        _line = self.command_help_screen.first_description_line
        self.assertIn(s, _line)

    def build_command_help_screen_subtree(self):
        o = self.build_end_state('stdout', None)
        self.assertEqual(o.exit_code, _success_exit_code)
        lines = tuple(o.lines)  # #here3
        assert('\n' == lines[1])  # meh
        return _StructUsageLineAndFirstDescLine(lines[0], lines[2])

    def apparently_just_prints_entire_help_screen(self):

        # #open [#867.L] the fact that exit_code=0 is an annoying thing from..

        es = self.build_end_state('stdout', None)
        exit_code = es.exit_code
        lines = tuple(es.lines)

        self.assertEqual(exit_code, _success_exit_code)

        # emits same generic message (near #here1)
        self.assertTrue('Usage:' in lines[0])

        # several lines
        self.assertTrue(3 < len(lines))

    def random_number(self):
        return None

    def filesystem(self):
        return None

    do_debug = False
    """turn on/off debugging output for the invocation of CLI commands.

    ALL of these behaviors require that `might_debug` (next) be True.

    so:
      - turn debugging on for all the tests in this file by
        setting the value to True here

      - turn debugging on for one particular test case by
        overriding the property and setting it to true in that case (class)

      - turn debugging on for one particular *test* by
        setting the property to true on the test context instance
        at the beginning of the test (method).

      - debugging can be turned on/off "momentarily" any time during the
        invocation of the test (but depending on your requirements you
        may need to code something fancy)

    (part of #here2)
    """

    might_debug = True
    """
    EXPERIMENTAL: on the one hand you can think of this as a nasty
    optimization, but on the other hand we see it as a coarse exercising of
    our dependency injection as described at #here2
    """


class Case5723_no_args(CommonCase):

    def test_100_just_prints_entire_help_screen(self):
        self.apparently_just_prints_entire_help_screen()

    def given_args(self):
        return ()


class Case5739_strange_arg(CommonCase):

    def test_100_throws_a_usage_error(self):
        self.assertEqual(self.end_exception.exit_code, 2)  # meh

    def test_200_whines_with_this_message(self):
        _msg = self.end_exception.message
        self.assertEqual(_msg, "No such command 'foo-fah-fee'.")

    @shared_subject
    def end_exception(self):
        o = self.build_end_state('stdout', 'usage_error')
        lines = tuple(o.lines)  # #here3
        self.assertEqual(len(lines), 0)
        return o.exception

    def given_args(self):
        return ('foo-fah-fee',)


class Case5756_strange_option(CommonCase):

    def test_100_just_prints_entire_help_screen(self):
        self.apparently_just_prints_entire_help_screen()

    def given_args(self):
        return ('--cho-monculous')


class Case5772_toplevel_help_in_general(CommonCase):

    def test_100_exit_code_is_whatever(self):
        self.assertEqual(_CASE_A().exit_code, _success_exit_code)

    def test_200_usage_section(self):
        # (abstract this ofc, if we ever really wanted to. #here1)
        import re
        _line_obj = _CASE_A().tree.children[0]
        _line = _line_obj.styled_content_string
        _head = re.match(r'^(.+)\.\.\.$', _line)[1]  # ends in ellipses
        _mid = re.match(r'^Usage: [-a-z]+ (.+)$', _head)[1]  # begins w this
        _ok = re.match(r'^[\[\]A-Z\. ]+$', _mid)  # mid looks like this
        self.assertIsNotNone(_ok)

    def test_300_options_section(self):
        node = _CASE_A().tree.children[2]  # the Options: section

        # the title of this section is something like "options"
        self.assertEqual(node.head_line.styled_content_string, 'Options:')

        cx = [x for x in node.children]  # make a mutable copy

        assert(cx[-1].is_blank_line)
        cx.pop()

        # the last item in the list of options is the self-referential one
        self.assertRegex(
                cx[-1].styled_content_string,
                r'^--help[ ]+Show this message and exit\.$')

        cx.pop()
        self.assertEqual(len(cx), 1)
        self.assertIn('collections-hub', cx[0].styled_content_string)


class Case5778_toplevel_help_plus_argument(CommonCase):

    def test_100_just_prints_entire_help_screen(self):
        self.apparently_just_prints_entire_help_screen()

    def given_args(self):
        return ('--help', 'fah-foo')


# Case5804_use_hub_help

# Case5853_create_hub_help


class Case5902_traverse_help(CommonCase):

    def test_100_expect_requires_these_particular_arguments(self):
        self.expect_requires_these_particular_arguments()

    def test_200_expect_this_string_in_first_line_of_description(self):
        self.expect_this_string_in_first_line_of_description(
                'traverse the collection of entities')

    @shared_subject
    def command_help_screen(self):
        return self.build_command_help_screen_subtree()

    def given_args(self):
        return ('traverse', '--help')


"""DO:
    - trav no hub
    - trav bad col
    - trav good col
"""


class Case5918_traverse_fail(CommonCase):

    def test_100_generic_failure_exit_status(self):
        self.expect_exit_code(2)  # FileNotFoundError.errno

    def test_200_message_lines(self):
        _actual, = self.end_state.lines
        reason, path = _actual.split(' - ')
        exp = 'cannot load collection: No such file or directory'
        self.assertEqual(reason, exp)
        self.assertEqual(path[0:5], 'qq/pp')

    @shared_subject
    def end_state(self):
        return self.build_end_state('stderr', None)

    def given_args(self):
        return ('--collections-hub', 'qq', 'traverse', 'pp')

    def filesystem(self):
        return real_filesystem_read_only()


class Case5934_traverse(CommonCase):

    def test_100_succeeds(self):
        self.expect_exit_code_is_the_success_exit_code()

    def test_200_lines_look_like_internal_identifiers(self):
        lines = tuple(self.end_state.lines)
        self.assertIn(len(lines), range(7, 10))
        import re
        rx = re.compile('^[A-Z0-9]{3}\n$')
        for line in lines:
            assert(rx.match(line))

    @shared_subject
    def end_state(self):
        return self.build_end_state('stdout', None)

    def given_args(self):
        return (*common_args_head(), 'traverse', _common_collection)

    def filesystem(self):
        return real_filesystem_read_only()


class Case5999_get_help(CommonCase):

    def test_100_expect_requires_these_particular_arguments(self):
        self.expect_requires_these_particular_arguments(_IID)

    def test_200_expect_this_string_in_first_line_of_description(self):
        self.expect_this_string_in_first_line_of_description(
                'retrieve the entity from the collection')

    @shared_subject
    def command_help_screen(self):
        return self.build_command_help_screen_subtree()

    def given_args(self):
        return ('get', '--help')


class Case6064_get_fail(CommonCase):

    def test_100_exit_code_is_404_lol(self):
        self.assertEqual(self.end_state.exit_code, 404)

    def test_200_says_only_not_found__with_ID(self):
        line, = self.end_state.lines
        self.assertEqual(line, (
            "entity not found: not found: 'B9F' not found\n"))  # #wish

    @shared_subject
    def end_state(self):
        return self.build_end_state('stderr', None)

    def given_args(self):
        return (*common_args_head(), 'get', _common_collection, 'B9F')

    def filesystem(self):
        return real_filesystem_read_only()


class Case6080_get(CommonCase):

    def test_100_succeeds(self):
        self.expect_exit_code_is_the_success_exit_code()

    def test_200_lines_wow(self):
        lines = self.end_state.lines
        _actual_big_string = ''.join(lines)  # correct an issue todo
        _actual_lines = tuple(_lines_via_big_string_as_is(_actual_big_string))

        _expect_big_s = """
        {
          "identifier_string": "B9H",
          "core_attributes": {
            "thing_A": "hi i'm B9H",
            "thing_B": "hey i'm B9H"
          }
        }
        """

        _expect_lines = tuple(unindent(_expect_big_s))
        self.assertSequenceEqual(_actual_lines, _expect_lines)

    @shared_subject
    def end_state(self):
        return self.build_end_state('stdout', None)

    def given_args(self):
        return (*common_args_head(), 'get', _common_collection, 'B9H')

    def filesystem(self):
        return real_filesystem_read_only()


class Case6096_create_help(CommonCase):

    def test_100_expect_requires_these_particular_arguments(self):
        self.expect_requires_these_particular_arguments()

    def test_200_expect_this_string_in_first_line_of_description(self):
        self.expect_this_string_in_first_line_of_description(
                'create a new entity in the collection')

    @shared_subject
    def command_help_screen(self):
        return self.build_command_help_screen_subtree()

    def given_args(self):
        return ('create', '--help')


class Case6113_create_fail(CommonCase):

    def test_100_exit_code_reflects_failure(self):
        self.expect_exit_code_for_bad_request()

    def test_200_reason(self):
        line, = self.end_state.lines
        self.assertEqual(line, 'request was empty\n')

    @shared_subject
    def end_state(self):
        return self.build_end_state('stderr', None)

    def given_args(self):
        return (*common_args_head(), 'create', _common_collection)

    def filesystem(self):
        return real_filesystem_read_only()


class Case6129_create(CommonCase):

    def test_100_succeeds(self):
        self.expect_exit_code_is_the_success_exit_code()

    def test_200_stdout_lines_are_toml_lines_of_created_fellow(self):
        # (the leading blank line belo keeps the first line out of test output)
        """

        currently what is written to stdout on successful create is simply
        the same lines of the mutable document entity that were inserted into
        this entities file.

        contrast this with what RETRIEVE (Case4292) does, which is to express
        to the user the retrieved entity as *json* (not toml).

        to have these two operations behave differently in this regard is
        perhaps a violation of "the principle of least astonishment"; but
        we uphold this inconsistency (for now) on these grounds:

        - the founding purpose of the CLI is towards a crude, quick-and-dirty
          debugging & development tool; not to be pretty & perfect (yet).

        - there is arguably one UI/UX benefit to the current way: when storing
          as opposed to retrieving, the user wants visual confirmation that
          nothing strange happened in encoding their "deep" data into a
          surface representation for this particular datastore.

        :#HERE3
        """

        _actual = self.common_entity_screen.stdout_lines

        _expected = tuple(unindent("""
        [item.2H3.attributes]
        aa = "AA"
        bb = "BB"
        """))

        self.assertSequenceEqual(_actual, _expected)

    def test_300_stderr_line_is_decorative(self):
        line, line2 = self.common_entity_screen.stderr_lines_one_and_two
        self.assertEqual(line, "created '2H3' with 2 attributes\n")
        self.assertIsNone(line2)

    @shared_subject
    def common_entity_screen(self):
        return self.expect_common_entity_screen()

    @shared_subject
    def end_state(self):
        return self.build_end_state('stdout_and_stderr', None)

    def given_args(self):
        return (*common_args_head(), 'create', _common_collection,
                '-val', 'aa', 'AA', '-val', 'bb', 'BB')

    def filesystem(self):
        return build_filesystem_expecting_num_file_rewrites(2)

    def random_number(self):
        return 481  # kiss ID 2H3 is base 10 481


class Case6145_delete_help(CommonCase):

    def test_100_expect_requires_these_particular_arguments(self):
        self.expect_requires_these_particular_arguments(_IID)

    def test_200_expect_this_string_in_first_line_of_description(self):
        self.expect_this_string_in_first_line_of_description(
                'delete the entity from the collection')

    @shared_subject
    def command_help_screen(self):
        return self.build_command_help_screen_subtree()

    def given_args(self):
        return ('delete', '--help')


# Case6161 - delete fail


class Case6177_delete(CommonCase):

    def test_100_succeeds(self):
        self.expect_exit_code_is_the_success_exit_code()

    def test_200_stdout_is_deleted_lines(self):

        _actual = self.common_entity_screen.stdout_lines

        _expected = tuple(unindent("""
        [item.B7G.attributes]
        thing_1 = "hi G"
        thing_2 = "hey G"
        """))

        self.assertSequenceEqual(_actual, _expected)

    def test_300_stderr_line_is_decorative(self):
        line1, line = self.common_entity_screen.stderr_lines_one_and_two
        self.assertEqual(line1.index("deleted 'B7G' with "), 0)
        self.assertEqual(line, 'deleted:\n')

    @shared_subject
    def common_entity_screen(self):
        return self.expect_common_entity_screen()

    @shared_subject
    def end_state(self):
        # return self.build_end_state_FOR_DEBUGGING()
        return self.build_end_state('stdout_and_stderr', None)

    def given_args(self):
        return (*common_args_head(), 'delete', _common_collection, 'B7G')

    def filesystem(self):
        return build_filesystem_expecting_num_file_rewrites(2)


class Case6194_update_help(CommonCase):

    def test_100_expect_requires_these_particular_arguments(self):
        self.expect_requires_these_particular_arguments(_IID)

    def test_200_expect_this_string_in_first_line_of_description(self):
        self.expect_this_string_in_first_line_of_description(
                'update the entity in the collection')

    @shared_subject
    def command_help_screen(self):
        return self.build_command_help_screen_subtree()

    def given_args(self):
        return ('update', '--help')


class Case6226_update(CommonCase):

    def test_100_succeeds(self):
        self.expect_exit_code_is_the_success_exit_code()

    def test_200_stdout_is_updated_lines_CAPTURE_WS_ISSUE(self):

        _actual = self.common_entity_screen.stdout_lines

        _expected = tuple(unindent("""
        [item.B7F.attributes]
        thing_2 = "hey F updated"

        thing_3 = "T3"
        thing_4 = "T4"
        """))

        self.assertSequenceEqual(_actual, _expected)

    def test_300_stderr_line_is_decorative(self):
        line, line2 = self.common_entity_screen.stderr_lines_one_and_two
        exp = "updated 'B7F' (created 2, updated 1 and deleted 1 attribute)\n"
        self.assertEqual(line, exp)
        self.assertIsNone(line2)

    @shared_subject
    def common_entity_screen(self):
        return self.expect_common_entity_screen()

    @shared_subject
    def end_state(self):
        return self.build_end_state('stdout_and_stderr', None)

    def given_args(self):
        return (*common_args_head(), 'update', _common_collection,
                'B7F',
                '-delete', 'thing_1',
                '-change', 'thing_2', 'hey F updated',
                '-add', 'thing_3', 'T3',
                '-add', 'thing_4', 'T4')

    def filesystem(self):
        return build_filesystem_expecting_num_file_rewrites(1)


@lazy
def _CASE_A():  # usually it's one invocation

    o = CLI_support.BIG_FLEX(
            given_stdin=None,
            given_args=('--help',),
            allow_stdout_lines=True,
            allow_stderr_lines=False,
            exception_category=None,
            injections_dictionary=None,
            might_debug=False,  # ..
            do_debug_f=lambda: False,  # ..
            )

    _tree = CLI_support.tree_via_lines(o.lines)
    return _StructTreeAndExitCode(_tree, o.exit_code)


class _StructUsageLineAndFirstDescLine:
    def __init__(self, *two):
        self.usage_line, self.first_description_line = two


class _StructTreeAndExitCode:
    def __init__(self, *two):
        self.tree, self.exit_code = two


@lazy
def real_filesystem_read_only():
    # push this up whenever - use the real filesystem but the same testy hook
    from kiss_rdb import real_filesystem_read_only__ as fser
    fs = fser()  # not really necessary
    otr = fs.__class__(commit_file_rewrite=None)
    otr.FINISH_AS_HACKY_SPY = lambda: None
    return otr


def _lines_via_big_string_as_is(big_string):
    import kiss_rdb.storage_adapters_.toml.CUD_attributes_via_request as lib
    return lib.lines_via_big_string_(big_string)


common_args_head = functions_for('toml').common_args_head


# == general

_common_collection = '050-rumspringa'
_IID = 'INTERNAL_IDENTIFIER'

_success_exit_code = 0

if __name__ == '__main__':
    unittest.main()

# #history-A.1 they fixed their abuse of exceptions for some cases
# #born.
