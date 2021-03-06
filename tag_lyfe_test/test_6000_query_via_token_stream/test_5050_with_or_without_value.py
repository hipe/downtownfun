"""
introduce with or without value
"""

from tag_lyfe_test.query import ScaryCommonCase
import unittest


class CommonCase(unittest.TestCase):
    do_debug = False


class Case5049_without(CommonCase, ScaryCommonCase):

    def given_tokens(self):
        return ('#foo', 'without', 'value', 'xx')

    def test_100_query_compiles(self):
        self.query_compiles()

    def test_150_unparses(self):
        self.unparses_to('#foo without value')

    def test_200_not_matches_with_value(self):
        self.does_not_match_against(('#foo:hi',))

    def test_300_yes_matches_without_value(self):
        self.matches_against(('#foo',))


# Case5050  # #midpoint


class Case5051_with(CommonCase, ScaryCommonCase):

    def given_tokens(self):
        return ('#foo', 'with', 'value', 'xx')

    def test_100_query_compiles(self):
        self.query_compiles()

    def test_150_unparses(self):
        self.unparses_to('#foo with value')

    def test_200_yes_matches_with_value(self):
        self.matches_against(('#foo:hi',))

    def test_300_not_matches_without_value(self):
        self.does_not_match_against(('#foo',))


if __name__ == '__main__':
    unittest.main()

# #born.
