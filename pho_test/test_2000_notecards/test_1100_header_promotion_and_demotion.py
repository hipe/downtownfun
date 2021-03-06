from pho_test.document_state import SexpCase, document_state_via_notecards
from modality_agnostic.test_support.common import (
        dangerous_memoize as shared_subject)
import unittest


class CommonCase(unittest.TestCase):

    def build_state(self):
        return document_state_via_notecards(self.given_notecards())


# (1100-1190)

class Case1115_sexps_from_this_body(SexpCase):

    def expected_sexps(_):
        yield 'header_line'
        yield 'blank_line_run', 1
        yield 'content_run', 1
        yield 'blank_line_run', 1
        yield 'code_fence_run', 4
        yield 'blank_line_run', 2
        yield 'content_run', 2

    def given_lines(_):
        yield '# Imagine\n'
        yield '\n'
        yield 'Like so:\n'
        yield '\n'
        yield '```fiz\n'
        yield '# not a header\n'
        yield '[not a link][1]\n'
        yield '```\n'
        yield '\n'
        yield '\n'
        yield 'Donezo.\n'
        yield 'Funzo.\n'


class Case1120_one_notecard_with_heading_and_leading_header(CommonCase):

    def test_100_heading_of_first_notecard_becomes_doc_title(self):
        self.assertEqual(self.end_state.document_title, 'dogs are great')

    def test_200_header_gets_pushed_down_one_level(self):  # provision [#883.3]
        self.assertEqual(self.end_state.first_section.header.depth, 2)

    def test_300_header_gets_pushed_down_for_subsequent_section(self):
        self.assertEqual(self.end_state.section_at(1).header.depth, 2)

    @shared_subject
    def end_state(self):
        return self.build_state()

    def given_notecards(self):
        yield 'dogs are great', ('#ha ha', 'so good', '#h3', 'yup')


class Case1150_nonfirst_notecard_headings(CommonCase):

    def test_100_turn_nonfirst_notecard_heading_into_header(self):
        act = self._this_header().label_text
        self.assertEqual(act, 'dogs are cool')

    def test_200_this_header_becomes_the_common_depth(self):
        self.assertEqual(self._this_header().depth, 2)

    def _this_header(self):
        return self.end_state.section_at(1).header

    @shared_subject
    def end_state(self):
        return self.build_state()

    def given_notecards(self):
        yield 'dogs', ('#h', 'xx1')
        yield 'dogs are cool', ('xx3',)


class Case1180_nonfirst_notecards_with_heading_and_headers(CommonCase):

    def test_100_headers_are_bumped_down_a_level_EVERYTHING(self):
        state = self.build_state()

        hdr = state.section_at(1).header
        assert hdr.label_text == 'dogs are cool'
        self.assertEqual(hdr.depth, 2)

        hdr = state.section_at(2).header
        assert hdr.label_text == 'loved dog #1'
        self.assertEqual(hdr.depth, 3)

        hdr = state.section_at(3).header
        assert hdr.label_text == 'loved dog #2'
        self.assertEqual(hdr.depth, 3)

    def given_notecards(self):
        yield 'dogs', ('#h', 'xx1')
        yield 'dogs are cool', ('#loved dog #1', 'abc', '#loved dog #2', 'xx')


class Case1210_nonfirst_notecards_with_NO_heading_YES_headers(CommonCase):

    def test_100_headers_are_NOT_bumped_down_a_level_EVERYTHING(self):
        state = self.build_state()

        hdr = state.section_at(1).header
        assert(hdr.label_text == 'loved dog #1')
        self.assertEqual(hdr.depth, 2)

        hdr = state.section_at(2).header
        assert(hdr.label_text == 'loved dog #2')
        self.assertEqual(hdr.depth, 2)

    def given_notecards(self):
        yield 'dogs', ('#h', 'xx1')
        yield None, ('#loved dog #1', 'abc', '#loved dog #2', 'xx')


def xx(*_):
    raise RuntimeError('ohai')


if __name__ == '__main__':
    unittest.main()

# #born.
