from kiss_rdb_test.CUD import (
        expect_big_success,
        emission_payload_expecting_error_given_run,
        run_given_edit_tuples,
        request_via_tuples as _request_via_tuples)
from modality_agnostic.test_support.common import \
        dangerous_memoize as shared_subject
import unittest


"""Concerned with processing internal "edit requests" on a single entity

This effort became the now familiar prepare-edit and flush-edit two-step, one
we duplicated blindly and much less code and fanfare in our toy SA.

Although it's tempting to abstract something generic out of this (and
we probably will); there's adapter-specific behavior covered in here,
around the comment policy.

This is close to being canon-relevant, but because it's not integrated with
a collecton façade here, it's not.
"""


class CommonCase(unittest.TestCase):

    def same_because_sho_madjozi_not_found_in_entity(self):
        _actual = self.two_parts[1]
        self.assertEqual(_actual, " because 'sho_madjozi' not found in entity")

    def _same_suggestion_use_this_one_not_that_one(self):
        _actual = self.three_parts[2]
        self.assertEqual(_actual, "use 'SHO_madjozi' not 'sho_madjozi'")

    def _same_because_reason_exact_match(self):
        _actual = self.three_parts[1]
        self.assertEqual(_actual, ' because names must match exactly')

    expect_big_success = expect_big_success

    def expect_request_error_reason(self, reason):
        _actual_reason = self.reason_via_expect_request_error()
        self.assertEqual(_actual_reason, reason)

    def reason_via_expect_cannot_update_error(self):
        return self._reason_via_which('cannot_update')

    def reason_via_expect_request_error(self):
        return self._reason_via_which('request_error')

    def _reason_via_which(self, which):
        sct = emission_payload_expecting_error_given_run(self, which)
        return sct['reason']

    def given_run(self, listener):
        run = run_given_edit_tuples(self)
        return run(listener)

    do_debug = False


class Case4214_when_request_empty(CommonCase):

    def test_100_reason(self):
        self.expect_request_error_reason('request was empty')

    def given_run(self, listener):
        return _request_via_tuples((), listener)


class Case4215_strange_verbs(CommonCase):

    def test_100_reason(self):
        self.expect_request_error_reason(
                'unrecognized verb(s): (fiz, bru-zuz)')

    def given_run(self, listener):
        return _request_via_tuples(
            (('fiz', 'a'), ('delete_attribute', 'x'), ('bru-zuz', 'x')),
            listener)


class Case4216_wrong_looking_attribute_name(CommonCase):

    def test_100_input_error(self):
        sct = emission_payload_expecting_error_given_run(self, 'input_error')
        self.assertEqual(sct['position'], 9)
        self.assertEqual(sct['line'], 'xxe_sesf_')  # ick/meh

    def given_run(self, listener):
        return _request_via_tuples((
            ('create_attribute', 'foo_bar', '1'),
            ('create_attribute', 'xxe_sesf_', '1'),
            ('create_attribute', '^---^', '1'),
            ), listener)


class Case4217_duplicate_names_within_request(CommonCase):

    def test_100_reason(self):
        _actual = self.two_parts[0]
        self.assertTrue(' more than once ' in _actual)

    def test_200_detail(self):
        _actual = self.two_parts[1]
        self.assertEqual(_actual, "'foo_bar' appeared twice")

    @shared_subject
    def two_parts(self):
        _rsn = self.reason_via_expect_request_error()
        return _rsn.split(' and ')

    def given_run(self, listener):
        return _request_via_tuples((
            ('create_attribute', 'foo_bar', '1'),
            ('update_attribute', 'biz_baz', '1'),
            ('delete_attribute', 'foo_bar'),
            ), listener)


class Case4218_names_too_similar_within_request(CommonCase):

    def test_100_reason(self):
        _actual = self.two_parts[1]
        self.assertTrue(' are too similar ' in _actual)

    def test_200_oxford_AND(self):
        _actual = self.two_parts[0]
        self.assertEqual(_actual, "'xx_zz', 'xxz_z' and 'xx_ZZ'")

    @shared_subject
    def two_parts(self):
        _rsn = self.reason_via_expect_request_error()
        return _split_hack(' are ', _rsn)

    def given_run(self, listener):
        return _request_via_tuples((
            ('delete_attribute', 'xx_zz'),
            ('delete_attribute', 'blink_182'),
            ('delete_attribute', 'xxz_z'),
            ('delete_attribute', 'xx_ZZ'),
            ), listener)


class Case4220_cannot_create_when_attributes_already_exist(CommonCase):

    def test_100_reason(self):
        _actual = self._right()
        self.assertTrue(' already exist' in _actual)

    def test_200_items(self):
        _actual = self.two_parts[0]
        _expected = "can't create attribute 'foo_fani'"  # ..
        self.assertEqual(_actual, _expected)

    def test_300_suggestion(self):
        _actual = self._right()
        self.assertTrue(' (use update?)' in _actual)

    def test_400_reason_did_pronoun_and_verb_agreement(self):
        _actual = self._right()
        self.assertTrue(' it already exists ' in _actual)

    def _right(self):
        return self.two_parts[1]

    @shared_subject
    def two_parts(self):
        _rsn = self.reason_via_expect_cannot_update_error()
        return _split_because_hack(_rsn)

    def given_request_tuples(self):
        return (('create_attribute', 'foo_fani', 'x'),)

    def given_entity_body_lines(self):
        return """
        foo_fani = "mum"
        """


class Case4221_cannot_delete_because_attributes_not_found(CommonCase):

    def test_100_reason(self):
        _actual = self.two_parts[0]
        self.assertEqual(_actual, "can't delete")

    def test_200_detail(self):
        self.same_because_sho_madjozi_not_found_in_entity()

    @shared_subject
    def two_parts(self):
        _rsn = self.reason_via_expect_cannot_update_error()
        return _split_because_hack(_rsn)

    def given_request_tuples(self):
        return (('delete_attribute', 'sho_madjozi'),)

    def given_entity_body_lines(self):
        return """
        # comment

        prop_1 = x

        # comment 2
        prop_2 = 123.45
        """


class Case4222_cannot_delete_because_attributes_not_exact_match(CommonCase):  # noqa: E501

    def test_100_content(self):
        _actual = self.three_parts[0]
        self.assertEqual(_actual, "can't delete attributes")

    def test_200_reason(self):
        self._same_because_reason_exact_match()

    def test_300_suggestion(self):
        self._same_suggestion_use_this_one_not_that_one()

    @shared_subject
    def three_parts(self):
        return _same_three_split(self.reason_via_expect_cannot_update_error())

    def given_request_tuples(self):
        return (('delete_attribute', 'sho_madjozi'),)

    def given_entity_body_lines(self):
        return """
        SHO_madjozi = xx
        """


class Case4223_cannot_update_because_attributes_not_found(CommonCase):

    def test_100_result_is_none(self):
        act = self.two_parts[0]
        self.assertEqual(act, "can't update")

    def test_200_emitted_accordingly(self):
        self.same_because_sho_madjozi_not_found_in_entity()

    @shared_subject
    def two_parts(self):
        _rsn = self.reason_via_expect_cannot_update_error()
        return _split_because_hack(_rsn)

    def given_request_tuples(self):
        return (('update_attribute', 'sho_madjozi', 'q'),)

    def given_entity_body_lines(self):
        return """
        aa = bb
        """


class Case4224_cannot_update_because_attributes_not_exact_match(CommonCase):  # noqa: E501

    def test_100_context(self):
        _actual = self.three_parts[0]
        self.assertEqual(_actual, "can't update attributes")

    def test_200_reason(self):
        self._same_because_reason_exact_match()

    def test_300_suggestion(self):
        self._same_suggestion_use_this_one_not_that_one()

    @shared_subject
    def three_parts(self):
        return _same_three_split(self.reason_via_expect_cannot_update_error())

    def given_request_tuples(self):
        return (('update_attribute', 'sho_madjozi', 'q'),)

    def given_entity_body_lines(self):
        return """
        SHO_madjozi = xx
        """


class Case4226_cannot_delete_because_comment_line_above(CommonCase):
    # #midpoint in file

    def test_100_unable_says_verb_and_name_of_attribute(self):
        _actual = self.two_parts[0]
        self.assertEqual(_actual, "cannot delete 'ab_fab' attribute line")

    def test_200_reason_explains_line_above(self):
        _actual = self.two_parts[1]
        self.assertEqual(_actual, 'line touches comment line above')

    @shared_subject
    def two_parts(self):
        return self.reason_via_expect_request_error().split(' because ')

    def given_request_tuples(self):
        return (('delete_attribute', 'ab_fab'),)

    def given_entity_body_lines(self):
        return """
        chab_tab = 123
        # comment line above
        ab_fab = 123
        """


class Case4227_cannot_update_because_comment_line_below(CommonCase):

    def test_100_unable_says_verb_and_name_of_attribute(self):
        _actual = self.two_parts[0]
        self.assertEqual(_actual, "cannot update 'ab_fab' attribute line")

    def test_200_reason_explains_line_below(self):
        _actual = self.two_parts[1]
        self.assertEqual(_actual, 'line touches comment line below')

    @shared_subject
    def two_parts(self):
        return self.reason_via_expect_request_error().split(' because ')

    def given_request_tuples(self):
        return (('update_attribute', 'ab_fab', 'qq'),)

    def given_entity_body_lines(self):
        return """
        chab_tab = 123
        ab_fab = 456
        # comment line below
        """


class Case4228_cannot_update_because_attribute_line_has_comment(CommonCase):  # noqa: E501

    def test_100_unable(self):
        _actual = self.two_parts[0]
        self.assertEqual(_actual, "cannot update 'ab_fab' attribute line")

    def test_200_reason_uses_pronoun_with_antecedent(self):
        _actual = self.two_parts[1]
        self.assertEqual(_actual, 'it has comment')

    @shared_subject
    def two_parts(self):
        return self.reason_via_expect_request_error().split(' because ')

    def given_request_tuples(self):
        return (('update_attribute', 'ab_fab', 'qq'),)

    def given_entity_body_lines(self):
        return """
        ab_fab = 124  # it's 124 because qq
        """


class Case4229_aggregate_multiple_comment_based_failures(CommonCase):

    def test_100_broken_up_into_two_sentences(self):
        self.assertEqual(len(self.two_sentences), 2)

    def test_100_reason(self):
        _actual = self.two_sentences[1]

        _expected = (
            "cannot delete 'ab_fab_2' attribute line "
            "because line touches comment line above and below "
            "and because it has comment")

        self.assertEqual(_actual, _expected)

    @shared_subject
    def two_sentences(self):
        return self.reason_via_expect_request_error().split('. ')

    def given_request_tuples(self):
        return (('delete_attribute', 'ab_fab_1'),
                ('delete_attribute', 'ab_fab_2'))

    def given_entity_body_lines(self):
        return """
        ab_fab_1 = 123
        # comment line causes 2x trouble
        ab_fab_2 = 123  # in-line comment
        # comment line final
        """


class Case4230_cannot_create_because_comment_line_above(CommonCase):

    def test_100_produces_two_sentences(self):
        self.assertIsNotNone(self.two_sentences)

    def test_200_first_sentence_says_first_component_of_first_group(self):
        return self._same(0, 'dd_dd')

    def test_300_second_sentence_says_only_component_of_second_group(self):
        return self._same(1, 'hh_hh')

    def _same(self, sp_i, id_s):
        _expected = (f"cannot create '{id_s}' attribute line because "
                     "line touches comment line above")
        _actual = self.two_sentences[sp_i]
        self.assertEqual(_actual, _expected)

    @shared_subject
    def two_sentences(self):
        _ = self.reason_via_expect_request_error()
        sp1, sp2 = _.split('. ')
        return (sp1, sp2)

    def given_request_tuples(self):
        return (('create_attribute', 'dd_dd', '123'),
                ('create_attribute', 'ee_ee', '123'),
                ('create_attribute', 'hh_hh', '123'))

    def given_entity_body_lines(self):
        # perhaps just visually:
        # 1) make sure both "comment M-C" get swepped up in the excerpt
        # 2) see how a bundle can be made with two
        # 3) see how a possible insertion point is passed over (ff-ff/gg-gg)
        return """
        aa_aa = 123
        bb_bb = 123
        mm_mm = 123
        # comment M-C one
        # comment M-C two
        cc_cc = 123
        # comment C-F
        ff_ff = 123
        gg_gg = 123
        # comment F-I
        ii_ii = 123
        """


class Case4232_can_update_idk(CommonCase):

    # this almost touches #multi-line

    def test_100_something(self):
        self.expect_big_success()

    def expect_entity_body_lines(self):
        return """
        thing_1 = 123
        thing_2 = 789
        """

    def given_request_tuples(self):
        return (('update_attribute', 'thing_2', 789),)

    def given_entity_body_lines(self):
        return """
        thing_1 = 123
        thing_2 = 456
        """


class Case4233_can_delete(CommonCase):

    def test_100_something(self):
        self.expect_big_success()

    def expect_entity_body_lines(self):
        return """
        thing_1 = 123
        # comment

        """

    def given_request_tuples(self):
        return (('delete_attribute', 'thing_2'),)

    def given_entity_body_lines(self):
        return """
        thing_1 = 123
        # comment

        thing_2 = 456
        """


class Case4234_can_create_when_comment_line_at_tail(CommonCase):

    # this tests for #multi-line but is not

    def test_100_everything(self):
        self.expect_big_success()

    def expect_entity_body_lines(self):
        return """
        aa_aa = 123
        bb_bb = 123
        mm_mm = 123
        # comment M-C one
        # comment M-C two
        cc_cc = 123
        dd_dd = 123
        ee_ee = "123"
        ff_ff = 123
        gg_gg = 123
        # comment at end of things

        hh_hh = 123.0
        """

    def given_request_tuples(self):
        return (('create_attribute', 'dd_dd', 123),
                ('create_attribute', 'ee_ee', '123'),
                ('create_attribute', 'hh_hh', 123.0))

    def given_entity_body_lines(self):
        return """
        aa_aa = 123
        bb_bb = 123
        mm_mm = 123
        # comment M-C one
        # comment M-C two
        cc_cc = 123
        ff_ff = 123
        gg_gg = 123
        # comment at end of things
        """


class Case4235_can_create_when_comment_line_at_head_of_excerpt(CommonCase):

    def test_100_everything(self):
        self.expect_big_success()

    def expect_entity_body_lines(self):
        return """
        bb_bb = 123
        cc_cc = 123

        # head comment 1
        # head comment 2
        dd_dd = 123
        ee_ee = 123
        ff_ff = 123
        """

    def given_request_tuples(self):
        return (('create_attribute', 'bb_bb', 123),
                ('create_attribute', 'cc_cc', 123))

    def given_entity_body_lines(self):
        return """
        # head comment 1
        # head comment 2
        dd_dd = 123
        ee_ee = 123
        ff_ff = 123
        """


class Case4236_create_into_truly_empty(CommonCase):

    def test_100_note_it_gets_ordered(self):
        self.expect_big_success()

    def expect_entity_body_lines(self):
        return """
        bb_bb = 123
        cc_cc = 456
        """

    def given_request_tuples(self):
        return (('create_attribute', 'cc_cc', 456),
                ('create_attribute', 'bb_bb', 123))

    def given_entity_body_lines(self):
        return """
        """


class Case4238_create_into_empty_with_comments(CommonCase):

    def test_100_note_it_gets_ordered(self):
        self.expect_big_success()

    def expect_entity_body_lines(self):
        return """
        # comment 1
        # comment 2

        bb_bb = 123
        cc_cc = 456
        """

    def given_request_tuples(self):
        return (('create_attribute', 'cc_cc', 456),
                ('create_attribute', 'bb_bb', 123))

    def given_entity_body_lines(self):
        return """
        # comment 1
        # comment 2
        """


def _same_three_split(reason):
    left, rest = _split_because_hack(reason)
    mid, right = rest.split('. ')
    return (left, mid, right)


def _split_because_hack(reason):
    return _split_hack(' because ', reason)


def _split_hack(sep, reason):
    left, right = reason.split(sep)
    return (left, f'{ sep }{ right }')  # ick/meh


# ==

def _subject_module():
    from kiss_rdb.storage_adapters_.toml import CUD_attributes_via_request as _
    return _


if __name__ == '__main__':
    unittest.main()


# #history-A.1: begin small changes for big overhaul for multi-line strings
# #born.
