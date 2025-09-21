# FIXME
from devapp.tools import tabulate, termwidth, action_flags, define_flags
from absl import app, flags
from xml.etree import ElementTree as ET
from inspect import signature
import textwrap
import sys
import os
import io

fixme = """
Remove all this.
If colors are important, use the xml output of --helpfull.
[2020-10-07 22:16] Done. Still due though:
This has a lot of legacy in trying to colorize functions and nested class trees help output
in sync wiht absl cli flags.
(do_action of old devapps)

Remove the bloat sooner or later...
"""

# TODO: Display use cases and detailled help attributes (see devapp/app.py flags)


def func_from_partial(f):
    while not hasattr(f, '__module__'):
        if not hasattr(f, 'func'):
            return f
        f = f.func
    return f, ''


def call_doc(obj, level=2, render=False):
    """Used by devapps.app.py for -hh and -hhh"""
    raise Exception('call_doc not implemented')
    f, kw = func_from_partial(obj)
    if type(f) == type:
        out = class_doc(f, level=level)
    else:
        out = func_doc(obj, level=level + 1)
    if len(out) < 3:
        breakpoint()  # FIXME BREAKPOINT
        if 'lambda' in out[0]:
            out.pop(0)
        mod = obj.__module__
        fn = sys.modules[mod].__file__
        out.insert(0, 'No flags defined: %s (%s)' % (mod, fn))
    out = '\n'.join(out)
    out = out.strip()
    if render:
        mdvl.render(out, header_numbering=True, header_numb_level_min=2)

    return out


def deindent(d):
    return ('\n'.join([l.strip() for l in d.splitlines()]).strip()) + '\n'


def func_doc(obj, level=1):
    f, _ = func_from_partial(obj)
    n = f.__qualname__
    if '.' in n:
        n = n.split('.', 1)[1]
    sig = str(signature(obj))

    # hack: specical case for devapp.run external process:
    # there we want to show the args of the process
    if n in ('run_exit', 'app_run_exit'):
        h = 'run: ' + (' '.join([str(i) for i in obj.args[0]]))
    else:
        h = '%s %s' % (n, str(sig).replace('*', '.'))
    r, doc = [h], f.__doc__ or ''
    if level > 1:
        r.append(deindent(doc))
    return r


def class_doc(cls, level=1, hir=0, out=None):
    hir += 1
    out = [] if out is None else out
    out.append('%s %s' % ('#' * hir, cls.__name__))
    d = getattr(cls, '__doc__')
    if d and level > 1:
        out.append(deindent(d))
    dflt_meth = getattr(cls, 'default', None)
    clss = []
    aliases = []
    funcs = []
    for k in sorted(dir(cls)):
        if k.startswith('_') or k == 'default':
            continue
        c = getattr(cls, k)
        if isinstance(c, type):
            if k != c.__name__ and c.__name__ in dir(cls):
                aliases.append([k, c.__name__])
                continue
            clss.append(c)

        elif callable(c):
            funcs.append(
                {
                    'short': '',
                    'long': k,
                    'expl': '\n'.join(func_doc(c, level=level)),
                }
            )
    # FIXME
    # add_md_list(funcs, out)
    for c in clss:
        class_doc(c, level, hir, out)
    if aliases:
        out.append('\nAliases: ' + ', '.join(['%s->%s' % (i, k) for i, k in aliases]))
    out.append('- -hh[h] to get more details about calls.')

    if hir == 1:
        return out


def module_doc(mod):
    n, d = mod.__name__, mod.__doc__
    if n == '__main__':
        n = sys.argv[0].rsplit('/', 1)[-1]
    return '# %s\n%s' % (n, d)


# --------------------------------------------------------------- -hf/--helpfull output
def term_widths(have_match):
    tw = termwidth()
    widths = dict(name=int(tw * 0.2 + 0.5), short_name=6, default=int(tw * 0.15 + 0.5))
    last = 'meaning'
    if have_match:
        widths = dict(name=25, short_name=8, meaning=0)
        last = 'default'

    widths[last] = max(0, tw - sum(widths.values()))
    widths['term'] = tw
    return widths


def term_line(line_spec, widths, have_match):
    """One line of output - have_match typically [main module name]"""
    # if 'cache' in str(line_spec) or 'filtered' in str(line_spec): breakpoint()   # FIXME BREAKPOINT
    m = line_spec
    is_action = m.get('action')
    # if is_action:
    #     breakpoint()  # FIXME BREAKPOINT
    r = []
    pos = 0
    for colmn in 'short_name', 'name', 'default', 'meaning':
        v = str(m.get(colmn)) or ''
        if v == 'None':
            v = '' if colmn == 'short_name' else "''"

        if have_match:
            v += ' '
        w = widths[colmn]
        oldpos = pos
        pos += w
        if colmn == 'meaning':
            choi = m.get('choices')
            if choi:
                v += m['opts']

                # breakpoint()   # FIXME BREAKPOINT
                # choi = ' [%s]' % ','.join(choi)
                # if have_match or len(v) + len(choi) <= w:
                #     v += col('choices') + choi

            det = m.get('details')
            if det:
                # det = ' 🗎 ' + det
                det = '\n' + det
                if have_match or len(v) + len(det) <= w:
                    v += col('details') + det
        c = colmn
        if is_action:
            if m.get('action_flag'):
                if colmn in ('short_name', 'meaning'):
                    v = '   ' + v
            elif colmn == 'default':
                v, c = 'ACTION', 'action'
                if m.get('is_default'):
                    v += '*'
                    c = 'default_action'

        if have_match:
            if colmn == 'meaning':
                r[-1] = r[-1].rstrip()
                v = '\n%s' % v  # (' ' * widths['short_name']) + v
            # else:
            #     if 0 and len(v) > w:
            #         dedented_text = textwrap.dedent(v).strip()
            #         v = textwrap.fill(
            #             dedented_text,
            #             initial_indent=' ' * oldpos,
            #             subsequent_indent=' ' * 4,
            #             width=widths['term'],
            #         )
            #         v += ' '
            #         pos = 0
        else:
            # if colmn == 'default' and 'mini' in v:
            #    breakpoint()  # FIXME BREAKPOINT
            if len(v) > w:
                if colmn in ('name', 'short_name'):
                    v = v + '\n' + ' ' * pos
                else:
                    try:
                        v = textwrap.shorten(v, width=w, placeholder='..')
                    except Exception as ex:
                        # when not even placeholder fits
                        v = v[:w]
        r.append(col(c) + v.ljust(w))
    return ''.join(r)


def to_terminal(flags, widths, match=None):
    r = [term_line(line_spec, widths, have_match=match) for line_spec in flags]
    return '\n'.join(r)


def parse_xml_help(xml_help, match, cli_actions=None):
    """parse --helpxml output of absl
    cli_actions: the action possibly given to the cli

    """

    class types:
        def do_float(c, el):
            c['default'] = float(c['default'])

        def do_bool(c, el):
            c['default'] = False if c['default'] == 'false' else True

        def do_string(c, el):
            m = c['meaning']
            c['meaning'] = m  # '\x1b1;38;5;124m%(meaning)s\x1b0;m' % c

        def do_comma_separated_list_of_strings(c, el):
            pass

        def do_string_enum(c, el):
            c['choices'] = [e.text for e in el]
            opts = '|'.join([e.text or '' for e in el if e.tag == 'enum_value'])
            c['opts'] = f'<{opts}>'
            m = c['meaning']
            if '>:' in m:  # split off the opts if given in meaning, we have them in opts
                m = m.split('>:', 1)[1]
            c['meaning'] = m

        def do_multi_string_enum(c, el):
            return types.do_string_enum(c, el)

        def do_int(c, el):
            c['default'] = int(c['default'])

    tree = ET.fromstring(xml_help)
    m, items = {}, {}
    j = {'program': tree[0].text, 'usage': tree[0].text, 'flags': m, 'actions': []}
    for fs in tree[2:]:
        f = fs
        c = {}
        for t in f:
            tn = t.tag
            c[tn] = t.text
            if tn == 'type':
                c[tn] = c[tn].replace(' ', '_')
                if not c[tn] == 'multi_string':
                    getattr(types, 'do_' + c[tn])(c, f)
                mn = c['meaning']
                # Details already set by the flag instantiation in define_flags:
                if 'Details: ' in mn:
                    c['meaning'], c['details'] = mn.split('Details: ', 1)
                break
        if match and not any([m in str(c) for m in match]):
            continue
        c.pop('current', 0)
        l = m.setdefault(c['file'], [])
        l.append(c)
        items[c['name']] = {'pos': len(l) - 1, 'mod': c['file']}

    have = set()
    # action_flags registered by flag tools at flag class parsing
    for f, af in action_flags.items():
        # if f == 'droplet_list': breakpoint()
        k = af['key']
        if k in have:
            continue
        have.add(k)
        item = items.get(k)
        if not item:
            continue  # not match
        p, mod = item['pos'] + 1, item['mod']
        modflags = m[mod]
        modflags[p - 1]['action'] = True
        modflags[p - 1]['is_default'] = af['is_default']
        # afp.append([p - 1, mod, k, True])
        # we must now, when an action is given on CLI, list also it's action flags,
        # defined within this help show module. They'll start with the action + _:
        if af in cli_actions and p < len(modflags):
            j['actions'].append(modflags[p - 1])
            f = modflags[p]
            fn = f['name']
            # mind e.g. droplet_list action and droplet_list_no_cache action:
            while fn.startswith(k + '_') and fn not in action_flags:
                j['actions'].append(f)
                f['action'] = f['action_flag'] = True
                f['action_name'] = k
                f['name'] = f['name'].split(k + '_', 1)[1]
                # if f['name'] == 'private_network': breakpoint()   # FIXME BREAKPOINT
                if p > len(modflags):
                    break
                p += 1
                f = modflags[p]
                fn = f['name']

    return j


invisible_sep = '\u2063'


def get_argv_val(k, ign_val=''):
    a = list(sys.argv)
    while a:
        v = a.pop(0)
        if v.startswith(k):
            if '=' in v:
                return v.split('=', 1)[1]
            else:
                if ign_val and a and a[0].startswith(ign_val):
                    return ''
                return a.pop(0) if a else ''


# coloring themeable,i.e. only using the base colors which themes modify:
def ansi_col(nr):
    return '\033[%sm' % nr


def col(c):
    return ansi_col(
        {
            'name': '1;33',
            'default': '0;31',
            'meaning': '0;38;5;245',
            'choices': '0;38',
            'details': '0;38;5;241',
            'short_name': '0;32',
            'action': '0;33',
            'default_action': '1;33',
        }.get(c)
    )


def color_usage(*a, main_module, full=None, **kw):
    """
    colorizes flag keys and match from --help <match>
    """
    ret = []
    d = main_module.__doc__
    if d:
        if d.lstrip().startswith('# '):
            from mdvl import mdvl

            d = mdvl.render(
                d, no_print=True, header_numbering=True, header_numb_level_min=2
            )
        ret.append('\n' + d.strip() + '\n\n')

    def add(s, end='\n', ret=ret):
        return ret.append(s + end)

    # catch the original output:
    hof = get_argv_val('--help_output_fmt')
    hof = hof if hof else 'terminal'
    match = get_argv_val('--helpfull', ign_val='--help_output_fmt')
    match = [match] if match else []
    dmn = os.environ.get('doc_module_name')
    if dmn:
        match.append(dmn)

    # -h with an action flag? Then we detail its sub flags:
    afs = []
    for k in sys.argv:
        af = action_flags.get(k)
        if af:
            define_flags(af['flg_cls'], sub=af['key'], parent_autoshort=af['autoshort'])
            afs.append(af)

    with io.StringIO() as s:
        flags.FLAGS.write_help_in_xml_format(s)
        u = s.getvalue()

    j = parse_xml_help(u, match=match, cli_actions=afs)
    program = j['program']
    all_flgs = j['flags']
    if hof != 'terminal':
        r = []
        [r.extend(v) for v in all_flgs.values()]
        add(tabulate(r, headers='keys', tablefmt=hof))
        return ret

    # only -h was given (artifically added match) but no real match - output as if
    # no match was given, the list is filtered at this point:
    if dmn and match == [dmn]:
        match = []
    match_hilite = ansi_col('1;32') + ' '.join(match) + ansi_col('0')
    j['match'] = '[matching %s]' % match_hilite if match else ''

    if match:
        n = 'All supported' if full else 'Main'
        add('%s command line flags %s:' % (n, j['match']))
    if hof != 'terminal':
        r = tabulate()

    w = term_widths(match)

    def do(fn_mod, w=w, flgs=None, program=program):
        # module headline:
        flgs = all_flgs[fn_mod] if flgs is None else flgs
        if len(all_flgs) > 1:
            add(ansi_col('1;34') + fn_mod.replace('__main__', program))
        add(to_terminal(flgs, w, match=match))

    # main_help = all_flgs.pop(main_module.__name__, [])
    # show non main module flags on helpfull:
    n = main_module.__name__
    if full:
        [do(fn_mod) for fn_mod in sorted(all_flgs) if fn_mod not in (n, 'actions')]

    if n in all_flgs:
        do(n)
    # when user has selected an action on CLI, show it last, again:
    if j.get('actions'):
        add(ansi_col('1;34') + '\nSelected Action')
        do('actions', flgs=j['actions'])

    # show main module's flags last - always:
    if not full:
        add(
            '\n\x1b[36m-hf [match string]\x1b[0m: List \x1b[36;1mALL\x1b[0m (matching) flags. E.g. -hf or -hf log.'
        )
    add('\033[0m')
    return ret


hlp_flags = {'-h': False, '--help': False, '-hf': True, '--helpfull': True}


def find_module(main):
    f, _ = func_from_partial(main)
    if f and f.__module__ != 'devapp.app':
        return sys.modules.get(f.__module__)
    return sys.modules.get('__main__')


env_hlp_exit_flg = '_exit_help_'


def exit_at_help_flag(main, argv):
    """Called always by devapp.app at runtime start"""
    full, mod = None, None
    for a in argv:
        if a in hlp_flags:
            full = hlp_flags[a]
            break
    if full is None:
        return

    mod = find_module(main)
    if argv[-1] == mod.__name__:
        # plugin_tools overwrite -h with -hf <module name>:
        full = None
    if not mod:
        print('No module for function found: %s' % main)
        sys.exit(1)
    i = argv.index(a)
    if a != '--helpfull':
        argv[i] = '--helpfull'

    h = color_usage(main_module=mod, full=full)
    print(''.join(h))
    os.environ[env_hlp_exit_flg] = 'true'
    sys.exit(0)
