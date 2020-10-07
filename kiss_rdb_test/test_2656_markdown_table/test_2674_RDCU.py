from kiss_rdb_test import storage_adapter_canon
from modality_agnostic.test_support.common import \
        dangerous_memoize as shared_subject
import unittest
import re


canon = storage_adapter_canon.produce_agent()


class CommonCase(unittest.TestCase):

    def reason(self):  # must be used with _flush_reason_early
        return self.end_state['reason']

    def build_file_patch(self):
        lines = self.end_state['diff_lines']
        from text_lib.diff_and_patch import \
            file_patches_via_unified_diff_lines as func
        file_patch, = tuple(func(lines))
        return file_patch

    def build_end_state_complicatedly(self):
        es = self.canon_case.build_end_state(self)  # #here1
        self.check_open_file_num_times()
        return self.include_diff_lines_in_end_state(es)

    def include_diff_lines_in_end_state(self, es):
        es['diff_lines'] = self.omg_diff_lines
        return es

    def mutable_collection(tc, pfile, num_times_read_file=1):
        # Hack the collection so it's mutli-shot, and add assertion of how
        # many times the file was traversed alond with a MASSIVE HACK to
        # get diff lines back from the collection.

        def opn(path):
            assert pfile.path == path
            return stack.pop()

        if 1 == num_times_read_file:
            stack = [pfile]
        else:
            pfiler = pretend_filer_via_pfile(pfile)
            stack = [pfiler() for _ in range(0, num_times_read_file)]

        def recv_diff_lines(diff_lines):
            tc.omg_diff_lines = tuple(diff_lines)
            return True  # important: tell it u succeeded in applying the patch

        opn.RECEIVE_DIFF_LINES = recv_diff_lines
        tc.omg_diff_lines = None

        if 1 < num_times_read_file:
            def check_open_file_num_times():
                tc.assertEqual(len(stack), 0)
            tc.check_open_file_num_times = check_open_file_num_times

        return msa().collection_implementation_via(pfile.path, opn=opn)

    def identifier_via_primitive(self, eid):
        return subject_module()._identifier(eid)

    do_debug = False


class Case2606_entity_not_found_because_identifier_too_deep(CommonCase):

    def test_100_result_is_none(self):
        self.canon_case.confirm_result_is_none(self)

    def test_200_emitted_accordingly(self):
        # at #history-B.1 this changed because freeform identifiers now
        # so there is no longer a complaint about identifier depth

        actual = self.end_state['payloader']()['reason']
        self.assertIn("'AB23' not found", actual)

    @shared_subject
    def end_state(self):
        return self.canon_case.build_end_state(self)

    def given_collection(self):
        return collection_one_shot(pretend_file_empty())

    def given_identifier_string(self):
        return 'AB23'

    @property
    def canon_case(self):
        return canon.case_of_entity_not_found_because_identifier_too_deep


class Case2609_entity_not_found(CommonCase):

    def test_100_result_is_none(self):
        self.canon_case.confirm_result_is_none(self)

    def test_200_emitted_accordingly(self):
        self.canon_case.confirm_emitted_accordingly(self)

    @shared_subject
    def end_state(self):
        return self.canon_case.build_end_state(self)

    def given_identifier_string(self):
        return 'AB2'

    def given_collection(self):
        return collection_one_shot_ordinary()

    @property
    def canon_case(self):
        return canon.case_of_entity_not_found


class Case2612_retrieve_OK(CommonCase):

    def test_100_the_entity_is_retrieved_and_looks_OK(self):
        self.canon_case.confirm_entity_is_retrieved_and_looks_ok(self)

    @shared_subject
    def end_state(self):
        return self.canon_case.build_end_state(self)

    def given_identifier_string(self):
        return 'B9H'

    def given_collection(self):
        return collection_one_shot_ordinary()

    @property
    def canon_case(self):
        return canon.case_of_retrieve_OK


class Case2641_delete_but_entity_not_found(CommonCase):

    def test_100_result_is_none(self):
        self.canon_case.confirm_result_is_none(self)

    def test_200_emitted_accordingly(self):
        self.canon_case.confirm_emitted_accordingly(self)

    @shared_subject
    def end_state(self):
        return self.canon_case.build_end_state(self)

    def given_collection(self):
        return collection_one_shot_ordinary()

    def given_identifier_string(self):
        return 'AB2'

    @property
    def canon_case(self):
        return canon.case_of_delete_but_entity_not_found


class Case2644_delete_OK_resulting_in_non_empty_collection(CommonCase):

    def test_100_result_is_the_deleted_entity(self):
        self.canon_case.confirm_result_is_the_deleted_entity(self)

    def test_200_emitted_accordingly(self):
        self.canon_case.confirm_emitted_accordingly(self)

    def test_300_now_collection_doesnt_have_that_entity(self):
        # self.canon_case.confirm_entity_no_longer_in_collection(self)
        fp = self.build_file_patch()  # one file patch
        hunk, = fp.hunks  # with one hunk
        run, = hunk.to_remove_lines_runs()  # with one run of removed lines
        line, = run.lines  # with one line
        self.assertEqual(line, "-|  B9H ||   | hi i'm B9H |  hey i'm B9H\n")

    def CONFIRM_THIS_LOOKS_LIKE_THE_DELETED_ENTITY(self, ent):
        dct = canon.yes_value_dictionary_of(ent)
        self.assertEqual(dct['thing_A'], "hi i'm B9H")
        self.assertEqual(dct['thing_B'], "hey i'm B9H")
        self.assertEqual(len(dct), 2)

    @shared_subject
    def end_state(self):
        es = self.canon_case.build_end_state_for_delete(self, 'B9H')
        return self.include_diff_lines_in_end_state(es)

    def given_collection(self):
        return self.mutable_collection(pretend_file_ordinary())

    @property
    def canon_case(self):
        return canon.case_of_delete_OK_resulting_in_non_empty_collection


class Case2647_delete_OK_resulting_in_empty_collection(CommonCase):

    def test_100_result_is_the_deleted_entity(self):
        self.canon_case.confirm_result_is_the_deleted_entity(self)

    def test_200_emitted_accordingly(self):
        self.canon_case.confirm_emitted_accordingly(self)

    def test_300_the_collection_is_empty_afterwards(self):
        # self.canon_case.confirm_the_collection_is_empty(self)
        fp = self.build_file_patch()  # one file patch
        hunk, = fp.hunks  # with one hunk
        run, = hunk.to_remove_lines_runs()  # with one run of removed lines
        line, = run.lines  # with one line
        self.assertEqual(line, "-| B9K | xx | | zz |\n")

    def CONFIRM_THIS_LOOKS_LIKE_THE_DELETED_ENTITY(self, ent):
        dct = canon.yes_value_dictionary_of(ent)
        self.assertEqual(dct['thing_1'], 'xx')
        self.assertEqual(dct['thing_A'], 'zz')
        self.assertEqual(len(dct), 2)

    @shared_subject
    def end_state(self):
        es = self.canon_case.build_end_state_for_delete(self, 'B9K')
        return self.include_diff_lines_in_end_state(es)

    def given_collection(self):
        return self.mutable_collection(pretend_file_one_shot_one_entity())

    @property
    def canon_case(self):
        return canon.case_of_delete_OK_resulting_in_empty_collection


class Case2676_create_but_something_is_invalid(CommonCase):

    def test_100_result_is_none(self):
        self.canon_case.confirm_result_is_none(self)

    def test_200_emitted_accordingly(self):
        self.canon_case.confirm_emitted_accordingly(self)

    def CONFIRM_THE_REASON_SAYS_WHAT_IS_WRONG_WITH_IT(self, reason):
        rec, ic = (getattr(re, attr) for attr in ('compile', 'IGNORECASE'))
        rxs = "unrecognized attribute[()s:]* '?thing_C'?"
        self.assertRegex(reason, rec(rxs, ic))
        self.assertRegex(reason, rec(r'\bdid you mean\b', ic))

    def test_600_also_says_table_name(self):
        self.assertIn(' in "table uno"', self.reason())

    def test_620_also_says_path_name(self):
        self.assertIn('n pretend-file/2536-for-ID-traversal.md', self.reason())

    def test_640_also_says_line_number(self):
        self.assertEqual(self.reason()[-12:], 'versal.md:2)')

    @shared_subject
    def end_state(self):
        return _flush_reason_early(self.canon_case.build_end_state(self))

    def dictionary_for_create_with_something_invalid_about_it(self):
        return {'i_de_n_ti_fier_zz': 'B9I',
                'thing_1': '123.45',  # was other primitives B4 #history-B.1
                'thing_A': 'True',
                'thing_C': 'false'}

    def given_collection(self):
        return collection_one_shot_ordinary()

    @property
    def canon_case(self):
        return canon.case_of_create_but_something_is_invalid


class Case2679_create_OK_into_empty_collection(CommonCase):

    def test_100_result_is_created_entity(self):
        self.canon_case.confirm_result_is_the_created_entity(self)

    def test_200_emitted_accordingly(self):
        self.canon_case.confirm_emitted_accordingly(self)

    def test_300_now_collection_doesnt_have_that_entity(self):
        # self.canon_case.confirm_entity_now_in_collection(self)
        fp = self.build_file_patch()  # one file patch
        hunk, = fp.hunks  # with one hunk
        run, = hunk.to_add_lines_runs()  # with one run of added lines
        line, = run.lines  # with one line
        self.assertEqual(line, '+| 123 ||3.14||\n')

    @shared_subject
    def end_state(self):
        return self.build_end_state_complicatedly()

    def given_collection(self):
        return self.mutable_collection(pretend_file_empty(), 2)

    @property
    def canon_case(self):
        return canon.case_of_create_OK_into_empty_collection


class Case2682_create_OK_into_non_empty_collection(CommonCase):

    def test_100_result_is_created_entity(self):
        self.canon_case.confirm_result_is_the_created_entity(self)

    def test_200_emitted_accordingly(self):
        self.canon_case.confirm_emitted_accordingly(self)

    def test_300_now_collection_doesnt_have_that_entity(self):
        # self.canon_case.confirm_entity_now_in_collection(self)
        fp = self.build_file_patch()  # one file patch

        lines = tuple(s for hunk in fp.hunks for run in hunk.runs for s in run.lines)  # noqa: E501
        lines = lines[-3:]
        expect = (
            " | -2.717 | x2\n",
            "+|-2.718||false||\n",
            " | -2.719 | x4\n")
        self.assertSequenceEqual(lines, expect)

    @shared_subject
    def end_state(self):
        es = self.canon_case.build_end_state(self)
        # self.check_open_file_num_times()
        return self.include_diff_lines_in_end_state(es)

    def given_collection(self):
        return self.mutable_collection(pretend_file_one_shot_ordinary_take_2())

    @property
    def canon_case(self):
        return canon.case_of_create_OK_into_non_empty_collection


class Case2710_update_but_entity_not_found(CommonCase):

    def test_100_result_is_none(self):
        self.canon_case.confirm_result_is_none(self)

    def test_200_emitted_accordingly(self):
        self.canon_case.confirm_emitted_accordingly(self)

    def test_600_reason_contains_number_of_lines(self):
        self.assertIn('(saw 3 entities)', self.reason())

    @shared_subject
    def end_state(self):
        return _flush_reason_early(self.canon_case.build_end_state(self))

    def request_tuple_for_update_that_will_fail_because_no_ent(self):
        return 'NSE', (('update_attribute', 'thing_1', 'no see'),)

    def given_collection(self):
        return collection_one_shot_ordinary()

    @property
    def canon_case(self):
        return canon.case_of_update_but_entity_not_found


class Case2713_update_but_attribute_not_found(CommonCase):

    def test_100_result_is_none(self):
        self.canon_case.confirm_result_is_none(self)

    def test_200_emitted_accordingly(self):
        self.canon_case.confirm_emitted_accordingly(self)

    @shared_subject
    def end_state(self):
        return self.canon_case.build_end_state(self)

    def request_tuple_for_update_that_will_fail_because_attr(self):
        return 'B9H', (('update_attribute', 'thing_1', 'no see'),)

    def given_collection(self):
        return collection_one_shot_ordinary()

    @property
    def canon_case(self):
        return canon.case_of_update_but_attribute_not_found


# == HERE

class Case2716_update_OK(CommonCase):

    def test_100_result_is_a_two_tuple_of_before_and_after_entities(self):
        self.canon_case.confirm_result_is_before_and_after_entities(self)

    def test_200_the_before_entity_has_the_before_values(self):
        self.canon_case.confirm_the_before_entity_has_the_before_values(self)

    def test_300_the_after_entity_has_the_after_values(self):
        self.canon_case.confirm_the_after_entity_has_the_after_values(self)

    def test_400_emitted_accordingly(self):
        self.canon_case.confirm_emitted_accordingly(self)

    def test_500_retrieve_afterwards_shows_updated_value(self):
        # self.canon_case.confirm_retrieve_after_shows_updated_value(self)
        # don't assert the line contents because too granular (see next tests)
        self.my_custom_index

    """
    given:

        | i De nTi Fier zz | thing 1  | thing-2 | Thing_A |thing-B|    hi-G|
        |  B9H ||   | hi i'm B9H | hey i'm B9H

    and:    'B9H', (
        ('delete_attribute', 'thing-A'),
        ('update_attribute', 'thing-B', "I'm modified \"thing-B\""),
        ('create_attribute', 'thing-2', "I'm created \"thing-2\""))

    expect these:
      - identifier cel is exactly unchanged (that extra space)
      - thing-1 unchanged (zero width)
      - thing-2 gets created and does *not* inherit those 3 spaces of pad
      - thing-A ("hi i'm..") gets deleted, new cel is zero width
      - thing-B  DOES OR DOES NOT inherit the leading padding
      - the final cel ("hi-G") gets added because it's in the example row
      - still no trailng pipe
    """

    def test_531_padding_of_ID_cel_surface_is_unchanged(self):
        s = self.cell_at(0)
        self.assertEqual(s, '  B9H ')

    def test_594_field_one_is_still_zero_width(self):
        s = self.cell_at(1)
        self.assertEqual(s, '')

    def test_656_field_two_is_created_and_clobbers_the_weird_padding(self):
        s = self.cell_at(2)
        self.assertEqual(s, ' I\'m created "thing_2" ')

    def test_719_deleted_cel_is_now_zero_width(self):
        s = self.cell_at(3)
        self.assertEqual(s, '')

    def test_781_updating_DOES_inherit_the_leading_padding(self):
        s = self.cell_at(4)
        exp = '  I\'m modified "thing_B"'
        self.assertEqual(s.index(exp), 0)

    def test_844_had_endcap_before_so_endcap_after(self):
        line = self.my_custom_index['the_whole_line']
        assert -1 != line.rfind('modified "thing_B"|\n')

    def test_906_that_final_cel_still_isnt_present(self):
        line = self.my_custom_index['the_whole_line']
        import functools
        _count_me = re.findall(r'\|', line)
        _num = functools.reduce(lambda m, x: m + 1, _count_me, 0)
        self.assertEqual(_num, 6)

    def test_969_no_trailing_whitespace_because_no_trailing_pipe(self):
        s = self.cell_at(4)
        exp = 'I\'m modified "thing_B"'
        act = s[-len(exp):]
        self.assertEqual(act, exp)

    def cell_at(self, i):
        return self.my_custom_index['cels'][i]

    @shared_subject
    def my_custom_index(self):

        # == at #history-B.1 change from reading cached lines to reading diff
        fp = self.build_file_patch()  # one file patch
        hunk, = fp.hunks  # one hunk
        _, _, run, _ = hunk.runs  # four runs
        line, = run.lines  # one line on this one
        assert '+' == line[0]
        line = line[1:]
        # ==

        md = re.match(r'^\|((?:[^|\n]*\|){4}[^|\n]*)', line)

        """With this much we are comfortable asserting here in the set-up:
        assert the existence of but do not capture the leading pipe,
        then four times of zero-or-more-not-pipes-then-a-pipe,
        and then as many non-pipes as you can after it. This isolates the
        parts of the production we are sure about from the parts we test.
        """

        cels = md[1].split('|')
        assert(5 == len(cels))

        return {'the_whole_line': line, 'cels': cels}

    @shared_subject
    def end_state(self):
        es = self.canon_case.build_end_state(self)
        return self.include_diff_lines_in_end_state(es)

    def request_tuple_for_update_that_will_succeed(self):
        return 'B9H', (
            ('delete_attribute', 'thing_A'),
            ('update_attribute', 'thing_B', "I'm modified \"thing_B\""),
            ('create_attribute', 'thing_2', "I'm created \"thing_2\""))

    def given_identifier_string(self):
        return 'B9H'

    def given_collection(self):
        return self.mutable_collection(pretend_file_ordinary())

    @property
    def canon_case(self):
        return canon.case_of_update_OK


# == Test Assertion Support

def _flush_reason_early(es):
    sct = es['payloader']()  # see in storage_adapter_canon
    es['payloader'] = lambda: sct
    es['reason'] = sct['reason']
    return es


# == Pretend Files & Fixture Collections (decorators & not interm.) Support

def collection_one_shot(pretend_file):

    def opn(path):
        assert pretend_file.path == path
        return pretend_file

    return msa().collection_implementation_via(pretend_file.path, opn=opn)


def reusable_pretend_filer(pretend_file_one_shot):
    def use_f():
        if use_f.is_first_call:
            use_f.is_first_call = False
            use_f.call = pretend_filer_via_pfile(pretend_file_one_shot())
        return use_f.call()
    use_f.is_first_call = True
    return use_f


def pretend_filer_via_pfile(o):
    def call():
        return cls(path=path, lines=lines)
    cls, path, lines = o.__class__, o.path, tuple(o.release_lines__())
    return call


def _build_pretend_file_one_shot_decorator():
    # Assert explicitly that you only access the pretend file once.  #here2

    def decorator(orig_f):  # #decorator
        def use_f():
            assert use_f.is_first_call
            use_f.is_first_call = False
            return build(orig_f)
        use_f.is_first_call = True
        return use_f

    def build(orig_f):
        path, big_string = normalize_args(** {k: v for k, v in orig_f()})
        return msa().pretend_file_via_path_and_big_string(path, big_string)

    def normalize_args(pretend_path, big_string):
        return pretend_path, big_string

    return decorator


pretend_file_one_shot = _build_pretend_file_one_shot_decorator()


# == Fixtures

# -- "Ordinary" Collection

def collection_one_shot_ordinary():
    return collection_one_shot(pretend_file_ordinary())


@pretend_file_one_shot
def pretend_file_one_shot_ordinary():
    # making this line up with the legacy collection perfectly is tricky
    # because in non-tabular formats, adding an arbitrary field to an
    # arbitrary entity is cheap and easy, but tables are .. tabular. SO:
    # here we have added *one* of the ad-hoc fields to test a thing
    # (to get more num_fields than num_original_cels)

    yield 'pretend_path', 'pretend-file/2536-for-ID-traversal.md'
    yield 'big_string', (
        """
        # table uno
        | i De nTi Fier zz | thing 1  | thing-2 | Thing_A |thing-B|    hi-G|
        |---|---|---|---|---|---|
        | HMM |  x | x |x|  x| x
        | B9G
        |  B9H ||   | hi i'm B9H |  hey i'm B9H
        | B9K
        """)
    # 👉 these three 'B9G', 'B9H', 'B9K' must be as if (12, 13, 15)
    # 👉 leave this identifier out: 'NSE' (for No Such Entity)


pretend_file_ordinary = reusable_pretend_filer(pretend_file_one_shot_ordinary)


@pretend_file_one_shot
def pretend_file_one_shot_ordinary_take_2():
    # new at #history-B.1 writing, identifier must be in argument dict

    yield 'pretend_path', 'pretend-file/2682-for-create.md'
    yield 'big_string', (
        """
        # table uno
        | thing 2 | foo fa | thing B | zoo zah |
        |---|---|---|---|
        |||||
        | -2.717 | x2
        | -2.719 | x4
        """)


@pretend_file_one_shot
def pretend_file_one_shot_one_entity():
    yield 'pretend_path', 'pretend-file/XXXX-one-entity.md'
    yield 'big_string', (
        """
        | i De nTi Fier zz | thing 1  | thing-2 | Thing_A |thing-B|
        |---|---|---|---|---|
        | EG |||||
        | B9K | xx | | zz |
        """)


@pretend_file_one_shot
def pretend_file_one_shot_empty():
    yield 'pretend_path', 'pretend-file/XXXX-empty-collection.md'
    yield 'big_string', (
        # leftmost field must be in the argument dict or error not under test
        """
        | thing-2 | Thing_A |thing-B| not me |
        |---|---|---|---|
        """)


pretend_file_empty = reusable_pretend_filer(pretend_file_one_shot_empty)


# == Support

def msa():
    import kiss_rdb_test.markdown_storage_adapter as msa
    return msa


def subject_module():
    import kiss_rdb.storage_adapters_.markdown_table as module
    return module


def xx(msg=None):
    raise RuntimeError('write me' + ('' if msg is None else f": {msg}"))


""":#here2:
In asserting the main collection story under test, the canon may also apply
additional, auxiliary operations to assert the before state or after state
of the story, in order to assert the expected change the story is supposed to
effect. This happens in at least one canon story and probably more.

For example, the overall purpose of #here1 is to assert that we can create
in to an empty collection. To assert this story, the canon first checks that
the collection starts out with zero items. It does this by traversing the
collection. This sequence of operations presents a challenge because it
violates one of our main rubrics, that our collection object is nominally
[#873.N] single-pass (a.k.a "one-shot") and short- (not long-) running.

We can imagine serveral possible approaches to addressing this challenge,
none of which immediately jump out at us as the best:

- Make canon stories more lax so they don't check collection count in this
  way (i.e., make them "single-pass"-friendly)
- Don't defer to the canon as tightly in stories like these
- Change the collection so it doesn't have a single-pass limitation

For better or worse, as it stands the collection implementation is not strictly
single-pass. It's single-pass per operation, but multiple operations may be
called on a single collection object, because the collection itself is
stateless: it only holds a `path`, a function to `open` the path, and (for
edits) we expose testpoints that produces diff patches, so we only have to test
against generated patches rather than testing against a mutated filesystem.

Now, just because we've decided that multiple-operation "should work" as-is
by collections in production, doesn't mean they will under test. They didn't
at writing because our pretend files themselves have an in-built (implicit)
assertion that the "files" are only traversed (read) once. 2 reasons why:

What we regard as the current best-practice way of representing fixtures in
these stories (for this adapter) is in-file as big-strings: in-file to avoid
the (mental, human) cost of jumping to a real file just to read a few lines,
and big-string rather than lines because it's easier to read and big strings
trivially isomorph with lines here.

Because our design default is always streaming not memory-hog, big strings
are parsed line-by-line on-demand. To support this while being ignorant of it,
pretend files are implemented assuming they are passed an iterator of lines,
which they release by being opened as a context manager (that is, by
implementing `__enter__` and `__exit__`). (In fact, the pretend file doesn't
"know" what its line payload looks like at all. All it does is hold it and
release it.)

But as soon as we want a collection to be able to `open` (and then close) its
`path` multiple times, we can't keep on returning the same pretend path from
`open` over and over, because (as illustrated above) it's stateful and it
exhausts after one traversal.

So, code areas tagged by the tag in our title address this challenge.

This is near [#867.Z] we can't use seek(0) etc on files. just line-by-line
"""


if __name__ == '__main__':
    unittest.main()

# #history-B.1
# #born.
