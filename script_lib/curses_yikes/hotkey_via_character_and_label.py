from script_lib.curses_yikes import MultiPurposeResponse_ as _change_response
from collections import namedtuple as _nt
import re


# inter_aa_dct = interactive abstract area dictionary


def experimental_deferential_button_AAer_(k, inter_aa_dct, more=None):
    # When first developed, button areas were defined "by hand". In production
    # we expect to mostly (if not always) autogenerate the pages of buttons
    # with the complicated algo. So, this function tries to "look like" an
    # abstract area class ("klass") to the extent that it needs to to sneak in,
    # but then calls the simpler, actual AA class.

    pi = _pages_index(inter_aa_dct)

    def buttons_definition():
        for page_name, page_content in pi.to_pages():
            yield 'page_of_buttons', page_name, defserer(page_content)

        # == BEGIN experiment
        #    (this will be an ongoing area of exploration, how to straddle
        #    the boundary between auto and manual, & let both coexist)
        seen_static = False
        if more:
            for tup in more:
                if 'static_buttons_area' == tup[0]:
                    seen_static = True
                yield tup
        if seen_static:
            return
        # == END

        yield 'static_buttons_area', lambda: (('[q]uit',),)

    def defserer(page_content):
        return lambda: (page_content,)  # it expects several rows

    return _abstract_hotkeys_area_via(buttons_definition(), pi)


_ = experimental_deferential_button_AAer_
KLASS = _
_.is_interactable = False  # hard to explain
_.defer_until_after_interactables_are_indexed = True


class _pages_index:

    def __init__(self, inter_aa_dct):
        for k, dct in _build_button_pages_index(inter_aa_dct):
            setattr(self, k, dct)

    def to_pages(self):
        return self.page_contents_via_page_key.items()


def _build_button_pages_index(inter_aa_dct):
    # Build the button pages index. Exactly [#608.2.B], the most complicated
    # algortihm here. This was rewritten blind 12 days later to better
    # isolate the use of FSA's from this module. All this is only used #here1

    page_key_via_component_page_key_via_component_type_key = {}
    page_contents_via_page_key = {}
    page_key_via_page_contents = {}
    component_type_key_via_component_key = {}
    seen_component_types = set()
    fields = tuple((locs := locals()).keys())[1:]  # skip the func arg YIKES

    for component_k, aa in inter_aa_dct.items():
        ctk = aa.component_type_key
        component_type_key_via_component_key[component_k] = ctk

        # Assume that every AA of the same component type has the same etc
        if ctk in seen_component_types:
            continue
        seen_component_types.add(ctk)

        page_key_via_component_page_key = {}  # this is all for one comp. type
        for component_page_k, labels in aa.to_button_pages():

            labels = tuple(labels)

            # The comp should explicitly tell us about no-button pages [#607.C]
            if 0 == len(labels):
                page_key_via_component_page_key[component_page_k] = None
                continue

            # Create a new page for thi list of labels IFF we didn't already
            if (page_k := page_key_via_page_contents.get(labels)) is None:
                number = len(page_key_via_page_contents) + 1
                page_k = f"buttons_page_{number}"
                page_key_via_page_contents[labels] = page_k
                page_contents_via_page_key[page_k] = labels

            page_key_via_component_page_key[component_page_k] = page_k

        page_key_via_component_page_key_via_component_type_key[ctk] = \
            page_key_via_component_page_key

    for k in fields:
        yield k, locs[k]


def _abstract_hotkeys_area_via(directives, pi=None):
    # #testpoint

    pages = {}
    static_page = None
    hotkeys_cache = _MutableHotkeysCache()

    scn = _scanner_via_iterator(directives)
    is_in_dynamic_section = True

    while True:
        # Resolve the directive type, looking for a mode change
        x = scn.next()  # advance early because we have to peek to end
        assert isinstance(x, tuple)
        direc_stack = list(reversed(x))
        typ = direc_stack.pop()  # let's just consume early for now

        assert is_in_dynamic_section

        if 'page_of_buttons' != typ:
            if 'static_buttons_area' != typ:
                xx(f"strange directive: '{typ}'")
            if scn.more:
                typ_ = scn.peek[0]
                xx(f"expecting no other directives after etc (had '{typ_}')")
            is_in_dynamic_section = False

        if is_in_dynamic_section:
            page_key = direc_stack.pop()
            assert isinstance(page_key, str)
            if page_key in pages:
                xx("page name collision")
        else:
            page_key = None

        # Build the page and add it to the pages, given the button labels
        button_defser, = direc_stack
        del direc_stack

        if is_in_dynamic_section:
            f = hotkeys_cache.offset_of_lazily_created_hotkey
        else:
            f = hotkeys_cache.STATIC_BUTTONS_THING

        labels = (s for row in button_defser() for s in row)  # #jumble
        button_offsets = tuple(f(label) for label in labels)
        page = _Page(page_key, button_offsets)

        if is_in_dynamic_section:
            pages[page_key] = page  # NOTE key can be None by this is a hack!
        else:
            static_page = page

        if scn.empty:
            break

    # (the only difference between a hotkeys index and a mutable hotkeys cache
    # is one property being a tuple versus a list; so for now we hack it)
    hotkeys_index = hotkeys_cache
    hotkeys_index.hotkeys = tuple(hotkeys_index.hotkeys)
    return _AbstractHotkeysArea(
        static_page, pages, hotkeys_index, pi)


class _AbstractHotkeysArea:

    def __init__(self, static_page, pages, hotkeys_index, pi):

        self._static_page = static_page
        self._dynamic_pages = pages
        self._hotkeys_index = hotkeys_index
        self._pages_index = pi

        self._wrap_plan_cache = {}

    def concretize_via_available_height_and_width(self, h, w, listener=None):
        # we make several leaps of faith meh
        tot, dyn_max_h, wrap_plans, static_wp = self._wrap_plan_cache[w]
        assert h == tot  # meh
        return _ConcreteHotkeysArea(
            h=h, w=w, dyn_max_h=dyn_max_h,
            wrap_plans=wrap_plans, static_wrap_plan=static_wp,
            pages=self._dynamic_pages, static_page=self._static_page,
            hotkeys_index=self._hotkeys_index,
            pages_index=self._pages_index)

    def minimum_height_via_width(self, w):
        cache = self._wrap_plan_cache
        if (tup := cache.get(w)) is None:
            # in production this wouldn't happen unless we had the mythic
            # #live-resize. but some test units have multiple tests such that
            # this cache gets used
            tup = _BEASTMODE(
                w, self._static_page, self._dynamic_pages, self._hotkeys_index)
            cache[w] = tup
        total_max_h, max_height_of_etc, wrap_plans, static_wp = tup
        return total_max_h

    @property
    def minimum_width(self):
        # Our wordwrap breaks up "long" lines but it won't break up a "word",
        # so the narrowest a button area can be squeezed is the width of its
        # widest button (& squeezing it this way could make it get quite tall)

        return self._hotkeys_index.width_of_widest_hotkey_label

    def hello_I_am_AHA(self):
        return True

    two_pass_run_behavior = 'break'
    can_fill_vertically = False  # button areas push (not fill) verticality


class _ConcreteHotkeysArea:

    def __init__(
            self, h, w, dyn_max_h, wrap_plans, static_wrap_plan,
            pages, static_page, hotkeys_index,
            pages_index=None):

        self._height = h
        self._max_height_of_dynamic_area = dyn_max_h
        self._height_of_static_area = h - dyn_max_h
        self._wrap_plans = wrap_plans
        self._static_wrap_plan = static_wrap_plan
        self._dynamic_pages = pages
        self._static_page = static_page
        self._hotkeys_index = hotkeys_index
        self._pages_index = pages_index

        self._center = _centerer(w)
        self._currently_selected_page_key = None
        self._blank_row = ' ' * w

    # == Receive change

    # cbpk = component button page key
    def apply_change_focus(self, k_, cbpk):

        page_k = self._page_key_for_component(k_, cbpk)
        if self._currently_selected_page_key == page_k:
            return _change_response()  # _do_nothing

        # Now, buttons area is guaranteed to change

        if page_k is None:
            self._set_active_page_to_none()
        else:
            self._set_active_page(page_k)

        # [#608.2.C] we don't get real name for now, just magic name 'buttons'
        return _change_response(changed_visually=('buttons',))

    def _page_key_for_component(self, k_, cbpk):  # :#here1

        # If the patch says "focus changed to NO focus (anywhere)", then
        # change the dynamic buttons area to have no buttons (if necessary)
        if k_ is None:
            assert not cbpk
            return None

        # Get from the currently focused component (key, state) to the page key

        pi = self._pages_index

        ctk = pi.component_type_key_via_component_key[k_]

        page_key_via_component_page_key = \
            pi.page_key_via_component_page_key_via_component_type_key[ctk]

        return page_key_via_component_page_key[cbpk]  # use provision [#607.C]

    # ==

    def _set_active_page(self, k):  # #testpoint
        self._dynamic_pages[k]  # validate argument
        self._wrap_plans[k]  # sanity
        self._currently_selected_page_key = k

    def _set_active_page_to_none(self):  # #testpoint
        self._currently_selected_page_key = None

    # ==

    def to_rows(self):

        def rows_via_wrap_plan(wrap_grid, words_tuple):
            # For each button row (wordwrapped, dynamic or static), render it
            # (one day if buttons get dynamic etc but for now, etc)

            for word_offsets_for_row in wrap_grid:
                labels = (words_tuple[i] for i in word_offsets_for_row)
                yield center(' '.join(labels))

        center = self._center

        # If "the none page" is selected, draw all blank lines for the dyn area
        k = self._currently_selected_page_key
        if k is None:
            for _ in range(0, self._max_height_of_dynamic_area):
                yield self._blank_row
        else:
            # Draw blank lines for the zero or more .. blank .. lines (gravity)
            wrap_plan = self._wrap_plans[k]
            this_many = len(wrap_plan.wrap_grid)
            num_blank_lines = self._max_height_of_dynamic_area - this_many
            for _ in range(0, num_blank_lines):
                yield self._blank_row

            for row in rows_via_wrap_plan(* wrap_plan):
                yield row

        # Rendering statics is like rendering dynamics except no blank lines
        if self._static_page:
            for row in rows_via_wrap_plan(* self._static_wrap_plan):
                yield row

    # ==

    def type_and_label_of_button_via_keycode__(self, keycode):
        # imagine if buttons also had transition names in them, separate
        # from labels. But maybe the FFSA's read more tightly this way..

        def via_page(page):
            for btn in (hotkeys[i] for i in page.button_offsets):
                if fig_key == btn.figurative_key:
                    return btn.label

        fig_key = self._figurative_key_via_keycode(keycode)
        hotkeys = self._hotkeys_index.hotkeys

        if (p := self._dynamic_page) and (x := via_page(p)):
            return 'dynamic', x

        if (p := self._static_page) and (x := via_page(p)):
            return 'static', x

    def _figurative_key_via_keycode(self, keycode):
        if re.match(r'[a-z]\Z', keycode):
            return keycode
        if '\n' == keycode:
            return 'enter'
        xx(f"how to translate this keycode to fig key: {keycode!r}")

    @property
    def _dynamic_page(self):
        if (k := self._currently_selected_page_key):
            return self._dynamic_pages[k]

    def hello_I_am_CHA(_):
        return True

    to_form_value = None
    is_focusable = False


def _centerer(w):
    def center(content):
        content_w = len(content)
        extra_space = w - content_w
        assert 0 <= extra_space
        half, zero_or_one = divmod(extra_space, 2)
        left_padding = ' ' * half
        right_padding = ' ' * (half + zero_or_one)  # center with left rising
        return ''.join((left_padding, content, right_padding))
    return center


def _BEASTMODE(w, static_page, pages, hotkeys_index):

    # This is the central crazy of the whole project so far: You have multiple
    # pages of buttons for your pseudo-dynamic buttons area, and you may have
    # one static buttons area (also a "page"). Given the constraint width,
    # do the word-wrap on each page and determine the highest height of your
    # pseudo-dynamic pages and also (if present) the height of the static area.
    # The sum of these two heights is the required height of your buttons area.

    max_height_of_etc = 0
    wrap_plans = {}

    wrap_plan_via_page = _make_wrap_planner(w, hotkeys_index)
    for k, page in pages.items():
        wp = wrap_plan_via_page(page)
        height = len(wp.wrap_grid)
        if max_height_of_etc < height:
            max_height_of_etc = height
        wrap_plans[k] = wp

    total_max_height = max_height_of_etc
    static_wp = None
    if static_page:
        static_wp = wrap_plan_via_page(static_page)
        total_max_height += len(static_wp.wrap_grid)

    return total_max_height, max_height_of_etc, wrap_plans, static_wp


def _make_wrap_planner(w, hotkeys_index):
    def wrap_plan_via_page(page):
        words_tuple = tuple(hotkeys[i].label for i in page.button_offsets)
        itr = word_wrap(w, words_tuple)
        wrap_grid = tuple(itr)
        return _WrapPlan(wrap_grid, words_tuple)

    from script_lib.curses_yikes.text_lib_ import \
        quick_and_dirty_word_wrap as word_wrap

    hotkeys = hotkeys_index.hotkeys
    return wrap_plan_via_page


_WrapPlan = _nt('_WrapPlan', ('wrap_grid', 'words_tuple'))


_Page = _nt('_Page', ('page_key', 'button_offsets',))


class _MutableHotkeysCache:

    def __init__(self):
        self.hotkeys = []
        self.hotkey_offsets_via_figurative_key_for_error_reporting = {}
        self.hotkey_offset_via_label = {}
        self.width_of_widest_hotkey_label = 0

    def STATIC_BUTTONS_THING(self, hotkey_label):
        """
        Discussion: Dynamic buttons can give the same letter different meanings
        on different pages. There might be a "[d]own" button on one page and a
        "[d]one" button on another. This is good and okay and normal.

        After all, if we had context-sensitive buttons but each button laid a
        universal claim on its letter, this wouldn't scale out to very many
        different contexts! :#here2

        On the other hand, static buttons (being static) lay an exclusive claim
        on their letter: If there's a static button "[q]uit", then no other
        button (static or dynamic) can use that letter.

        In the original rough prototype, we pre-declared what were the reserved
        hotkey *letters*. Then, if you declared any dyanmic buttons that used
        these letters you got a custom exception.

        Now we do it the other way: Now we define button .. definitions in the
        same visual order that they appear on screen (with the static button
        area below the dynamic button area).

        Because it feels most intuitive (and requires less code) to process
        the definition in order, we now do it the other way where *AS* each
        static is defined, it enforces the above rules, but it might be sort
        of "backwards" feeling for static to complain about dyanmics after
        the fact.
        """

        btn = _Hotkey(hotkey_label)
        k = btn.figurative_key

        arr_via_k = self.hotkey_offsets_via_figurative_key_for_error_reporting
        offsets = arr_via_k.get(k)
        if offsets:
            labels = tuple(self.hotkeys[i].label for i in offsets)
            rsns = []
            rsns.append(f"Can't create static button {hotkey_label!r}")
            these = ', '.join(repr(label) for label in labels)
            s = '' if 1 == len(labels) else 's'
            rsns.append(f"There's already button{s} with same letter {these}")
            raise RuntimeError('. '.join(rsns))

        return self._register(btn)

    def offset_of_lazily_created_hotkey(self, hotkey_label):
        i = self.hotkey_offset_via_label.get(hotkey_label)
        if i is None:
            return self._register(_Hotkey(hotkey_label))
        else:
            return i

    def _register(self, btn):
        offset = len(self.hotkeys)

        # Index by button label
        hotkey_label = btn.label
        dct = self.hotkey_offset_via_label
        assert hotkey_label not in dct
        dct[hotkey_label] = offset

        self.hotkeys.append(btn)  # after the above sanity check

        # We know that we don't have this button by label BUT: we may or may
        # not already have such a button by this letter (figurative key) #here2
        # (Mapping the button to its page is out of scope for this cache)
        fk = btn.figurative_key
        arr_via_k = self.hotkey_offsets_via_figurative_key_for_error_reporting
        if (arr := arr_via_k.get(fk)) is None:
            arr_via_k[fk] = (arr := [])
        arr.append(offset)

        # Keep track of what is the widest label you've ever seen, for etc
        if self.width_of_widest_hotkey_label < (w := len(hotkey_label)):
            self.width_of_widest_hotkey_label = w

        return offset


class _Hotkey:

    def __init__(self, label):
        if (md := _hotkey_rx.match(label)) is None:
            raise RuntimeError(f"you must comply. button label: {label!r}")
        self.label = label
        self.figurative_key = md[1]


_hotkey_rx = re.compile(r'''
    [^[\]]*         # zero or more not '[' or ']'
    \[([a-z]+)\]    # one or more [a-z] between '[' and ']'
    [^[\]]*         # again with the zero or more not '[' or ']'
    \Z              # match the end of the string
''', re.VERBOSE)


# == SNIP 3


def _scanner_via_iterator(itr):
    from text_lib.magnetics.scanner_via import scanner_via_iterator as func
    return func(itr)


def xx(msg=None):
    raise RuntimeError(''.join(('cover me', *((': ', msg) if msg else ()))))

# #history-B.4
# #born
