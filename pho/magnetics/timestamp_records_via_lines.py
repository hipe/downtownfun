import re

# ==== BEGIN SYNC STUFF ======================================================

# Terminology: The local collection is the "logfile" and the remote collection
# the "spreadsheet".
#
# Design choices and premises:
#
# 👉 For the near forseeable future, this syncing operation only ever pushes
#    "up" to the spreadsheet. It never pulls "down" from the spreadsheet in
#    to the logfile. So a better name might be "push" rather than "sync",
#    but for the fact that "sync" is such a well-known idiom.
#
# 👉 For the near forseeable future, this syncing operation only ever adds
#    rows (it never deletes or modifies) to the existing spreadsheet.
#
# 👉 The logfile is appended to (it grows downward) whereas in the spreadsheet,
#    each next entity is inserted at the top (it grows upwards). That is to
#    say, the two sides grow in opposite directions. (Both choices
#    have reasons, of UI and idiomatic and historical.) In a broad sense the
#    dimensionality is arbitrary but in practice it impacts every aspect of
#    the algorithm, including how we describe everything here.
#
# 👉 In both cases, multi-line entries read downward; i.e., the logfile reads
#    "normally" in both respects; but on the spreadsheet, the most recent
#    entity is at the top but you won't have to read its lines from down
#    to up. That is, within the entity you still read the lines "normally",
#    no matter which side you're looking at.
#    As such, when you have multi-line entities, the same two collections
#    won't have the same line order even after you take in to account the
#    opposite growth directions.
#
# 👉 Entities from the two sides are compared for equality like so: two normal
#    entites are equal IFF they have string equality for their date, time, and
#    each of their N messages (i.e., N must be the same). (A corollary of this
#    is that if you have two entries with the same message within the same
#    minute, syncing behavior is undefined (but shouldn't be catastrophic).)
#
# 👉 Premise: the topmost entity in the spreadsheet exists somewhere in the
#    logfile. (Syncing into an empty spreadsheet is considered an edge case
#    with a straightforward workaround: hand-insert the very first entry.)
#
# So the algortihm for a typical sync: Get the topmost entity from the
# spreadsheet. (You will have to read multiple rows to know if you got all
# the messages and possibly to populate the date field.)
#
# Traverse the local entities (top-to-bottom, earlier to later) looking for
# a match to the reference entity. Once it is found, each local entity that
# comes after it in the stream is one you will insert on the cloud. Cache
# every such entity - flush the remainder of the stream so you have a tuple.
# Now the entities to be added proceed chronologically left to right.
#
# Excercise to the reader: sparsifying the years. That's it!


def records_to_push_via_entities_to_push_(ref, add_me):
    # we determine whether or not to show the dates by going forwards in time
    # and then we replay it backwards in time to get the newest at the top.
    # so we use two parallel stacks, sort of for giggles

    current_date_s = ref.date_string

    show_date_yes_no_stack = []
    local_entities_stack = []

    for ent in add_me:
        date_s = ent.date_string
        if current_date_s == date_s:
            show_date_yes_no_stack.append(False)
        else:
            show_date_yes_no_stack.append(True)
            current_date_s = date_s
        local_entities_stack.append(ent)

    while True:
        ent = local_entities_stack.pop()
        do_show_date = show_date_yes_no_stack.pop()

        use_date_s = ent.date_string if do_show_date else ''

        time_s = ent.time_string
        assert(8 == len(time_s))  # [#882.J]
        use_time_s = time_s[0:5]  # lose precision when pushing

        msgs = ent.message_strings

        yield (use_date_s, use_time_s, msgs[0])

        for msg in msgs[1:]:
            yield ('', '', msg)

        if not len(local_entities_stack):
            break


def reference_and_normal_entities_to_sync_(
        local_normals_iterator, remote_records_iterator, listener):
    # the main workhorse of the syncing operation (see algorithm) #testpoint

    remote_normal = _normal_topmost_entity(remote_records_iterator, listener)

    find_this_date_s = remote_normal.date_string
    find_this_time_s = remote_normal.time_string
    assert(5 == len(find_this_time_s))  # [#882.J]

    scn = _scanner_via_iterator(local_normals_iterator)
    if scn.empty:
        xx("logfile empty? nothing to sync?")

    def is_equal():
        if find_this_date_s != local_normal.date_string:
            return False

        time_s = local_normal.time_string
        assert(8 == len(time_s))  # [#882.J]
        hours_minutes_s = time_s[0:5]  # lose precision when pushing

        if find_this_time_s != hours_minutes_s:
            return False
        return remote_normal.message_strings == local_normal.message_strings

    # discard every local entity we traverse over including the one that match
    found_reference_entity = False
    while scn.more:
        local_normal = scn.next()
        if is_equal():
            found_reference_entity = True
            break

    if not found_reference_entity:
        xx(f"remote entity not found anywhere in {scn.lineno} lines")

    if scn.empty:
        xx("apparently there are no new entities to push")

    push_these = []
    while scn.more:
        push_these.append(scn.next())
    assert(len(push_these))
    return (remote_normal, tuple(push_these))


def _normal_topmost_entity(remote_records_iterator, listener):
    # this would be nicer as a stream of normal entities like the other thing.
    # imagine paging, stopping after each entity with a date

    scn = _scanner_via_iterator(remote_records_iterator)
    if scn.empty:
        xx()

    date_s, time_s, msg = scn.next()

    # keep (only) the first date that we find
    def maybe_remember_date():
        if len(use_date_s_pointer):
            return
        if len(date_s):
            assert(len(time_s))  # just saying hello
            use_date_s_pointer.append(date_s)

    use_date_s_pointer = []  # the worst
    maybe_remember_date()

    # first record must have time
    assert(len(time_s))
    use_time_s = time_s

    # first record must have message
    assert(len(msg))
    use_messages = [msg]

    # we don't know that we've found the last message for this entity until
    # either we exhaust the input or we find another populated time cell

    while scn.more:
        date_s, time_s, msg = scn.next()
        maybe_remember_date()
        if len(time_s):  # you found a record with time. it's the next entity
            break
        assert(len(msg))  # message cels should never be blank
        use_messages.append(msg)

    # now, keep looking for a date if we haven't found one yet

    while not (len(use_date_s_pointer) or scn.empty):
        date_s, _, __ = scn.next()
        maybe_remember_date()

    if not len(use_date_s_pointer):
        assert scn.empty
        xx(f'no date found in {scn.lineno} records')

    use_date_s, = use_date_s_pointer

    return _NormalStruct(use_date_s, use_time_s, tuple(use_messages), 1)


# ==== END SYNC STUFF ========================================================


def normal_structs_via_lines(lines):
    _line_rec_scts = line_record_structs_via_lines_(lines)
    return normal_structs_via_line_record_structs_(_line_rec_scts)


def normal_structs_via_line_record_structs_(structs):

    most_recent_date_string = None
    most_recent_time_string = None
    message_list = []
    last_significant_lineno = None

    def has_pending():
        return len(message_list)

    def flush():
        assert(most_recent_date_string)
        assert(most_recent_time_string)
        assert(len(message_list))

        msg_strings = tuple(message_list)
        message_list.clear()
        return _NormalStruct(
                date_string=most_recent_date_string,
                time_string=most_recent_time_string,
                message_strings=msg_strings, lineno=last_significant_lineno)

    def at():
        return f" at line {sct.lineno}"

    for sct in structs:

        ds = sct.date_string
        ts = sct.time_string
        ms = sct.message_string

        assert(len(ms))  # #here1

        if ds is None:
            if ts is None:
                if most_recent_time_string is None:
                    raise _MyExe("supplemental message w/o first msg" + at())
            else:
                if most_recent_date_string is None:
                    raise _MyException("date must be somewhere above" + at())

                if has_pending():
                    yield flush()

                most_recent_time_string = ts
                last_significant_lineno = sct.lineno
        else:
            if ts is None:
                raise _MyException("datestamp without timestamp?" + at())

            if has_pending():
                yield flush()

            most_recent_date_string = ds
            most_recent_time_string = ts
            last_significant_lineno = sct.lineno

        message_list.append(ms)  # #here1

    if has_pending():  # should be true always except for empty files
        yield flush()


class _NormalStruct:
    def __init__(self, date_string, time_string, message_strings, lineno):
        self.date_string = date_string
        self.time_string = time_string
        self.message_strings = message_strings
        self.lineno = lineno


def line_record_structs_via_lines_(lines):
    class LineCounter():
        def __init__(self):
            self.count = 0

        def __call__(self):
            self.count += 1
            return self.count

    inc = LineCounter()
    return (_line_record_struct_via_line(line, inc()) for line in lines)


def _line_record_struct_via_line(line, lineno):

    def at():
        return f' at line {lineno} - {line[0:-1]}'

    md = _line_rx.match(line)
    if md is None:
        raise _MyException(f"line must be at least {_min_width} long" + at())

    day_cell, time_cell, message_cell = md.groups()

    md = _day_cell_rx.match(day_cell)
    if md is None:
        raise _MyException(f'must be mm-dd: {repr(day_cell)} ' + at())
    date_string = md[1]

    md = _time_cell_rx.match(time_cell)
    if md is None:
        raise _MyException(f'must be hh:mm:ss {repr(day_cell)} ' + at())
    time_string = md[1]

    md = _message_cell_rx.match(message_cell)
    msg = md and md[1].strip()
    if not msg and len(msg):  # #here1
        raise _MyException("there must be some message " + at())

    return _LineRecordStruct(
            date_string=date_string, time_string=time_string,
            message_string=msg, lineno=lineno)


_seven = 7
_nine = 9
_line_rx = re.compile(f'^(.{{{_seven}}})(.{{{_nine}}})(.+)\\n\\Z')
_min_width = _seven + _nine + 1


_day_cell_rx = re.compile(r'^[ ]{2}(?:(\d\d-\d\d)|[ ]{5})\Z')
_time_cell_rx = re.compile(r'^[ ]{1}(?:(\d\d:\d\d:\d\d)|[ ]{8})\Z')
_message_cell_rx = re.compile(r'^[ ]{2}(.+)\Z')  # #here1


class _LineRecordStruct:

    def __init__(self, date_string, time_string, message_string, lineno):
        self.date_string = date_string
        self.time_string = time_string
        self.message_string = message_string
        self.lineno = lineno


def _scanner_via_iterator(itr):  # #testpoint (for lineno)
    def on_advance():
        scn.lineno += 1
    import text_lib.magnetics.scanner_via as scnlib
    scn = scnlib.scanner_via_iterator(itr)
    scn.lineno = 0
    scnlib.MUTATE_add_advance_observer(scn, on_advance)
    return scn


def xx(msg=None):
    raise RuntimeError(f'cover me{": " + msg if msg else ""}')


class _MyException(RuntimeError):
    pass


_MyExe = _MyException


if __name__ == '__main__':
    from sys import stdout, stderr, argv
    prog_name, *args = argv
    so = stdout.write
    se = stderr.write

    def usage():
        se(f'usage: {prog_name} <filename>\n')

    if len({'-h', '--help'} & set(args)):
        usage()
        se('description: attempt to parse a timestamps file\n')
        exit(0)

    filename, = args  # ..

    with open(filename) as lines:
        _ = line_record_structs_via_lines_(lines)
        for o in normal_structs_via_line_record_structs_(_):
            so(f"{o.date_string} {o.time_string} (line {o.lineno}):\n")
            count = 0
            for msg in o.message_strings:
                count += 1
                so(f"  msg {count}:  {msg}\n")
# #born.
