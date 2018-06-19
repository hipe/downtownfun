"""this is *the* [#019.file-type-D]. see."""

import os.path as os_path


def _():
    dn = os_path.dirname
    import sys

    a = sys.path
    head = a[0]

    top_test_dir = dn(__file__)
    project_dir = dn(top_test_dir)

    if project_dir == head:

        pass  # assume low entrypoint loaded us to use for resources

    elif top_test_dir == head:
        None if '' == a[1] else sanity()
        a[0] = project_dir
        a[1] = top_test_dir  # [#019.why-this-in-the-second-position]

    else:
        sanity()

    return (top_test_dir,)


def build_end_state_commonly(self):  # (stowaway - relevant to FA's only)

    import modality_agnostic.test_support.listener_via_expectations as lib

    exp = lib(self.expect_emissions())

    _d = self.given()

    import script.sync as lib
    _lines_opener = lib.OpenNewLines_via_Sync_(
            ** _d,
            listener=exp.listener,
            )

    line_a = []

    with _lines_opener as lines:
        for line in lines:
            line_a.append(line)

    _ = exp.actual_emission_index_via_finish()
    return _EndState(tuple(line_a), _)


class _EndState:
    def __init__(self, outputted_lines, aei):
        self.outputted_lines = outputted_lines
        self.actual_emission_index = aei


def minimal_listener_spy():
    """similar elsewhere. this one is minimal.

    #open [#410.I] the soul of this has been stolen and moved to [#509]
    """

    def listener(*a):
        None if 'error' == a[0] else sanity(a[0])
        None if 'expression' == a[1] else sanity(a[1])
        a[-1](o)

    def o(s):
        mutable_message_array.append(s)

    mutable_message_array = []
    return (mutable_message_array, listener)


def fixture_executable_path(stem):
    return os_path.join(_top_test_dir, 'fixture_executables', stem)


def fixture_file_path(stem):
    return os_path.join(_top_test_dir, 'fixture-files', stem)


def release(self, prop):
    x = getattr(self, prop)
    delattr(self, prop)
    return x


def cover_me(s=None):
    msg = 'cover me'
    if s is not None:
        msg = '{}: {}'.format(msg, s)
    raise Exception(msg)


def sanity(s='assumption failed'):
    raise Exception(s)


(
    _top_test_dir,
) = _()

# #born.
