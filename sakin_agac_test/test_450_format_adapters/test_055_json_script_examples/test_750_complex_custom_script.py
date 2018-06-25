from _init import (
        fixture_file_path,
        )
from modality_agnostic.memoization import (
        dangerous_memoize as shared_subject,
        memoize,
        )
import unittest


class _CommonCase(unittest.TestCase):
    pass


class Case200(_CommonCase):

    def test_010_loads(self):
        self.assertIsNotNone(_subject_module())

    def test_020_three_sections(self):  # #coverpoint8.1
        _act = len(self._shared_state().sections)
        self.assertEqual(_act, 3)

    def test_030_this_many_objects_in_each_section(self):
        _act = [len(x.item_strings) for x in self._shared_state().sections]
        self.assertSequenceEqual(_act, (3, 3, 3))

    def test_040_said_seen_N_of_same(self):
        _ohai = self._shared_state().emissions
        _act = _ohai[3].to_string()
        _exp = '(first was subset of second (3 were same))'
        self.assertEqual(_act, _exp)

    @shared_subject
    def _shared_state(self):

        emissions = []
        sections = []

        import modality_agnostic.test_support.listener_via_expectations as lib

        # use_listener = lib.for_DEBUGGING (works)
        use_listener = lib.listener_via_emission_receiver(emissions.append)

        _eek = _subject_module().open_dictionary_stream(
                html_document_path=fixture_file_path('0120-real-subtree.html'),
                listener=use_listener,
                )

        def store_previous():
            nonlocal store_previous
            store_previous = store_previous_normally

        def store_previous_normally():
            sections.append(section)

        class _Section:
            def __init__(self, s):
                self.item_strings = []
                self.header_content = s

        with _eek as json_objs:
            json_obj = next(json_objs)
            json_obj['_is_sync_meta_data']  # assert
            for json_obj in json_objs:
                if 'header_level' in json_obj:
                    store_previous()
                    section = _Section(json_obj['header_content'])
                else:
                    section.item_strings.append(json_obj['lesson'])

        store_previous_normally()

        class _State:
            def __init__(self, em_tup, sect_tup):
                self.emissions = em_tup
                self.sections = sect_tup

        return _State(tuple(emissions), tuple(sections))


@memoize
def _subject_module():
        import script.khong.json_stream_via_website as x
        return x


if __name__ == '__main__':
    unittest.main()

# #born.
