"""
introduce negation.
"""

from tag_lyfe_test.query import ScaryCommonCase
import unittest


class CommonCase(unittest.TestCase):
    do_debug = False


class Case4050_simple(CommonCase, ScaryCommonCase):  # #midpoint

    def given_tokens(self):
        return ('not', '#foo', 'xx')

    def test_100_query_compiles(self):
        self.query_compiles()

    def test_150_unparses(self):
        self.unparses_to('not #foo')

    def test_200_yes_tag_not_matches(self):
        self.does_not_match_against(('#foz', '#foo'))

    def test_300_against_no_tag_yes_matches(self):
        self.matches_against(('#bar', '#baz'))


class Case4060_rumskalla_integration(CommonCase, ScaryCommonCase):

    def given_tokens(self):
        return ('#foo', 'and', 'not', '#bar:baz', 'xx')

    def test_100_query_compiles(self):
        self.query_compiles()

    def test_150_unparses(self):
        self.unparses_to('#foo and not #bar:baz')

    def test_200_not_matches_this(self):
        self.does_not_match_against(('#foo', '#bar:baz'))

    def test_250_yes_matches_this(self):
        self.matches_against(('#bar:bazzo', '#other', '#foo'))


if __name__ == '__main__':
    unittest.main()

# #born.
