"""this is a *100% copy-paste* of the inelegant #[#019.file-type-C]. see."""

import sys


def _():
    import os

    path = os.path
    dn = path.dirname

    a = sys.path
    head = a[0]

    test_sub_dir = dn(__file__)
    top_test_dir = dn(test_sub_dir)
    project_dir = dn(top_test_dir)

    if test_sub_dir != head:
        raise Exception('sanity')

    a[0] = project_dir


_()

import grep_dump_test._init as yikes  # noqa: E402

sys.modules[__name__] = yikes

# #born.
