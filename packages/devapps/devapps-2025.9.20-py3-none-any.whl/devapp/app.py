import json
import os
import signal
import subprocess
import sys
import time
from functools import partial

from absl import app as abslapp
from absl import flags as flags_
from devapp import gevent_patched  # noqa
from devapp import load, tools
from devapp.lib import sh
from structlogging import sl
from theming.absl_color_help import call_doc, env_hlp_exit_flg, exit_at_help_flag
from theming.colorhilite import coljhighlight

FLG = flags_.FLAGS


env = os.environ
py_env = load.py_env


def kvmsg(kw):
    return '  ' + '\n  '.join(['%s: %s' % (k, str(v)) for k, v in kw.items()])


def kvprint(l, msg, kw):
    return print('[%s] %s\n%s' % (l, msg, kvmsg(kw)))


notifier = [None]


def notify(app, msg, **kw):
    app.info('NOTIF: %s' % msg, **kw)
    if notifier[0] is None:
        notifier[0] = False
        for n in 'dunstify', 'notify-send':
            if os.system('type %s 1>/dev/null 2>/dev/null' % n) == 0:
                notifier[0] = n
                break
    if not notifier[0]:
        return
    try:
        subprocess.Popen([notifier[0], msg, '\n' + kvmsg(kw)])
    except Exception:
        pass


class App:
    """
    Placeholder for dirs and log and die function, when app is run without the framework
    e.g. in unit tests, where, in the same process later the run_app function will be
    called, for the tested code (e.g lc's test_node_red)

    Otherwise, better use init_app, when you never call run_app.
    """

    is_initted = False
    name = sys.argv[0]
    selected_action = None

    def die(self, msg, **kw):
        App().warn(msg, **kw)
        sys.exit(1)

    def info(self, msg, **kw):
        kvprint('NFO', msg, kw)

    def warn(self, msg, **kw):
        kvprint('WRN', msg, kw)

    def debug(self, msg, **kw):
        kvprint('DBG ', msg, kw)

    def error(self, msg, **kw):
        kvprint('ERR ', msg, kw)

    def fatal(self, msg, **kw):
        kvprint('DIE ', msg, kw)

    def notify(self, msg, **kw):
        notify(App, msg, **kw)

    def __repr__(self):
        return json.dumps({'DevApp': self.name})


App.dbg = App.debug

# def kvs(f):
#    d = [k for k in dir(self) if not k.startswith('_')]
#    return dict([(k, getattr(self, k)) for k in d if f(k)])

# return json.dumps(
#    {
#        'DevApp': self.name,
#        'dirs': kvs(lambda k: '_dir' in k),
#        'attrs': kvs(lambda k: not '_dir' in k),
#    },
#    indent=4,
#    default=str,
#    sort_keys=True,
# )


# this is only for being able to print it:
app = App()
named_loggers = []


def set_direct_log_methods(app):
    for k in dir(app.log):
        if k[0] != '_' and not k == 'log':
            setattr(app, k, getattr(app.log, k))
    app.dbg = app.debug
    app.log_level = app.log._logger.level


def named_logger(name=None, level=None, capp=None, ctx=None) -> App:
    """buildable before flags are parsed, will be configured only after"""
    capp = App() if capp is None else capp
    if not hasattr(app, 'log'):  # called before flags -> delay
        named_loggers.append([name, level, capp, ctx])
        return capp
    log = sl.get_logger(name, level, **(ctx or {}))
    capp.log = log
    set_direct_log_methods(capp)
    return capp


# --------------------------------------------------------------- Wrapping Apps
def set_dirs():
    """
    - sets PATH if project.root()/bin exists so that resources are found
    """
    from devapp.tools import project

    # no-fail returns None when not found
    db = project.root(no_fail=True)
    if not db:
        return
    db += '/bin'

    if db and os.path.exists(db):
        p = os.environ['PATH']
        if db + ':' not in p:
            os.environ['PATH'] = db + ':' + p


plugin = ['']


def command_name():
    return plugin[0] or sys.argv[0].rsplit('/', 1)[-1].replace('.py', '')


def set_app(name, log):
    app.log = log
    set_direct_log_methods(app)  # app.info, app.debug, ...
    [named_logger(*c) for c in named_loggers]
    app.notify = partial(notify, app)
    app.sh = sh
    # app.var_dir ...:
    set_dirs()
    # [setattr(app, k, v) for k, v in dirs(name).items()]
    # allows raise app.die(msg, **kw):

    def die(msg, silent=False, **kw):
        """Application decided to bail out"""
        if silent:
            app.fatal(msg, **kw)
            sys.exit(1)
        raise DieNow(msg, kw)

    app.die = die
    app.name = name
    app.name_clean = tools.clean_env_key(name)
    app.is_initted = True
    if load.py_env:
        app.env = load.py_env
    if load.app_mod:
        app.mod = load.app_mod

    if FLG.redir_stderr and not os.environ.get('stderr_is_redirected'):
        # we leave it to the the system, can do better than python:
        os.environ['stderr_is_redirected'] = str(FLG.redir_stderr)
        cmd = ' '.join(['"%s"' % j for j in sys.argv])
        sys.exit(os.system(cmd + ' 2>%s' % FLG.redir_stderr))


def init_app_parse_flags(*args):
    """
    An app creator for situations when we do not call run_app - i.e. in pytest
    but still want e.g. logging

    Used in test.tools.build_flow for pytest.
    """
    if hasattr(app, 'log'):
        # not twice
        return
    name = args[0]
    # initializes flags - from argv; stores parsed flags into this FlagValues object.
    # we have no sys.argv in test situations, all will be default:
    l = list(args)
    # allows this: log_level=40 pytest -xs .
    l.extend(['--environ_flags'])
    # FLG = flags.FLAGS
    FLG(l)  # <----------- Flag parsing
    # now reset their values from env
    tools.set_flag_vals_from_env()
    kw_log = {}
    sl.setup_logging(**kw_log)
    log = sl.get_logger(name)
    set_app(name, log)


running = [0]


from typing import Literal, Union

LogLevel = Union[
    Literal[
        'fatal',
        'critical',
        'error',
        'exception',
        'err',
        'warn',
        'warning',
        'info',
        'debug',
    ],
    Literal[70, 60, 50, 40, 20, 10],
]


def init_app(**kw):
    """
    Lightweight Alternative to full run_app.
    Getting log and (optional) flag features configured with a non blocking function call

    log_level: LogLevel = '20',
    log_time_fmt: Literal['ISO', 'dt', '%m-%d %H:%M:%S'] = '%m-%d %H:%M:%S',
    log_to_stdout=False,
    log_fmt: Union[ Literal['off', 'auto', 'plain', 'plain_no_colors', 'json'], Literal[0, 1, 2, 3, 4] ] = 'auto',
    log_add_thread_name=False,
    log_add_thread_name=False,
    log_thread_local_names=False,
    log_dev_match='',
    log_dev_dimm_no_match=False,
    log_dev_coljson_style='dark',
    log_dev_coljson_no_truecolor=False,
    log_dev_fmt_coljson=['json', 'payload'],
    """
    lkw = [k for k in kw if k[:4] == 'log_']
    # new dflts. still ovrwrtble by cli
    [setattr(flags_.FLAGS, k, kw.pop(k)) for k in lkw]
    if 'argv' not in kw:
        # w/o setting flags we just have 2: sl.flags and tools.appflags:
        if len(tools.have_flg_cls) > 2 or kw.get('flags'):
            # define_flags was or will be called
            kw['argv'] = sys.argv  # flag feature in use
        else:
            # when he does not use flags, sys.argv should not collide
            kw['argv'] = [sys.argv[0]]
    try:
        run_app(lambda: None, **kw)
    except SystemExit:
        if env_hlp_exit_flg in os.environ:
            raise
    return app


def run_app(
    main,
    kw_log=None,
    flags_parser=None,
    flags_validator=None,
    wrapper=None,
    flags=None,
    argv=None,
    call_main_when_already_running=False,
):
    """Starter for devapps' main functions

    Examples:
        run = lambda: run_app(build, {'log_dev_fmt_coljson': ['r']})

    flags: Optional flags class

    """

    if running[0]:
        # workaround:
        # certain tests require starting the app when already an app is running:
        if call_main_when_already_running:
            return main()
        _ = 'Repeated call of app.run_app'
        app.die(_, hint='Should call only once per proc.')

    running[0] = True

    # some callers, like plugins, pass over their flags classes, do not call define in mod
    if flags:
        tools.define_flags(flags)
    tools.rm_absl_flags()
    # that's for flags: they only understand helpfull, we want -hf <match>
    argv = argv if argv else sys.argv
    exit_at_help_flag(main, argv)

    #     if '-hf' in argv or '--hf' in argv:
    #         av = list(argv)
    #         argv.clear()
    #         [argv.append('--helpfull' if a in ['-hf', '--hf'] else a) for a in av]

    # name of app (-> logging, var, log, ...folders):
    # n = env.get('DA_CLS') or command_name()
    n = command_name()
    if not flags_parser:
        #     # setup_colorized_help(main, argv)
        flags_parser = abslapp.parse_flags_with_usage
    define_action_flags_in_cli()
    # flags_parser = wrap_flag_parser_with_action_detector(flags_parser)

    try:
        abslapp.run(
            partial(
                run_phase_2,
                name=n,
                main=main,
                kw_log=kw_log,
                flags_validator=flags_validator,
                wrapper=wrapper,
            ),
            argv=argv,
            flags_parser=flags_parser,
        )
    except Exception:
        sys.exit(1)


def define_action_flags_in_cli():
    args = sys.argv
    afs = tools.action_flags
    p = 0
    have = set()
    for a in args[1:]:
        p += 1
        if a == '--':
            return
        if a not in afs:
            continue
        if p > 1:
            pa = args[p - 1]
            pa = pa[2:] if pa.startswith('--') else pa[1:] if pa.startswith('-') else pa
            pf = FLG.__flags.get(pa)
            if pf and pf.flag_type() != 'bool':
                continue
        f = afs.get(a)
        key = f['key']
        if key in have:
            continue
        have.add(key)
        args[p] = '--' + f['key']
        # after this all subclass flags for that action are defined:
        tools.define_flags(f['flg_cls'], sub=key, parent_autoshort=f['autoshort'])
        allow_short_action_cli_args(args, p, key)
        app.selected_action = key
        # action[0] = key


def allow_short_action_cli_args(args, p, key):
    """
    make 'myaction --filename[=v]' ident to 'myaction --myaction_filename[=v]' cli
    """
    L = len(args) - 1
    while p < L:
        p += 1
        a = args[p]
        if not a[:2] == '--':
            continue
        a = a[2:].split('=', 1)
        s = f'{key}_{a[0]}'
        if s in FLG.__flags:
            args[p] = f'--{s}'
            if len(a) == 2:
                args[p] += f'={a[1]}'


# action = [0]
# def on_flag_parse_err_have_action_flag(key, af, parser):
#     p = sys.argv.index(key)
#     key = af['key']  # short to long
#     action[0] = key
#     args = list(sys.argv)
#     args[p] = '--' + key
#     tools.define_flags(af['flg_cls'], sub=key, parent_autoshort=af['autoshort'])
#     for arg in args[p + 1 :]:
#         p += 1
#         if arg.startswith('--'):
#             if arg == '--':
#                 break
#             args[p] = arg.replace('--', '--%s_' % key)
#     return parser(args)


#     for k in sys.argv[1:]:
#         if k == '--':
#             break
#         af = afg(k)
#         if k[0] != '-' and af:
#             return on_flag_parse_err_have_action_flag(k, af, parser=parser)
#     # No AF. Let crash - or leave alone, e.g. a app -a1 -- foo -a1 construct
#     sys.stderr.write(err)
#     return sys.exit(1)


class DieNow(Exception):
    # required since sys.exit will be catched - halting the app, not stopping it
    def __init__(self, msg, kw):
        self.msg = msg
        self.kw = kw


class dev_app_exc_handler(abslapp.ExceptionHandler):
    def wants(self, exc):
        return True

    def handle(self, exc):
        if type(exc) == DieNow:
            # app.die was called, we logged already:
            return  # -> silent exit, we logged already
        # Trying to return after json logging as below
        # seems to halt the app with geven sometimes:
        #    48 Sep 10 18:34:55 qtwesacs01 Expert[29848]:   File "src/gevent/greenlet.py", line 716, in gevent._greenlet.Greenlet.run
        #        (...)
        #    Sep 10 18:34:55 qtwesacs01 Expert[29848]:   File "/opt/axwifi_prod/envs/wi
        #    65 Sep 10 18:34:55 qtwesacs01 Expert[29848]:     item: T1 = heapq.heappop(sel
        #    66 Sep 10 18:34:55 qtwesacs01 Expert[29848]: IndexError: index out of range
        #    67 Sep 10 18:34:55 qtwesacs01 Expert[29848]: 2019-09-10T16:34:55Z <Greenlet "
        # so better play save and not invoke app.log when a greenlet crashes:
        raise exc
        # sentry here
        if app.is_initted:
            app.log.error('Exception. Dying now', exc=exc)
        else:
            raise exc


abslapp.install_exception_handler(dev_app_exc_handler())


class Reloaded(Exception):
    pass


reload_signal = 1


def reload_handler(signum, frame):
    app.warn('Reload!', signal=reload_signal)
    raise Reloaded('signal')


# def wrap_flag_parser_with_action_detector(flags_parser):
#     def parser(args, p=flags_parser):
#         try:
#             breakpoint()  # FIXME BREAKPOINT
#             e = sys.stderr
#             sys.stderr = StringIO()
#             r = p(args)
#             sys.stderr = e
#             return r
#         except SystemExit as ex:
#             sys.stderr, e = e, sys.stderr.getvalue()
#             return on_flag_parse_err_try_action_flags(args, err=e, parser=p)

#     return parser


# def on_flag_parse_err_try_action_flags(args, err, parser):
#     afg = tools.action_flags.get

#     for k in sys.argv[1:]:
#         if k == '--':
#             break
#         af = afg(k)
#         if k[0] != '-' and af:
#             return on_flag_parse_err_have_action_flag(k, af, parser=parser)
#     # No AF. Let crash - or leave alone, e.g. a app -a1 -- foo -a1 construct
#     sys.stderr.write(err)
#     return sys.exit(1)


# def on_flag_parse_err_have_action_flag(key, af, parser):
#     p = sys.argv.index(key)
#     key = af['key']  # short to long
#     action[0] = key
#     args = list(sys.argv)
#     args[p] = '--' + key
#     tools.define_flags(af['flg_cls'], sub=key, parent_autoshort=af['autoshort'])
#     for arg in args[p + 1 :]:
#         p += 1
#         if arg.startswith('--'):
#             if arg == '--':
#                 break
#             args[p] = arg.replace('--', '--%s_' % key)
#     return parser(args)


# action = ['']
def setup_auto_restart(dw="fd '.py' src"):
    """Start the app in a while loop"""
    current_pid = os.getpid()
    cmd = dw
    cmd += f""" | entr -p -z -n -r sh -c 'kill -TERM {current_pid}' """
    dn = subprocess.DEVNULL
    proc = subprocess.Popen(cmd, shell=True, stdout=dn, stderr=dn)
    app.info('🔍 Starting watcher', cmd=cmd, pid=proc.pid)


def run_phase_2(args, name, main, kw_log, flags_validator, wrapper):
    tools.set_flag_vals_from_env()  # 0.0001sec

    if FLG.help_call:
        # -h shows level 1:
        call_doc(main, level=2, render=True)
        return

    if FLG.help_call_detailed:
        call_doc(main, level=3, render=True)
        return

    kw_log = {} if kw_log is None else kw_log
    if flags_validator:
        try:
            err = flags_validator()
        except Exception as ex:
            err = str(ex)
        if err:
            print('Flags validation error: %s' % err, file=sys.stderr)
            sys.exit(1)
    sl.setup_logging(**kw_log)
    log = sl.get_logger(app.selected_action or name)
    set_app(name, log)
    if FLG.dirwatch:
        setup_auto_restart(FLG.dirwatch)

        # # ps wwwax |grep python |grep app | grep client | xargs kill
        # # test if tools present:
        # d, match, rec, sig, freq = (FLG.dirwatch + ':::::').split(':')[:5]
        # if not sig:
        #     sig = str(reload_signal)
        # d = os.path.abspath(d)
        # if not os.path.isdir(d):
        #     app.die('No directory:', d=d, nfo='Use <dir>:<match>[:r[:sig[:freq]]]')
        # w = os.path.dirname(os.path.abspath(__file__)) + '/utils/watch_dog.py'
        # cmd = [w, ':'.join([d, str(os.getpid()), match, rec, sig, freq])]
        # # print('pid', os.getpid())
        # app.info('watcher', cmd=' '.join(cmd))
        # watcher_pid = subprocess.Popen(cmd).pid

    res = post = None
    while True:
        try:
            if isinstance(main, type):
                main, post = handle_action_cls(app, action_cls=main)
            # so that everybody knows what is running. informational
            app._app_func = main
            # main = lambda: run_app(Action, flags=Flags, wrapper=cleanup)
            # if FLG.dirwatch:
            #     signal.signal(reload_signal, reload_handler)
            res = wrapper(main) if wrapper else main()
            # if FLG.dirwatch:
            #     app.info('Keep running, dirwatch is set')
            #     while 1:
            #         # wait for receiving watchdog signal
            #         time.sleep(10)
        except DieNow as ex:
            app.error(ex.msg, exc=ex, **ex.kw)
            raise
        except Reloaded:
            continue
        except SystemExit as ex:
            return ex.args[0]
        except KeyboardInterrupt:
            # if watcher_pid:
            #     os.kill(watcher_pid, 9)
            print('Keyboard Interrupt - Bye.')
            sys.exit(1)
        except Exception as ex:
            try:
                app.error(str(ex), exc=ex)
            except Exception as ex:
                pass
            raise
        finally:
            if post:
                # app.debug(
                #     'Post app hook', running=[p.__name__ for p in tools.to_list(post)]
                # )

                [p() for p in post] if isinstance(post, list) else post()
        break
    if not isinstance(res, (list, dict, tuple)):
        if res is not None:
            print(res)
        return
    # exit phase. postprocessing, pretty to stdout, plain to | jq .:
    if FLG.flat:
        res = tools.flatten(res, sep='.')
    f = getattr(app, 'out_formatter', 0)
    if f:
        r = f(res)
        if r:
            return
    if not sys.stdout.isatty():
        jres = json.dumps(res, default=str)
        print(jres)
    else:
        # return res
        print(coljhighlight(res))
    # abseil would print it again:
    # return res


def handle_action_cls(app, action_cls, post=None):
    # An Action class - use it:
    if not app.selected_action:
        for af in tools.action_flags.values():
            if af['flg_cls'].d:
                app.selected_action = af['key']
                app.debug('Running default action', action=af['key'])
                break
    if not app.selected_action:
        app.die('Require action. No default action is set.')
    main = getattr(action_cls, app.selected_action, None)
    if not main:
        app.die('Require action', no_found=app.selected_action)
    pre = getattr(action_cls, '_pre', 0)
    if pre:
        # app.debug('Prepare hook') - may parametrize the action func
        _ = pre()

        if _:
            main = _
    if isinstance(main, type):
        main = main.run
    post = getattr(action_cls, '_post', 0)
    return main, post


#
# class Die(Exception):
#     log = None
#
#     def __xinit__(self, msg, log=None, **kw):
#         raise DieNow(msg, kw)

# log = log or self.log
# if log:
#     log.error(msg, **kw)
# else:
#     print(
#         msg, json.dumps(kw, sort_keys=True, default=str, indent=4)[1:-1],
#     )
# breakpoint()  # FIXME BREAKPOINT
# raise DieNow()


def app_func(inner=False):
    if not inner:
        return app._app_func
    f = app._app_func
    while hasattr(f, 'func'):
        f = f.func
    return f


def do(
    func, *a, _step=[0], titelize='', log_level=None, ll=None, fl=None, store=None, **kw
):
    """When fl (full log level) is set to e.g. 10 we log only the message at higher levels"""

    if ll is not None:
        log_level = {10: 'debug', 20: 'info', 30: 'warn'}.get(ll, 'info')
    fn = func.__qualname__  # .rsplit('.', 1)[-1]
    if titelize:
        _step[0] += 1
        fn = 'STEP %s: %s' % (_step[0], fn)
    log = app.debug if func == system else app.info
    if log_level:
        log = getattr(app, log_level)

    if func == system:
        cmd, args = (a[0] + ' ').split(' ', 1)
        kwl = {} if not args else {'args': args}
        fn = 'sh: ' + cmd
        log(fn, store_log=store, **kwl)
    else:
        if fl is not None and fl < app.log_level:
            log(fn)
        else:
            if a:
                ar = a[0] if len(a) == 1 else a
                log(fn, args=ar, store_log=store, **kw)
            else:
                log(fn, store_log=store, **kw)

    return func(*a, **kw)


def system(cmd, no_fail=False):
    if isinstance(cmd, list):
        cmd = ' '.join('"%s"' % str(i) for i in cmd)
    # print('\x1b[38;5;240m', end='')
    d = ' 1>&2'
    # cat -> colors off
    fnf = '/tmp/failed_system_cmd'
    rcmd = 'echo -ne "\x1b[38;5;240m"%s; %s%s || touch "%s"; echo -ne "\x1b[0m"%s'
    rcmd = rcmd % (d, cmd, d, fnf, d)
    os.system(rcmd)

    err = False
    if os.path.exists(fnf):
        os.unlink(fnf)
        err = True
    # print('\x1b[0m', end='')
    if err:
        f = app.warn if no_fail else app.die
        f('Failed', cmd=cmd)
        return 1
    else:
        return 0


_uv = [False]


def aioloop(main, *main_args, init=True, uv=True, keep_running=False):
    """convenience function for real workers"""
    import asyncio

    os.environ['gevent_no_patch'] = 'true'
    if uv:
        try:
            import uvloop

            uvloop.install()
            _uv[0] = True

        except ImportError:
            pass
    if main_args:
        main = partial(main, *main_args)
    appmain = main

    if init:
        init_app()

        async def appmain(main=main):
            try:
                await main()
                if keep_running:
                    await asyncio.Event().wait()
            finally:
                for f in ataioexit:
                    try:
                        await f()
                    except Exception as ex:
                        print(f'ataioexit err [{f}]: {ex}', file=sys.stderr)

    try:
        asyncio.run(appmain())
    except KeyboardInterrupt:
        app.fatal('KeyboardInterrupt')


ataioexit = []
# is set into app as .die:
# allows raise app.die(msg, **kw) with correct error logging:
# we want to raise for --pdb_post_mortem
# app_die = lambda app: type('Die', (Die,), {'log': app.log})
