from script_lib.cheap_arg_parse import formals_via_definitions as formals_via


def _formals_for_toplevel():
    yield '-r', '--readme=PATH', "or use PHO_README. '-' might read from STDIN"
    yield '-h', '--help', 'This screen'
    yield 'command [..]', "One of the below"


def _subcommands():
    yield 'open', lambda: _subcommand_open
    yield 'close', lambda: _subcommand_close
    yield 'list', lambda: _subcommand_list
    yield 'top', lambda: _subcommand_top
    yield 'which', lambda: _subcommand_which
    yield 'use', lambda: _subcommand_use
    yield 'find-readmes', lambda: _subcommand_find_readmes
    yield 'graph', lambda: _subcommand_graph


def CLI(sin, sout, serr, argv, enver):
    """my dream as a boy and as a man
    desc line 2
    """

    bash_argv = list(reversed(argv))
    long_program_name = bash_argv.pop()

    def prog_name():
        pcs = long_program_name.split(' ')
        from os.path import basename
        pcs[0] = basename(pcs[0])
        return ' '.join(pcs)

    foz = formals_via(_formals_for_toplevel(), prog_name, _subcommands)
    vals, es = foz.nonterminal_parse(serr, bash_argv)
    if vals is None:
        return es

    if vals.get('help'):
        return _write_help_into(serr, CLI.__doc__, foz)

    # The Ultra-Sexy Mounting of an Alternation Component:
    cmd_tup = vals.pop('command')
    cmd_name, cmd_funcer, es = foz.parse_alternation_fuzzily(serr, cmd_tup[0])
    if not cmd_name:
        return es

    ch_pn = ' '.join((prog_name(), cmd_name))  # we don't love it, but later
    ch_argv = (ch_pn, * cmd_tup[1:])

    def env_and_related():
        from os import environ
        return environ, vals

    return cmd_funcer()(sin, sout, serr, ch_argv, env_and_related)


def _formals_for_open():
    yield '-h', '--help', 'this screen'
    yield '<message>', 'any one line of some appropriate length'


def _subcommand_open(sin, sout, serr, argv, env_stacker):
    """Open an issue"""

    prog_name = (bash_argv := list(reversed(argv))).pop()
    foz = formals_via(_formals_for_open(), lambda: prog_name)
    vals, es = foz.terminal_parse(serr, bash_argv)
    if vals is None:
        return es

    if vals.get('help'):
        return _write_help_into(serr, _subcommand_open.__doc__, foz)

    env_stack = env_stacker()
    if (readme := _resolve_readme(serr, env_stack)) is None:
        return 4

    dct = {'main_tag': '#open', 'content': vals['message']}
    mon = _error_monitor(serr)
    from pho._issues.edit import open_issue as func
    bef_aft = func(readme, dct, mon.listener)
    if bef_aft is not None:
        before, after = bef_aft
        if before:
            serr.write(f"before: {before.to_line()}")
            serr.write(f"after:  {after.to_line()}")
        else:
            serr.write(f"line:   {after.to_line()}")
    return mon.exitstatus


def _formals_for_close():
    yield '-h', '--help', 'this screen'
    yield '<identifier>', 'whomst ("123" or "#123" or "[#123]" all OK)'


def _subcommand_close(sin, sout, serr, argv, env_stacker):
    """Close an open issue..

    Actually what this probably does is update *any* issue to become a '#hole'.
    It does not actually confirm that the issue is open, as far as we know.
    """

    prog_name = (bash_argv := list(reversed(argv))).pop()
    foz = formals_via(_formals_for_close(), lambda: prog_name)
    vals, es = foz.terminal_parse(serr, bash_argv)
    if vals is None:
        return es

    if vals.get('help'):
        return _write_help_into(serr, _subcommand_close.__doc__, foz)

    env_stack = env_stacker()
    if (readme := _resolve_readme(serr, env_stack)) is None:
        return 4

    eid = vals['identifier']

    mon = _error_monitor(serr)
    from pho._issues.edit import close_issue as func
    func(readme, eid, mon.listener)
    return mon.exitstatus


def _formals_for_top():
    yield '-M', '--newest-first', 'opposite of default (oldest first)'
    yield '-q', '--quick', 'take away sort by mtime. overrides above'
    yield _batch_opt
    yield '-f', '--format=FMT', '{json|table} (default: table)'
    yield '-<number>', _build_int_matcher, 'show the top N items (default: 3)'
    yield '-h', '--help', 'this screen'
    yield '[query […]]', "default: '#open'. Currently limited to 1 tag."


def _subcommand_top(sin, sout, serr, argv, env_stacker):
    "`list` with popular defaults"

    bash_argv = list(reversed(argv))
    prog_name = bash_argv.pop()
    foz = formals_via(_formals_for_top(), lambda: prog_name)
    vals, es = foz.terminal_parse(serr, bash_argv)
    if vals is None:
        return es

    if vals.get('help'):
        return _write_help_into(serr, _subcommand_top.__doc__, foz)

    easy_defaults = {'format': 'table', 'number': 3, 'query': ('#open',)}
    easy_defaults.update(vals)
    vals = easy_defaults

    if 'newest_first' not in vals:
        vals['oldest_first'] = True

    if vals.get('quick'):
        vals.pop('oldest_first', None)
        vals.pop('newest_first', None)

    return _top_or_list(sin, sout, serr, vals, foz, env_stacker)


def _formals_for_list():
    yield '-m', '--oldest-first', 'sort by time last modified (acc. to VCS)'
    yield '-M', '--newest-first', 'sort by time last modified (acc. to VCS)'
    yield _batch_opt
    yield '-f', '--format=FMT', '{json|table} (default varies)'
    yield '-<number>', _build_int_matcher, 'show the top N items'
    yield '-h', '--help', 'this screen'
    yield '[query […]]', "e.g '#open'. Currently limited to 1 tag."


_batch_opt = '-b', '--batch', "treat --readme (or PHO_README) as list of paths"


def _subcommand_list(sin, sout, serr, argv, env_stacker):
    """List issues according to the query"""

    bash_argv = list(reversed(argv))
    prog_name = bash_argv.pop()
    foz = formals_via(_formals_for_list(), lambda: prog_name)
    vals, es = foz.terminal_parse(serr, bash_argv)
    if vals is None:
        return es

    if vals.get('help'):
        return _write_help_into(serr, _subcommand_list.__doc__, foz)

    return _top_or_list(sin, sout, serr, vals, foz, env_stacker)


def _top_or_list(sin, sout, serr, vals, foz, env_stacker):

    # Local variables via vals
    sort_by_time = None
    if vals.get('oldest_first'):
        if vals.get('newest_first'):
            serr.write(f"-m and -M are mutually exclusive. {foz.invite_line}")
            return 4
        sort_by_time = 'ASCENDING'
    elif vals.get('newest_first'):
        sort_by_time = 'DESCENDING'

    env_stack = env_stacker()
    if (readme := _resolve_readme(serr, env_stack)) is None:
        return 4

    readme_is_dash = '-' == readme
    do_batch = vals.get('batch')
    query = vals.get('query')

    # Resolve query
    mon = _error_monitor(serr)
    if query is not None:
        from pho._issues import parse_query_ as func
        if (query := func(query, mon.listener)) is None:
            return 4

    # Quad table
    if do_batch:
        if readme_is_dash:
            # Read from stdin and each line is a readme path
            opened = sin
        else:
            # Open readme and each line is passed to the collection constructor
            opened = open(readme)
    elif readme_is_dash:
        # Pass stdin to open as the collection
        opened = _pass_thru_context_manager((sin,))
    else:
        # Pass the readme path to the collection
        opened = _pass_thru_context_manager((readme,))

    # Run the query
    from pho._issues import records_via_query_ as func
    itr = func(opened, sort_by_time, query, do_batch, mon.listener)
    jsoner, counts = next(itr)

    # Prepare for output
    is_complicated = do_batch or sort_by_time is not None
    if (fmt := vals.get('format')) is not None:
        allow = 'json', 'table'
        if fmt not in allow:
            _ = ''.join(('{', '|'.join(allow), '}'))
            inv = foz.invite_line
            serr.write(''.join((f'-f must be {_}. Had: {fmt!r}. ', inv)))
            return 4
        if 'table' == fmt:
            fmt = 'most_complicated' if is_complicated else 'simplest'
    else:
        fmt = 'json' if sort_by_time else 'simplest'

    # Prepare to limit output
    if (num := vals.get('number')) is None:
        def stop_here():
            return False
    else:
        def stop_here():
            return num == counts.items

    # Output results
    oa = getattr(_output_adapters, fmt)(sout, do_batch, sort_by_time, jsoner)
    oa.at_beginning_of_output_collection()
    curr_readme = None
    for rec in itr:
        counts.items += 1
        if curr_readme != rec.readme:
            curr_readme = rec.readme
            oa.maybe_output_header(rec)
        oa.output_record(rec)
        if stop_here():
            break
    oa.at_ending_of_output_collection()

    # Output summary
    if do_batch or 0 == counts.items or 'json' == fmt:
        serr.write(f"({counts.items} items(s) in {counts.files} file(s))\n")
    return mon.exitstatus


def _build_most_complicated_output_adapter(sout, do_batch, do_time, jsoner):

    assert do_time or do_batch
    if do_time and do_batch:
        def pieces(rec):
            yield cel_for_time(rec)
            yield chomped_orig_line(rec)
            yield cel_for_readme(rec)
            yield '\n'
    elif do_time:
        def pieces(rec):
            yield cel_for_time(rec)
            yield rec.row_AST.to_line()
    else:
        def pieces(rec):
            yield chomped_orig_line(rec)
            yield cel_for_readme(rec)
            yield '\n'
        assert do_batch

    def cel_for_time(rec):
        return rec.mtime.strftime(use_strftime_fmt)

    def cel_for_readme(rec):
        return ''.join((' | ', rec.readme))

    from kiss_rdb.vcs_adapters.git import DATETIME_FORMAT as strftime_fmt
    use_strftime_fmt = f"| {strftime_fmt} "

    def chomped_orig_line(rec):
        return rec.row_AST.to_line()[:-1]

    class lets_go:  # #class-as-namespace
        at_beginning_of_output_collection = _niladic_no_op
        maybe_output_header = _monadic_no_op

        def output_record(rec):
            sout.write(''.join(pieces(rec)))

        at_ending_of_output_collection = _niladic_no_op

    return lets_go


def _build_json_output_adapter(sout, do_batch, do_time, jsoner):
    class json_output_adapter:  # #class-as-namespace
        def at_beginning_of_output_collection():
            sout.write('[')

        def maybe_output_header(_):
            pass

        output_record = jsoner(sout, do_time)

        def at_ending_of_output_collection():
            sout.write(']\n')

    return json_output_adapter


def _build_simplest_output_adapter(sout, do_batch, do_time, jsoner):
    def output_header(rec):
        if subsequent():
            sout.write('\n')
        sout.write(f"## {rec.readme}\n")

    class simplest_output_adapter:  # #class-as-namespace
        at_beginning_of_output_collection = _niladic_no_op

        maybe_output_header = output_header if do_batch else _monadic_no_op

        def output_record(rec):
            sout.write(rec.row_AST.to_line())

        at_ending_of_output_collection = _niladic_no_op

    def subsequent():
        if subsequent.value:
            return True
        subsequent.value = True

    subsequent.value = False

    return simplest_output_adapter


class _output_adapters:
    most_complicated = _build_most_complicated_output_adapter
    json = _build_json_output_adapter
    simplest = _build_simplest_output_adapter


def _resolve_readme(serr, env_stack):
    readme = env_stack[1].get('readme') or env_stack[0].get('PHO_README')
    if readme:
        return readme
    serr.write("please use -r or PHO_README for now.\n")


def _formals_for_find_readmes():
    yield '-h', '--help', 'This screen'
    yield 'path?', "Filesystem path to search (default: '.')"  # [path] #todo


def _subcommand_find_readmes(sin, sout, serr, argv, env_and_vals_er):
    """Find the README.md files in our sub-projects

    This is a development aid.
    """

    prog_name = (bash_argv := list(reversed(argv))).pop()
    foz = formals_via(_formals_for_find_readmes(), lambda: prog_name)
    vals, es = foz.terminal_parse(serr, bash_argv)
    if vals is None:
        return es

    if vals.get('help'):
        return _write_help_into(serr, _subcommand_find_readmes.__doc__, foz)

    path = vals.get('path', '.')
    args = ('find', path, '-maxdepth', '2', '-name', 'README.md')
    import subprocess as sp
    opened = sp.Popen(args=args, text=True, cwd='.',
                      stdin=sp.DEVNULL, stdout=sp.PIPE, stderr=sp.PIPE)
    with opened as proc:
        while True:
            did = False
            for line in proc.stderr:
                serr.write(f"error from find?: {line}")
                did = True
            if did:
                exitstatus = 4
                break
            for line in proc.stdout:
                did = True
                sout.write(line)
            if not did:
                break
        proc.wait()
        exitstatus = proc.returncode
    return exitstatus


def _subcommand_which(sin, sout, serr, argv, env_stacker):
    """Which readme is being used? (per env variable 'PHO_README')"""

    prog_name = (bash_argv := list(reversed(argv))).pop()
    formals = (('-h', '--help', 'this screen'),)
    foz = formals_via(formals, lambda: prog_name)
    vals, es = foz.terminal_parse(serr, bash_argv)
    if vals is None:
        return es

    if vals.get('help'):
        return _write_help_into(serr, _subcommand_which.__doc__, foz)

    env_stack = env_stacker()
    if (readme := _resolve_readme(serr, env_stack)) is None:
        serr.write("no readme selected.\n")
        return 4

    sout.write(readme)
    sout.write('\n')
    return 0


def _subcommand_use(sin, sout, serr, argv, env_stacker):
    """Use a different readme (a shellable line. experimental)

    EXPERIMENTALLY you can try `$( pi use ./foo/bar/README.md )`
    You can get a list of available files with the `find` subcommand
    sibling to this one.
    """

    prog_name = (bash_argv := list(reversed(argv))).pop()
    formals = (('-h', '--help', 'this screen'), ('<readme>', 'path to file'))
    foz = formals_via(formals, lambda: prog_name)
    vals, es = foz.terminal_parse(serr, bash_argv)
    if vals is None:
        return es

    if vals.get('help'):
        return _write_help_into(serr, _subcommand_use.__doc__, foz)

    readme = vals['readme']
    from shlex import quote

    from os import stat
    try:
        st = stat(readme)
    except FileNotFoundError as e:
        serr.write(str(e))
        serr.write('\n')
        return e.errno
    from stat import S_ISREG
    if not S_ISREG(st.st_mode):
        serr.write(f"Not a file: {quote(readme)}. {foz.invite_line}")
        return 4
    sout.write(''.join(('export PHO_README=', quote(readme), '\n')))
    return 0


def _formals_for_graph():
    yield '-h', '--help', 'this screen'


def _subcommand_graph(sin, sout, serr, argv, env_stacker):
    """Experimental graph-viz visualization of issues..

    Use tags in your issue rows like `#after:[#123.4]` or `#part-of:[#123.4]`
    """

    prog_name = (bash_argv := list(reversed(argv))).pop()
    foz = formals_via(_formals_for_graph(), lambda: prog_name)
    vals, es = foz.terminal_parse(serr, bash_argv)
    if vals is None:
        return es

    if vals.get('help'):
        return _write_help_into(serr, _subcommand_graph.__doc__, foz)

    env_stack = env_stacker()
    if (readme := _resolve_readme(serr, env_stack)) is None:
        return 4

    mon = _error_monitor(serr)

    from pho._issues import issues_collection_via_ as func
    ic = func(readme, mon.listener)
    # ..

    from pho._issues.graph import to_graph_lines_ as func
    for line in func(ic, mon.listener):
        sout.write(line)

    return mon.exitstatus


def _write_help_into(serr, doc, foz):
    for line in foz.help_lines(doc):
        serr.write(line)
    return 0


def _build_int_matcher():
    def match(token):
        if (md := re.match('^-([1-9][0-9]*)$', token)) is None:
            return
        return int(md[1])
    import re
    return match


def _error_monitor(serr):
    from script_lib.magnetics import error_monitor_via_stderr as func
    return func(serr, default_error_exitstatus=4)


def _pass_thru_context_manager(lines):  # #[#510.12] pass-thru context manager
    class cm:
        def __enter__(_):
            return lines

        def __exit__(self, *_3):
            pass
    return cm()


def _monadic_no_op(_):
    pass


def _niladic_no_op():
    pass


def xx(msg=None):
    raise RuntimeError('write me' + ('' if msg is None else f": {msg}"))


if '__main__' == __name__:
    def enver():
        xx()
    from sys import stdin, stdout, stderr, argv
    exit(CLI(stdin, stdout, stderr, argv, enver))

# #born
