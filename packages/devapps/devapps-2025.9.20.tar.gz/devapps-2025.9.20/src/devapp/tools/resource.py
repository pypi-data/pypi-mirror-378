#!/usr/bin/env python
"""
Common API for all resources
"""
# FIXME Do this as state table! Its crying for that

import os
import sys
import json
import time
import shutil
from functools import partial
import importlib
from devapp.app import app, do, run_app, system
from devapp.tools import (
    username,
    offset_port,
    to_list as listed,
    FLG,
    sp_call,
    project,
    deindent,
    exists,
    repl_dollar_var_with_env_val,
    dirname,
    write_file,
    read_file,
)


class S:
    """state"""

    is_mamba = True
    rscs_defined = None  # from resource_list
    pkg_cmd = None
    rsc_modified = False
    name_to_func = {}
    conda_prefix = None  # env vars replaced
    fs_dir = None  # filesystem install dest
    constants = {}
    constants_z = {}  # priority of overwriting constants
    rsc_dirs = {}
    mm_binary = None


# mamba support hack
MRP = os.environ.get('MAMBA_ROOT_PREFIX')
CP = os.environ.get('CONDA_PREFIX', '').split('/envs/')[0]
if CP:
    S.is_mamba = CP == MRP
    MRP = CP

os.environ['CONDA_PREFIX'] = CP


T_unit = """
[Unit]
Description      = %(descr)s %(name)s
Wants            = network-online.target
StopWhenUnneeded = false

[Service]
Type             = simple
Environment      = INSTANCE=%(env_instance)s
ExecStart        = %(exec_start)s
KillSignal       = SIGTERM
PrivateTmp       = true
Restart          = always
RestartSec       = 5
SendSIGKILL      = yes
TimeoutStopSec   = 5
SyslogIdentifier = %(name)s
%(user)s

[Install]
WantedBy = default.target

# _MATCH_ (auto created %(ctime)s) 
"""
unit_match = 'DevApp Unit'
T_unit = T_unit.replace('_MATCH_', unit_match)


def add_const(key, val, z=0):
    """import order matters, i.e. 4A's flows file will overrule lc-py. For this we have z now"""
    # if key == 'fn_flows':
    #     breakpoint()  # FIXME BREAKPOINT
    v = S.constants.get(key)
    if v is not None:
        zhave = S.constants_z[key]
        if z < zhave:
            app.info(
                'NOT overwriting constant %s' % key,
                keeping=v,
                wanted=val,
                z=z,
                zhave=zhave,
            )
            return
        app.info('Overwriting constant %s' % key, have=v, new=val, z=z, zhave=zhave)
    S.constants[key] = val
    S.constants_z[key] = z


def constant(key, dflt=None):
    v = S.constants.get(key, dflt)
    if v is None:
        app.die('Expected constant not found', key=key)
    return v


def into(m, k, v):
    m[k] = v


environ = os.environ


def cur_prefix():
    m = MRP
    cli = os.environ.get('CONDA_PREFIX', m).split('/envs/', 1)[0]
    if not cli:
        app.die('No $CONDA_PREFIX currently set')
    return cli


def set_conda_prefix():
    """
    Resources install location, except filesystem based ones. Env vars resolved.

    Aliases:
    - local|l: <project_dir>/conda
    - default|d: $HOME/miniconda3 (default path of conda)
    - current|c: Any current conda_prefix set when running.

    Note: Installing resources outside the project keeps the project relocatable and resources reusable for other products.
    """

    cli = repl_dollar_var_with_env_val(FLG.conda_prefix)
    if not cli:
        cli = 'default'
    if cli in ('current', 'c'):
        cli = cur_prefix()
    elif cli in ('local', 'l'):
        cli = project.root() + '/conda'
    elif cli in ('default', 'd'):
        # cli = os.environ['HOME'] + '/miniconda3'
        cli = os.environ['HOME'] + '/micromamba'
        S.mm_binary = shutil.which('micromamba')
    cli = os.path.abspath(cli)
    S.conda_prefix = cli


def set_fs_dir():
    """
    Filesystem based resource location. Env vars resolved.
    Aliases:
    - local|l: <project_dir>/fs
    - default|d: $HOME/miniconda3/fs (default path of conda)
    - conda|c: Within conda_prefix/fs
    """
    cli = FLG.fs_dir or 'default'
    cli = repl_dollar_var_with_env_val(cli)
    if cli in ('local', 'l'):
        cli = project.root() + '/fs'
    elif cli in ('default', 'd'):
        cli = S.conda_prefix + '/fs'
    elif cli in ('conda', 'c'):
        cli = cur_prefix() + '/fs'
    cli = os.path.abspath(cli)
    S.fs_dir = cli


def conda_prefix():
    return S.conda_prefix or [set_conda_prefix(), S.conda_prefix][1]


class CommonFlags:
    autoshort = ''

    class install_state:
        n = 'show install state infos'
        d = False

    class conda_prefix:
        n = set_conda_prefix.__doc__
        d = MRP or 'default'

    class fs_dir:
        n = set_fs_dir.__doc__
        d = 'default'

    class log_resources_fully:
        n = 'Always output all settings of resources when logging'
        d = False


# --------------------------------------------------------------------- tools/  actions

simple_types = (bool, int, float, str, list)


def to_struct(s):
    return (to_list if s.name == 'resources' else to_dict)(s)


def to_list(rscs):
    return [to_dict(rsc) for rsc in rscs]


def to_dict(rsc):
    return {
        k: getattr(rsc, k)
        for k in dir(rsc)
        if not k.startswith('_') and isinstance(getattr(rsc, k), simple_types)
    }


# # get some nice respresentation of the rsc classes:
# class Resource(type):
#     # print the resources always fully - too much spam:
#     # __repr__ = __str__ = lambda s: json.dumps(to_struct(s), sort_keys=True, indent=2)
#     __repr__ = __str__ = (
#         lambda s: rsc_repr(s)
#         if not FLG.log_resources_fully
#         else json.dumps(to_struct(s), sort_keys=True, indent=2)
#     )


# class R(metaclass=Resource):
#     listed = classmethod(lambda s: rsc_classes(s))


# def representable(name, *bases):
#     return type(name, (R,) + bases, {'__metaclass__': Resource})


# api:
def g(rsc, key, default=''):
    return getattr(rsc, key, default)


def gf(rsc, key, default=''):
    """Get function if it was a callable"""
    v = g(rsc, key, default)
    return S.name_to_func.get('.'.join((rsc.name, v)), v)


# ------------------------------------ Setting Directories project dir and conda_prefix


def matching_resource(match, exact=False):
    if not S.rscs_defined:
        find_resource_defs()
    if exact:
        rsc = [r for r in S.rscs_defined.listed() if match == r.name]
    else:
        app.info('trying fuzzy match', match=match)
        rsc = [r for r in S.rscs_defined.listed() if match in str(to_dict(r)).lower()]
        app.debug('matches', rsc=rsc)
        if len(rsc) > 1:
            prov = to_list(g(rsc, 'provides', ''))
            rsc = [r for r in rsc if match in r.name.lower() or match in str(prov)]
            if len(rsc) > 1:
                rsc = [r for r in rsc if match == r.name or match in prov]
    if not rsc or len(rsc) > 1:
        app.die('No unique match', match=match, defined=S.rscs_defined, found=len(rsc))
    return rsc[0]


def is_fs(rsc):
    return str(g(rsc, 'pkg')).startswith('layers:')


def dir_rsc_cfg(rsc):
    """configured directory of the resource"""
    if is_no_pkg_rsc(rsc):
        return project.root() + '/bin'
    elif is_fs(rsc):
        return S.fs_dir + '/' + rsc.name
    else:
        return S.conda_prefix + '/envs/%s/bin' % (g(rsc, 'conda_env', rsc.name))


def rsc_path(rsc, verify_present=False):
    """
    Find path of resource (e.g. /home/joe/miniconda3/envs/myrsc/bin)
    Return nothing if not present

    We are intrested in the path not the file itself because we'll export it before running.
    """
    path = dir_rsc_cfg(rsc)
    if not verify_present:
        return path
    v = gf(rsc, 'verify_present')
    if v:
        return path if v(rsc=rsc, path=path) else None
    if is_no_pkg_rsc(rsc):
        return path if exists(path + '/' + rsc.name) else None
    exe = g(rsc, 'exe') or g(rsc, 'cmd')
    if not exe:
        return path if exists(path) else None
    else:
        return path if exists(path + '/' + exe) else None


def interactive():
    return '-y' if FLG.force else ''


# resources without a package (e.g. client)
def is_no_pkg_rsc(rsc):
    return g(rsc, 'pkg') is False


class Run:
    def get_full_cmd(rsc, sel):
        spec = {}
        cmd_pre = ''
        if is_no_pkg_rsc(rsc):
            f = gf(rsc, sel, sel)
            d = project.root()
        else:
            d = rsc_path(rsc, verify_present=True)
            if not d:
                # d = rsc_path(rsc, verify_present=True)
                app.die('Not installed', **to_dict(rsc))

            spec = {}
            # find a function to call:
            f = gf(rsc, sel, sel)
            if not callable(f):
                f = gf(rsc, 'run')
                if not callable(f):
                    f = gf(rsc, 'cmd')
        # else just take the command string:
        cmd = gf(rsc, 'run') or gf(rsc, sel, sel)
        if callable(f):
            spec = f(cmd=sel, rsc=rsc, pth=d, api=api())
            i = isinstance
            if i(spec, dict):
                # e.g.: export LD_...
                cmd_pre = spec.get('cmd_pre', '')
            cmd = spec if i(spec, str) else (spec or {}).pop('cmd', cmd)
            if callable(cmd):
                # cmd was a function which e.g. just changed dir:
                cmd = cmd.__name__

        # app.info('Adding PATH', path=d)
        # os.environ['PATH'] = d + ':%s' % os.environ.get('PATH')
        if cmd.startswith(':'):
            cmd = cmd[1:]
        else:
            cmd = d + '/' + cmd
        cmd = cmd_pre + cmd
        # if not cmd.split(' ')[0] == orig_cmd.split(' ')[0]:
        #     app.info('completing command', given=orig_cmd, completed=cmd)
        return cmd, spec or {}


def get_instances(rsc):
    n = rsc.name
    i = int(os.environ.get(f'{n}_instances', '0'))
    return i


settings_marker = '# Resource settings:'


class Install:
    """Install methods"""

    _ = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh'
    conda_installer_url = _

    def no_pkg(rsc):
        app.info('No package resource - no install')

    def resource(rsc):
        """Api entry: install a resource"""
        Install.requirements(g(rsc, 'req'))
        if not rsc.installed or g(FLG, 'force_reinstall', ''):
            if g(rsc, 'pkg') is False:
                install_mode = Install.no_pkg
            elif is_fs(rsc):
                install_mode = Install.FS.filesystem
            else:
                install_mode = Install.Conda.conda_env

            do(install_mode, rsc=rsc)
        else:
            app.debug('already installed', rsc=rsc.name)
        do(Install.post, rsc=rsc, ll=10)
        do(Install.write_starter_and_unit_file, rsc=rsc, ll=10)
        rsc.installed = True
        S.rsc_modified = True

    class Tools:
        def download(url, dest):
            # TODO
            cmd = 'curl "%s" -o "%s"' % (url, dest)
            do(system, cmd)
            app.info('downloaded', dest=dest)

    class FS:
        def filesystem(rsc):
            if not rsc_path(rsc, verify_present=True):
                pass
            d = S.fs_dir + '/%s' % rsc.name
            img = rsc.pkg.split('layers:', 1)[1]
            system('ops container_pull --repo "%s" --dir "%s.img"' % (img, d))
            s = '--skip_filesystem_adaptions'
            system('ops container_build --dirs "%s.img" --target_dir "%s" %s' % (d, d, s))

    def write_unit_file(name, fn, rsc, instance):
        pn = project.root().rsplit('/', 1)[-1]
        name = exported_name(rsc, name)

        inst_name = f'{name}-{instance}' if instance else name
        user = ''
        ddest = dh = os.environ['HOME'] + '/.config/systemd/user'
        exec = fn
        if FLG.create_system_units:
            # here we cannot write directly, will os.system(mv) it after write:
            dh = '/etc/systemd/system'
            user = f'User             = {username()}'
            # selinux only accepts bin files in certain places!
            exec = '/usr/local/bin/' + '__'.join(fn.split('/')[1:])
        m = {
            'name': inst_name,
            'descr': '%s %s ' % (g(rsc, 'n', inst_name), pn),
            'ctime': time.ctime(),
            'exec_start': exec,
            'env_instance': instance if instance else '',
            'user': user,
        }
        if not exists(dh):
            app.info('creating systemd user dir', dir=dh)
            os.makedirs(dh)

        n_svc = '%s-%s.service' % (inst_name, pn)
        sfndest = ddest + '/' + n_svc
        sfnh = dh + '/' + n_svc
        unit = T_unit % m
        have = read_file(sfnh, dflt='')
        if unit.split('WantedBy', 1)[0] != have.split('WantedBy', 1)[0]:
            os.environ['unit_file_changed'] = '1'
            write_file(sfndest, unit)
            app.info('have written unit file', fn=sfndest)
            if FLG.create_system_units:
                app.info(f'Will now try move it to {dh}')
                r = sp_call('mv', sfndest, sfnh, as_root=True, get_all=True)

                def Die(what, d, r):
                    return app.die(
                        f'Could not move {what} file',
                        wanted_dest=d,
                        json=r,
                        hint='sudo password problem?',
                        silent=True,
                    )

                Die('unit', sfnh, r) if r['exit_status'] != 0 else 0
                # selinux only accepts bin files in certain places!
                app.info('Moving to /usr/local/bin', fn=fn, exec=exec, hint='selinux...')
                r = sp_call('mv', fn, exec, as_root=True, get_all=True)
                Die('bin wrapper', exec, r) if r['exit_status'] != 0 else 0
                app.info('symlinking', fn=fn, exec=exec)
                os.system(f'ln -s "{exec}"  "{fn}"')

        else:
            app.info('unit file unchanged', fn=sfnh)
        return n_svc

    def write_starter_and_unit_file(rsc):
        env = os.environ
        env['d_conf'] = project.root() + '/conf'
        env['d_bin'] = project.root() + '/bin'

        def write(cmd, fcmd, spec, instance=0, scmds=[]):
            def env_settings_info_for_start_wrapper(rsc):
                e = os.environ.get
                r = ''
                for ek in g(rsc, 'environ', ()):
                    n = f'{rsc.name}_{ek}'
                    v = e(n)
                    if v:
                        v = v.replace("'", "\\'")
                        r += f'  {n}={v}\n'
                if r:
                    r = 'With Env:\n' + r
                return r

            # if cmd == 'dot':
            #    breakpoint()  # FIXME BREAKPOINT
            if isinstance(spec, str):
                spec = {}
            app.debug('writing bin/' + cmd, cmd=fcmd)
            pre_exec = spec.pop('pre_exec', '')
            spec_env = spec.pop('env', {})
            fn_name = exported_name(rsc, cmd)
            fn = project.root() + '/bin/%s' % fn_name
            have = read_file(fn, '')
            marker = '-AUTOCREATED- '
            if have and len(have.split(settings_marker)[0].split('\n' + marker, 1)) == 1:
                return app.warn(
                    'Skipping write of starter file, marker was manually removed',
                    fn=fn,
                    marker=marker,
                )
            call = sys.argv[0]
            args = ' '.join(sys.argv[1:])
            if call.endswith('/ops'):
                call = call.rsplit('/', 1)[-1] + ' ' + args
            else:
                call = call + '\\\n' + args
            i = rsc
            D = '\n'.join([f'# {l}' for l in rsc.doc.splitlines()]) or ''
            r = [
                '#!/usr/bin/env bash',
                D,
                '# Delete line containing "%s" to avoid overwrites of this file by next resource install.'
                % marker,
                "_='%s" % time.ctime(),
                marker,
                '%s' % call,
                env_settings_info_for_start_wrapper(rsc),
                "'",
            ]
            add = r.append
            if g(rsc, 'systemd', None) is True:
                rsc.systemd = cmd
            units = g(FLG, 'init_create_unit_files', [])
            if g(FLG, 'init_create_all_units'):
                units.extend(listed(g(rsc, 'systemd', None)))
            has_unit = False
            sudo = ''
            typ = '--user '
            if FLG.create_system_units:
                sudo = 'sudo '
                typ = ''
            if any([u for u in units if u == cmd]):
                has_unit = True
                n_svc = Install.write_unit_file(cmd, fn, rsc, instance)
                scmd = f'{sudo}systemctl {typ}--no-pager ${{*:-}} "{n_svc}"'
                jcmd = f'{sudo}journalctl {typ}-u "{n_svc}"'
                if instances:
                    jcmd = jcmd.rsplit('-', 1)[0] + '-\\*.service"'  # wildcard
                    _ = f'\n        {sudo}systemctl {typ}--no-pager ${{*:-}} "{n_svc}"'
                    scmds.append(_)  # adding one more per loop
                    scmd = ''.join(scmds)

                s = """

                case "${1:-}" in
                    start|restart|stop|status)
                        set -x
                        _CMD_
                        exit $?
                        ;;
                    j)
                        shift && set -x
                        _JCMD_ "$@"
                        exit $?
                        ;;
                esac
                """
                s = s.replace('_CMD_', scmd).replace('_JCMD_', jcmd)
                add(deindent(s))

            # env['PATH'] = '%s:$PATH' % g(rsc, 'path')
            add('')
            add("H='__HOME__'")
            add('export PROJECT_ROOT="%s"' % project.root())
            add('# set e.g. in unit files:')
            add('test -n "$INSTANCE" && inst_postfix="-$INSTANCE" || inst_postfix=""')
            add('')
            add(settings_marker)
            # for whoever needs that:
            allk = set()
            for m in to_dict(rsc), spec, spec_env:
                for k, v in sorted(m.items()):
                    if k in {'cmd_pre', 'doc'}:
                        continue
                    allk.add(k)
                    if k == 'port':
                        v = offset_port(v)
                    exp = 'export ' if m == env else ''
                    add('%s%s="%s"' % (exp, k, str(v)))
            add('')
            if 'logdir' not in allk:
                add('export logdir="$PROJECT_ROOT/log"')
            if 'logfile' not in allk:
                add('export logfile="$logdir/%s$inst_postfix.log"' % cmd)

            add('')
            # only for services. Tools not: (e.g. cd mydir && git status -> bum, differentdir)
            if has_unit:
                add('builtin cd "$PROJECT_ROOT"')
            # for client but also possibly other python resources:
            env['PYTHONPATH'] = env.get('PYTHONPATH', '')
            add('export PYTHONPATH="%(d_conf)s:%(PYTHONPATH)s"' % env)
            # to just call w/o virtenv activation:
            # we remove all d_bin refs and put them to the end, to avoid circulars,
            # e.g. for npm - find it first in conda env
            d, p = env['d_bin'], env['PATH']
            for k in ':', '':
                p = p.replace(d + k, '')
            p += ':' + d
            add('export PATH="$path:%s"' % p)
            add('')
            _ = '$PROJECT_ROOT/.creds_$bin_name'
            add(f'test -e "{_}" && {{ set -a && . "{_}" && set +a; }}')
            add('return 2>/dev/null # when sourced\n')

            if pre_exec:
                for c in listed(pre_exec):
                    add(c)
                add('')
            postproc = g(FLG, 'add_post_process_cmd', '')
            if not has_unit:
                postproc = ''
            add('%s "$@" %s\n\n' % (fcmd, postproc))

            h = os.environ['HOME']
            s = '\n'.join(r).replace(h, '$H').replace('__HOME__', h)

            if have and have.split(marker, 1)[-1] == s.split(marker, 1)[-1]:
                app.debug('No change', cmd=cmd)
            else:
                write_file(fn, s, chmod=0o755)

        for cmd in rsc_cmds(rsc):
            fcmd, spec = Run.get_full_cmd(rsc, cmd)
            cmd = cmd.rsplit('/', 1)[-1]  # /usr/bin/seagull -> bin/seagull
            instances = get_instances(rsc)
            if not instances:
                write(cmd, fcmd, spec)
            else:
                scmds = []
                for i in range(instances):
                    write(cmd, fcmd, spec, instance=i + 1, scmds=scmds)

    def requirements(req):
        if not req:
            return
        app.info('Installing requirements', req=req)
        for r in to_list(req):
            rsc = matching_resource(r, exact=True)
            Install.resource(rsc)

    class Conda:
        def conda_env(rsc):
            D = S.conda_prefix

            # return False if not dp else all([exists(dp + '/' + p) for p in rsc.provides])
            if not exists(D):
                app.warn('Micromamba not fully installed')
                do(Install.Conda.base, location=D)

            if str(rsc.path).startswith(D):
                return app.debug('already installed - skipping', rsc=rsc)

            env = g(rsc, 'conda_env', rsc.name)
            ctx = dict(mm_binary=S.mm_binary, D=D, name=env, yes=interactive())
            for fn in 'micromamba', 'mamba':
                fn = f'{D}/etc/profile.d/{fn}.sh'
                if os.path.exists(fn):
                    ctx['shfile'] = fn

            mamba = os.environ.get('MAMBA_EXE')
            # if os.system('type micromamba') == 0 or 1:
            if S.is_mamba and mamba and MRP:
                ctx['conda'] = mamba
                # The activate during docker build is a problem in micromamba which runs as subprocess
                cmd = [
                    '%(conda)s create %(yes)s -n "%(name)s"',
                    f'. "{MRP}/etc/profile.d/micromamba.sh"',
                    'micromamba activate "%(name)s"',
                ]
                # in mamba containers we don't have the .sh file
                # os.system in python often sees not bash but a minimal shell only
                if not exists(f'. "{MRP}/etc/profile.d/micromamba.sh"'):
                    cmd[1] = f'eval "$("{mamba}" shell hook --shell=dash)"'

            elif S.is_mamba and mamba:
                ctx['conda'] = mamba
                cmd = [
                    '%(conda)s create %(yes)s -n "%(name)s"',
                    'eval "$(%(conda)s shell hook --shell=bash)"',
                    '%(conda)s activate "%(name)s"',
                ]
            else:
                assert ctx.get('shfile'), 'micromamba not fully installed'

                if not S.mm_binary:
                    app.die('Need a working micromamba install')
                ctx['conda'] = 'micromamba'
                cmd = [
                    'export MAMBA_EXE=%(mm_binary)s',
                    'export MAMBA_ROOT_PREFIX=%(D)s',
                    '. %(shfile)s',
                    '%(conda)s create %(yes)s -n "%(name)s"',
                    '%(conda)s activate "%(name)s"',
                ]
            ctx['conda'] = ctx.get('conda', 'conda')
            pth = '%(D)s/envs/%(name)s/bin/' % ctx

            if g(rsc, 'typ') == 'pip':
                ctx['cmd'] = rsc.cmd
                cmd += [
                    '%(conda)s install -c conda-forge python; %p/pip install %%(cmd)s'
                    % pth
                ]
            else:
                icmd = g(rsc, 'conda_inst', '')
                if icmd:
                    cmd += [icmd]
                else:
                    p = g(rsc, 'conda_pkg') or g(rsc, 'pkg') or ' '.join(rsc.provides)
                    chan = g(rsc, 'conda_chan', '')
                    if chan:
                        chan = '-c ' + chan
                    ctx['chan'] = chan
                    ctx['pkg'] = p
                    cmd += ['%(conda)s install %(yes)s -c conda-forge %(chan)s %(pkg)s']
            cmd = ' && '.join(cmd) % ctx
            rsc.path = g(rsc, 'path') or pth

            # app.info('cmd', cmd=cmd)
            # import subprocess
            # s = subprocess.run(cmd, shell=True, executable='/bin/bash')
            # will run under dash, sh, bash -> problem e.g. for conda activate
            return do(system, cmd)

        def base(location):
            if not FLG.force:
                q = 'Confirm: Install micromamba at %s? [y/N]'
                if not input(q % location).lower() == 'y':
                    app.die('unconfirmed')
            raise NotImplemented(
                'https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html#homebrew'
            )
            # fn = os.environ['HOME'] + '/install_miniconda.sh'
            # url = Install.conda_installer_url
            # if not exists(fn):
            #     Install.Tools.download(url, fn)
            # if not exists(fn):
            #     app.die('download failed', fn=fn)
            # os.system('chmod +x "%s"' % fn)
            # os.makedirs(os.path.dirname(location), exist_ok=True)
            # do(system, '%s -b -p "%s"' % (fn, location))

    def post(rsc):
        pf = gf(rsc, 'post_inst')
        if not pf:
            return
        # when post_inst_verify is True they have been installed. When not present there are none:
        if g(rsc, 'post_inst_verify') and not g(FLG, 'force_reinstall'):
            return

        if callable(pf):
            app.info('postinstall function', name=rsc.name)
            # they may be requirements for the post install as well:
            Install.requirements(gf(rsc, 'post_inst_req'))
            # run it:
            pth, here = environ['PATH'], os.getcwd()
            try:
                if rsc.path.endswith('/bin'):
                    environ['PATH'] = rsc.path + ':' + pth
                res = pf(rsc, install=True, api=api())
            finally:
                os.chdir(here)
                environ['PATH'] = pth

            # Usually pf installs - except Exception:
            # special case for tools, it has not a single cmd but a list of provides.
            # no cmd -> not yet install_conda_env was run. we do it now via this conventin:
            if res == 'install_conda_env':
                return Install.Conda.conda_env(rsc)
        else:
            app.die('Unsupported postinstall method', method=pf)


def rsc_cmds(rsc):
    r = []
    cmd = g(rsc, 'exe') or g(rsc, 'cmd')
    if cmd:
        r.append(cmd)
    for p in g(rsc, 'provides', ()):
        r.append(p)
    return r


def api():
    from devapp.tools import resource as api

    return api


def check_installed(rscs):
    """Sets the installed flag"""

    def check_installed_path(rsc):
        rsc.path = rsc_path(rsc, verify_present=True) or False

    def check_post_installed(rsc):
        # funnily we cannot import this module there, hash(S) is different then :-/
        # guess because of dynamic imports / freezing. So we pass ourselves over:
        cp = gf(rsc, 'post_inst')
        if callable(cp):
            res = cp(rsc, verify=True, api=api())
            rsc.post_inst_verify = res
        elif cp:
            raise NotImplementedError

    for rsc in listed(rscs):
        d = partial(do, rsc=rsc, ll=10)
        # if g(rsc, 'pkg') == False:
        #     rsc.installed = False
        #     continue
        d(check_installed_path)
        d(check_post_installed)

        rsc.installed = bool(rsc.path and g(rsc, 'post_inst_verify', 'y'))


add_install_state = check_installed


def find_resources_files_in_sys_path():
    files = {}

    def find_file_in_pth(pth, d, files=files):
        fn = '%s/%s/operations/resources.py' % (pth, d)
        if exists(fn) and d not in files:
            files[d] = fn
            S.rsc_dirs[fn] = pth + '/' + d

    def find_files_in_sys_path(pth):
        [find_file_in_pth(pth, d) for d in os.listdir(pth)]

    [find_files_in_sys_path(pth=pth) for pth in sys.path if os.path.isdir(pth)]
    return files


def doc(rsc, d=''):
    for r in rsc.mro():
        d = g(r, '__doc__', '')
        if d:
            return d
    return d


def complete_attrs(rsc):
    fn = rsc._filename

    def to_name(rsc, p):
        if callable(p):
            n = p.__name__
            S.name_to_func['.'.join((rsc.name, n))] = p
            return n
        return p

    def repl_callable(rsc, k, v):
        listed_attrs = ['provides']  # allow to say provides= npm
        if isinstance(v, list):
            vn = [to_name(rsc, i) for i in v]
        else:
            vn = to_name(rsc, v)
        if k in listed_attrs and not isinstance(vn, list):
            vn = [vn]
        if vn != v:
            setattr(rsc, k, vn)

    rsc.doc = doc(rsc)
    rsc.name = rsc.__name__
    rsc.bin_name = exported_name(rsc)
    rsc.module = rsc.__module__.replace('.operations.resources', '')
    rsc.__repr__ = lambda r: str(to_dict(r))
    rsc.__str__ = lambda r: to_str(r)
    rsc.module_dir = S.rsc_dirs[fn]
    rsc.host_conf_dir = '$PROJECT_ROOT/conf/${host:-$HOSTNAME}/' + exported_name(rsc)
    rsc.disabled = g(rsc, 'disabled', g(rsc, 'd', False))
    rsc.installed = g(rsc, 'installed', False)
    [repl_callable(rsc, k, getattr(rsc, k)) for k in dir(rsc) if not k.startswith('_')]


def exported_name(rsc, d=None):
    return os.environ.get(f'{rsc.name}_name', d if d else rsc.name)


def to_str(rsc):
    svc = g(rsc, 'systemd')
    i = 'i' if g(rsc, 'installed') else ' '
    d = 'd' if rsc.disabled else ' '
    s = 's' if svc else ' '
    n = svc if svc else rsc.name
    return '%s %s %s %s %s' % (s, i, d, n, g(rsc, 'provides', ''))


def rsc_repr(rsc):
    return rsc.name + ('[i]' if g(rsc, 'installed', '') else '')


# ------------------------------------------------------------------------    API entry
def find_resource_defs(_have_mod={}):
    """

    Delivers back a list of resources with unique classnames, i.e. w/o parents of same name

    (class mysql of 4A overwrites mysql of python)

    Identical ones are also possible and are removed:

        class rsc(other_rsc):
            pass


    """
    set_conda_prefix()
    set_fs_dir()
    m = {}
    for k in 'fs_dir', 'conda_prefix':
        f, s = g(FLG, k), g(S, k)
        m[k] = s if f == s else '%s(%s)' % (s, f)
    app.info('Directories', **m)

    rsc_files = find_resources_files_in_sys_path()

    def rsc_classes(rsc_cls_of_resources_module):
        """rscs is class rsc (with resource classes as attrs"""
        _ = rsc_cls_of_resources_module
        rsc_clses = [g(_, k) for k in dir(_) if not k.startswith('_')]
        rsc_clses = [r for r in rsc_clses if isinstance(r, type)]
        return rsc_clses

    rscs = []

    def find_cls_in_pth(d, fn, rscs=rscs):
        try:
            n_mod = '%s.operations.resources' % d
            if n_mod in _have_mod:
                app.info('%s' % n_mod, conflict=fn, taken=_have_mod[n_mod])
                return
            _have_mod[n_mod] = fn
            mod = importlib.import_module(n_mod)
        except Exception as ex:
            return app.error('Cannot import', package=n_mod, fn=fn, exc=ex)
        mod.rsc._package = d
        mod.rsc._filename = fn

        rsc_clses = rsc_classes(mod.rsc)
        for r in rsc_clses:
            r._filename = fn
            r.module = r.__module__.replace('.operations.resources', '')

        rscs.extend(rsc_clses)

    {find_cls_in_pth(d, fn) for d, fn in rsc_files.items()}

    def remove_redefined_rscs(rscs=rscs):
        # this removes the identical ones:
        all = set(rscs)
        # assert len(all) == len(rscs)
        for r in all:
            for p in r.mro()[1:]:
                if p in all:
                    n = p.__name__
                    d = {'redefined by': r.module, 'was': p.module + '.' + n}
                    app.info('Resource redefined: %s' % n, **d)
                    rscs.remove(p)

        i, j = len(all), len(rscs)
        if i > j:
            app.info('%s resources redefined' % (i - j))

    remove_redefined_rscs()

    [complete_attrs(r) for r in rscs]
    # remove dubs (through class rsc(other_rsc))
    rscs = set(rscs)
    # sort by name:
    rscs = sorted([r for r in rscs], key=lambda x: x.name)
    # now we make singletons for __repr__ w/o metaclass hacks
    rscs = [r() for r in rscs]
    for k in rscs:
        app.debug(k.name, **to_dict(k))
    S.rscs_defined = rscs
    return rscs
