"""parse a stream of lines into a tree-like structure, assuming the..

..intuitive indentation rules similar to that of python. like:

    head
      eyes
      mouth
    torso
      arms
        left arm
        right arm
      legs
"""

from game_server import memoize

def tree_via_line_stream(line_st):

    _scanned_line_itr = (_ScannedLine(s) for s in line_st)
    scn = _scanner_via_iterator(_scanned_line_itr)

    if scn.has_current_token:
        return __tree_when_one_or_more_lines(scn)

def __tree_when_one_or_more_lines(scn):

    """traverse every line of input, effecting state changes.

      - implement the parsing grammar through a state machine whose
        transitions correspond to changes in indent from one line to
        another (with special handling for blank lines). (below we'll
        say "indentation deltas" to mean changes in indentation from
        one line to another (including the "no change" change))

      - the transitions in the state machine will effect "actions"
        (code) that probaly places each input line somewhere into a
        stack which will somehow end up as the output tree.

      - the responsibility here is simply to traverse every line of
        input straightforwardly, comparing each current line to each
        previous line, effecting the appropriate transition at each
        hop (again, recognizing blank lines as special).

      - detail: let a "hop" be the transition from one line to another.
        any sequence of N lines has N-1 hops. hops are what effect state
        machine transitions, and transitions are how actions are
        effected, and actions are where our result structure is built.

        we want the first line of input to trigger the same indentation-
        delta-based mechanics as the rest of the parsing, but note there
        is no hop onto the first line because there is no pre-existing
        line to compare it to. so imagine this:

        imagine an "imaginary line before the first line" that:
          - is not a blank line
          - has no indent

        modeling such an imaginary line has these advantages:

          - we get to have One Loop to rule them all, that handles
            the first line indifferently from other lines.

          - there are certain special assertions that we want to make of the
            first line of input: that it is not a blank line, that it is not
            indented. we can effect these assertions "for free" through our
            state machine by virtue of not modeling those transitions we
            disallow. but in order to employ the state machine for this
            purpose, we have to see the first line of input in terms of an
            indentation delta just as we do the other lines.

          - as it works out, we also want to make these same assertions
            for every first line of a top-level section, not just the
            first line of input. we will re-use this this "imaginary
            line" for this purpose #here2.
    """

    def __main_loop():
        while True:
            this_line = scn.current_token
            if this_line.is_blank_line:
                state.blank_line()
            else:
                prev_line = state.use_this_line_as_reference
                prev_num = prev_line.effective_margin_length
                this_num = this_line.effective_margin_length
                if prev_num < this_num:
                    state.more_indent()
                elif prev_num == this_num:
                    state.same_indent()
                else:
                    state.less_indent()

            scn.advance_by_one_token()
            if not scn.has_current_token:
                break

    _l = lambda: scn.current_token
    state = _StateMachine(_l, _this_one_state_machine_definition())
    __main_loop()
    _tree = state.end_of_input()
    return _tree

@memoize
def _this_one_state_machine_definition():
    """the definitional structure of our state machine

    in part, the state machine helps assert which kinds of transitions
    can and cannot happen from various states. (for example, we do not
    allow that the very first line is blank or indented. for now, these
    provisions appear to extend also to every line that comes in after
    a blank line. we model both these cases under a single state we call
    'nothingness'.)

    this is memoized in part to emphasize that it is immutable, invariant
    structure through the course of our execution.

    (dynamic grammars *are* a thing but we'd rather avoid them if possible..)
    """

    return {
        'nothingness': {
            'same_indent': 'indeterminate_line',  # read 'no_indent'
        },
        'indeterminate_line': {
            'blank_line': 'nothingness',
            'same_indent': 'branch_node',
            'more_indent': 'indeterminate_line',
            'less_indent': 'indeterminate_line',
            'end_of_input': 'closed',
        },
        'branch_node': {
            'blank_line': 'nothingness',
            'same_indent': 'branch_node',
            'more_indent': 'indeterminate_line',
            'less_indent': 'indeterminate_line',
            'end_of_input': 'closed',
        },
    }

class _StateMachine:
    """(the more abstract parts of this could certainly be abstracted out..)

    (..the bulk of this is business-specific but etc.)
    """

    def __init__(self, curr_tok_f, states_d):

        self._current_line_function = curr_tok_f
        self._use_the_special_reference_line_for_nothingness()
        self._stack = [ _StackFrame() ]

        self._current_state_name = 'nothingness'
        self._states = states_d

    def from__nothingness__to__indeterminate_line__because__same_indent(self):
        self._use_current_line_as_indeterminate_line_and_reference_line()

    def from__indeterminate_line__to__nothingness__because__blank_line(self):
        self._add_indeterminate_line_to_branch_node()
        self._common_after_blank_line()

    def from__indeterminate_line__to__branch_node__because__same_indent(self):
        self._begin_branch_node_with_indeterminate_line_as_header_line()
        # self._add_indeterminate_line_to_branch_node()
        self._use_current_line_as_indeterminate_line_and_reference_line()

    def from__indeterminate_line__to__indeterminate_line__because__more_indent(self):
        self._begin_branch_node_with_indeterminate_line_as_header_line()
        self._use_current_line_as_indeterminate_line_and_reference_line()

    def from__indeterminate_line__to__indeterminate_line__because__less_indent(self):
        self._common_pop()

    def from__branch_node__to__nothingness__because__blank_line(self):
        self._add_indeterminate_line_to_branch_node()
        self._common_after_blank_line()

    def from__branch_node__to__branch_node__because__same_indent(self):
        self._add_indeterminate_line_to_branch_node()
        self._use_current_line_as_indeterminate_line_and_reference_line()

    def from__branch_node__to__indeterminate_line__because__more_indent(self):
        self._begin_branch_node_with_indeterminate_line_as_header_line()
        self._use_current_line_as_indeterminate_line_and_reference_line()

    def from__branch_node__to__indeterminate_line__because__less_indent(self):
        self._common_pop()

    def from__branch_node__to__closed__because__end_of_input(self):
        return self._common_close()

    def from__indeterminate_line__to__closed__because__end_of_input(self):
        return self._common_close()


    # --

    def _common_pop(self):
        self.__add_indeterminate_line_to_branch_node_and_pop_stack_appropriately()
        self._use_current_line_as_indeterminate_line_and_reference_line()


    def _common_close(self):
        self._add_indeterminate_line_to_branch_node()
        return self._close()

    # --

    def __add_indeterminate_line_to_branch_node_and_pop_stack_appropriately(self):
        self._add_indeterminate_line_to_branch_node()
        target_num = self._current_line_function().effective_margin_length

        if _D: print("POPPING STACK down to a guy with an indent of %d HACKING STATE CHANGE" % target_num)

        stack = self._stack
        while True:
            frame = stack.pop()
            this_num = frame.the_effective_margin_length
            if this_num > target_num:
                # it is normal to see a depth that is deeper than your tareget depth
                # cover_me('you may already be a winner')
                pass  # #coverpoint1.1
            elif this_num == target_num:
                # if the depth of this item we just popped off the stack
                # IS EQUAL to the depth of the current line, that means they
                # are siblings, and that the stack is now ready to accept
                # this child (the current line) when it reaches determinancy.
                break
            else:
                cover_me('strange indent level')

        self._current_state_name = 'branch_node'

    def _common_after_blank_line(self):

        if _D: print("POP STACK down to first frame because blank line")

        stack = self._stack
        while len(stack) is not 1:
            stack.pop()

        self._use_the_special_reference_line_for_nothingness()  # :#here2

    def _begin_branch_node_with_indeterminate_line_as_header_line(self):

        _line = self._release_indeterminate_line()

        if _D: print("creating and PUSHing branch node with header line: "+_line._match[0])

        former_top = self._top_frame()
        next_frame = former_top.__class__()
        next_frame.append_terminal_item(_line)

        former_top.append_child_frame(next_frame)

        self._stack.append(next_frame)


    def _add_indeterminate_line_to_branch_node(self):
        _line = self._release_indeterminate_line()
        if _D: print("ACTUALLY adding this line to existing branch node: "+_line._match[0])
        self._top_frame().append_terminal_item(_line)

    def _release_indeterminate_line(self):
        line = self._indeterminate_line
        del self._indeterminate_line
        return line

    def _use_current_line_as_indeterminate_line_and_reference_line(self):
        line = self._current_line_function()
        self._indeterminate_line = line
        self.use_this_line_as_reference = line

    def _use_the_special_reference_line_for_nothingness(self):
        self.use_this_line_as_reference = _IMAGINARY_LINE_BEFORE_FIRST_LINE

    def _top_frame(self):
        return self._stack[-1]

    def _close(self):
        del self._current_line_function
        del self._current_state_name
        del self._states
        del self.use_this_line_as_reference
        stack = self._stack
        del self._stack
        if len(self.__dict__) is not 0: OCD()
        return stack[0].close_stack()

    # --

    def transition(f):
        """(decorator)"""

        transition_name = f.__name__
        def g(self):
            state_name = self._current_state_name
            state_d = self._states[state_name]
            if transition_name in state_d:
                return self._do_transition(state_d[transition_name], transition_name)
            else:
                _fmt = "cannot have '{t}' from '{s}'"
                _msg = _fmt.format(s=state_name, t=transition_name)
                raise _my_exception(_msg)
        return g

    def _do_transition(self, new_state_name, trans_name):
        s = self._current_state_name
        self._current_state_name = new_state_name
        _m = 'from__%s__to__%s__because__%s' % (s, new_state_name, trans_name)
        return getattr(self.__class__, _m)(self)

    @transition
    def blank_line(self):
        pass

    @transition
    def less_indent(self):
        pass

    @transition
    def same_indent(self):
        pass

    @transition
    def more_indent(self):
        pass

    @transition
    def end_of_input(self):
        pass


class _ThisDummy:
    def __init__(self):
        self.effective_margin_length = 0
        self.is_blank_line = False

_IMAGINARY_LINE_BEFORE_FIRST_LINE = _ThisDummy()


class _StackFrame:

    def __init__(self):
        self.children = []

    def append_child_frame(self, x):
        x.hello_stack_frame()
        self.children.append(x)

    def append_terminal_item(self, x):
        if not x.is_terminal: sanity()
        self.children.append(x)

    def close_stack(self):
        lis = self.children
        del self.children
        def f(x):
            if x.is_terminal:
                return x
            else:
                return x.close_stack()
        return _BranchNode( [ f(x) for x in lis ] )

    @property
    def the_effective_margin_length(self):  # assume first child is terminal yikes
        return self.children[0].effective_margin_length

    @property
    def is_terminal(self):
        return False

    def hello_stack_frame(self):
        pass  # #wish [#008.D]


class _BranchNode:

    def __init__(self, cx):
        self.children = cx

    @property
    def is_terminal(self):
        return False


class _ScannedLine:

    def __init__(self, line_s):
        match = self.__class__._THIS_ONE_RE.search(line_s)
        if match is None: outside_of_spec('assume newline terminated for now')
        self._match = match

        margin_s = self.margin_string
        content_s = self.styled_content_string

        is_blank_line = False
        if margin_s is None:
            if content_s is None:
                is_blank_line = True
            else:
                self.effective_margin_length = 0
        elif content_s is None:
            raise _my_exception('blank line with trailing whitespace is frowned upon: '+repr(line_s))
        elif _TAB in margin_s:
            raise _my_exception('tabs are gonna be annoying because math')
        else:
            self.effective_margin_length = len(margin_s)

        self.is_blank_line = is_blank_line


    def reader_for_named_group(m):
        """(ad-hoc single-purpose decorator for this classs only)"""

        name = m.__name__
        def f(self):
            return self._match.group(name)
        return f

    @property
    @reader_for_named_group
    def styled_content_string():
        pass

    @property
    @reader_for_named_group
    def margin_string():
        pass

    @property
    def is_terminal(self):
        return True

    # #todo - can you employ decorators without a starting method :#here1

    import re
    _THIS_ONE_RE = re.compile(
        '^(?P<margin_string>[ \t]+)?'+  # there need not be any, but if there is, etc.
        '(?P<styled_content_string>[^\n\r]+)?'+  # there need not .. ibid.
        '(?:\n|\r\n?)'
    )


def _line_stream_via_big_string(big_s):  # #testpoint
    """convert any string into a stream of "lines" (isomorphically)..

    ## objective & scope

    intended for for "consuming agents" that want to parse a "big string"
    one "line" at at time.

    in practice this is useful for implementing a parser for line-centric
    grammars. i.e, this produces a tokenizer (scanner) whose tokens are
    lines.


    ## implementation notes (and possible counter-justification)

    in ruby and perhaps python, the spirit of this could be achieved with
    a oneliner something like `big_s.split(/(?<=\n)/)`. but in the current
    stable version of python, they disallow this "zero-width regex" (even
    though it does not cause the kind of problems they are trying to prevent.
    this sounds like it's getting some attention there.)

    fortunately python's `re.finditer()` does not have the same limitation
    as `re.split()` (weirdly), and produces a function that is as
    elegant and more memory efficient, scaling to "large" strings more
    reasonably. (we didn't always use a generator expression for this.
    see #history-A.1 for its clunkier predecessor.)


    ## theory & details

    in the unix world, lines are terminated by the the newline character
    ("\n"). but it would be trivial to extend this work to other formats
    (MS-DOS/windows "\r\n", ancient mac "\r") if (in our language if not
    our code) we broaden the conception of this "newline character" into
    the more abstract-sounding "line terminator sequence" ("LTS").

    it's now worth considering the difference between "separator semantics"
    and "terminator semantics"; a distinction discussed in the manpage for
    `git-log` near those terms. the question basically amounts to whether
    the last line (of a file, e.g) should itself end with the LTS or not.

    fortunately there's a strong convention, as is suggested by the manpage
    for the unix utility `wc`:

      > A line is defined as a string of characters delimited by a <newline> character

    this is to say, it appears that terminator (not separator) semantics
    are considered the norm.

    however, if we were to omit into oblivion any one-or-more non-LTS
    characters that trail the "big string" of input (as `wc` does), this
    would very likely effect unexpected behavior, with users wondering
    where the rest of their string went.

    as such, the subject does not act as a "normalizer" in this regard -
    it's garbage-in, garbage-out if you like. if your "big string"'s final
    "line" does *not* have an LTS, this "line" will still come back out as-
    is (i.e without an LTS). (tests cover this).
    """

    import re
    return( match[0] for match in re.finditer('[^\n]*\n|[^\n]+', big_s) )
        # (note we aren't even messing with non-unix line-ending formats for now)


class _scanner_via_iterator:  # #testpoint
    """there is a fundamental idiomatic difference between scanners and iterators..

    ..even though are isomorphic to one another.
    """

    def __init__(self, itr):
        self._iterator = itr
        self.has_current_token = True
        self.current_token = None
        self.advance_by_one_token()

    def advance_by_one_token(self):
        stay, item = self.__next_stay_and_item()
        if stay:
            self.current_token = item
        else:
            del self.current_token
            self.has_current_token = False

    def __next_stay_and_item(self):
        try:
            x = next(self._iterator)
            return True, x
        except StopIteration:
            del self._iterator
            return False, None


def _my_exception(msg):  # #copy-pasted
    from game_server import Exception as MyException
    return MyException(msg)


_EMPTY_S = ''  # ..
_TAB = "\t"

_D = False  # turn on debugging output

# #history-A.1: refactor line streamer to use generator expression
# born.
