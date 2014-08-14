#!/usr/bin/env python

import os
import sys
import time
import glob
import getpass
import optparse
import subprocess
import re
from optparse import OptionParser, OptionGroup
from threading import Thread
from functools import partial
from collections import deque
from pkg_resources import (get_distribution, iter_entry_points, parse_version,
                           DistributionNotFound, AvailableDistributions)

try:
    import importlib
    has_importlib = True
except ImportError:
    has_importlib = False

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x


import logging
if __name__ == '__main__':
    logger = logging.getLogger('steel')
else:
    logger = logging.getLogger(__name__)

try:
    __VERSION__ = get_distribution('steelscript').version
except DistributionNotFound:
    __VERSION__ = None


LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'critical': logging.CRITICAL,
    'error': logging.ERROR
}

LOGFILE = None

STEELSCRIPT_CORE = ['steelscript',
                    'steelscript.netprofiler',
                    'steelscript.netshark']

STEELSCRIPT_APPFW = ['steelscript.appfwk',
                     'steelscript.wireshark',
                     'steelscript.appfwk.business-hours']


logging_initialized = False

class ShellFailed(Exception):
    def __init__(self, returncode, output=None):
        self.returncode = returncode
        self.output = output

class MainFailed(Exception):
    pass

class _Parser(OptionParser):
    """Custom OptionParser that does not re-flow the description."""
    def format_description(self, formatter):
        return self.description


class PositionalArg(object):
    def __init__(self, keyword, help, dest=None):
        self.keyword = keyword.upper()
        self.help = help
        if dest:
            self.dest = dest
        else:
            self.dest = keyword.replace('-', '_')


class BaseCommand(object):
    """Parent class for all Command objects."""

    # The keyword to select this command, not used
    # for the root Command in a file
    keyword = None

    # Short help for this command
    help = None

    # Submodule to search for subcommands of this command
    submodule = None

    def __init__(self, parent=None):
        self.parent = parent

        if self.keyword is None:
            self.keyword = self.__module__.split('.')[-1]

        # OptionParser created when parse() called
        self.parser = None

        # Positional args
        self.positional_args = []
        self._positional_args_initialized = False

        # options and args filled in by parse()
        self.args = None
        self.options = None

        # List of subcommands
        self._subcommands = []
        self._subcommands_loaded = False

        if parent:
            self.parent._subcommands.append(self)

    def add_positional_arg(self, keyword, help, dest=None):
        self.positional_args.append(PositionalArg(keyword, help, dest=dest))

    def add_positional_args(self):
        pass

    @property
    def subcommands(self):
        # On demand, load additional subcommands from self.submodule
        # if defined.
        if not self._subcommands_loaded:
            self._subcommands_loaded = True
            if self.positional_args:
                pass
            elif self.submodule:
                self.load_subcommands()
        return self._subcommands

    def usage(self, fromchild=False):
        # Customize the usage string based on whether there are any
        # subcommands
        if self.parent:
            parentusage = self.parent.usage(True)
            if parentusage:
                base = '%s %s' % (parentusage, self.keyword)
            else:
                base = self.keyword
        else:
            base = '%prog'

        if self.positional_args:
            for p in self.positional_args:
                base = base + ' <' + p.keyword.upper() + '>'
            return '%s [options] ...' % base

        elif self.subcommands:
            if fromchild:
                return base
            return '%s [command] ...' % base
        else:
            return '%s [options]' % base

    def version(self):
        return '%s (%s)' % (__VERSION__, os.path.abspath(__file__))

    def description(self):
        # Customize the description.  If there are subcommands,
        # build a help table.
        if self.help is not None:
            lines = self.help.strip()
            desc = '\n'.join(['  ' + line for line in self.help.split('\n')]) + '\n'
        else:
            desc = ''

        def add_help_items(title, items, desc):
            help_items = [(sc.keyword,
                           (sc.help or '').split('\n')[0]) for sc in items]
            help_items.sort(key=lambda item: item[0])
            maxkeyword = max([len(sc.keyword) for sc in items])
            maxkeyword = max(10, maxkeyword)

            if desc:
                desc = desc + '\n'
            desc = desc + (
                title + ':\n' +
                '\n'.join(['  %-*s  %s' % (maxkeyword, item[0], item[1] or '')
                           for item in help_items]) + '\n')

            return desc

        if self.positional_args:
            desc = add_help_items('Required Arguments', self.positional_args, desc)

        elif self.subcommands:
            desc = add_help_items('Sub Commands', self.subcommands, desc)


        return desc

    def _load_command(self, mod):
        try:
            return mod.Command(self)
        except AttributeError:
            if str(mod.__name__) != 'steelscript.commands.steel':
                logger.warning('Module has no Command class: %s' % str(mod))
            return None
        except:
            raise

    def load_subcommands(self):
        # Look for *.py files in self.submodule and try to
        # construct a Command() object from each one.
        if not has_importlib:
            return None

        try:
            i = importlib.import_module(self.submodule)
        except ImportError:
            return

        for f in glob.glob(os.path.join(os.path.dirname(i.__file__), '*.py')):
            base_f = os.path.basename(f)

            # Always skip __init__.py and this script
            if base_f == '__init__.py' or os.path.abspath(f) == __file__:
                continue

            n = '%s.%s' % (self.submodule,
                           os.path.splitext(base_f)[0])

            i = importlib.import_module(n)

            self._load_command(i)

    def add_options(self, parser):
        add_log_options(parser)

    def parse(self, args):
        """Parse the argument list."""

        if self.parent is None:
            start_logging(args)

        if not self._positional_args_initialized:
            self._positional_args_initialized = True
            self.add_positional_args()

        # Look for subcommands, strip off and pass of
        # remaining args to the subcommands.  If there are
        # positional args, skip this step
        if (  not self.positional_args and
              len(args) > 0 and
              not args[0].startswith('-')):
            subcmds = [subcmd for subcmd in self.subcommands
                       if subcmd.keyword == args[0]]
            if subcmds:
                # Found a matching registered subcommand
                subcmds[0].parse(args[1:])
                return

        if not self.parser:
            # Create a parser
            self.parser = _Parser(usage=self.usage(),
                                  version=self.version(),
                                  description=self.description())

            self.add_options(self.parser)

        if not self.positional_args and args and not args[0].startswith('-'):
            self.parser.error('Unrecognized command: {cmd}'
                              .format(cmd=args[0]))

        (self.options, self.args) = self.parser.parse_args(args)

        if self.positional_args:
            if len(self.args) < len(self.positional_args):
                self.parser.error('Missing required argument: %s'
                                  % self.positional_args[0].keyword)

            for i, p in enumerate(self.positional_args):
                setattr(self.options, p.dest, self.args[i])

            self.args = self.args[len(self.positional_args):]

        self.validate_args()
        self.setup()
        try:
            self.main()
        except MainFailed as e:
            console(e.message, logging.ERROR)
            sys.exit(1)

    def validate_args(self):
        """Hook for validating parsed options/arguments.

        If validation fails, this function should raise an error with
        self.parser.error(msg) or raise an exception.

        If defined in a subclass, the subclass must recursively
        validate_args of the parent:

          super(<subclass>, self).setup()

        """

        pass

    def setup(self):
        """Commands to run before execution.

        If defined in a subclass, the subclass will mostly
        want to call setup() of the parent via:

          super(<subclass>, self).setup()

        This will ensure the any setup required of the parent
        classes is perfomed as well.

        """
        pass

    def main(self):
        """Body of the execution for this command.

        This is where subclasses should define the action of this
        command.  By this point all command line arguments are
        parsed and stored as attributes."""
        if self.args:
            self.parser.error('Unrecognized command: {cmd}'
                              .format(cmd=self.args[0]))
        self.parser.print_help()


class SteelCommand(BaseCommand):
    """The 'steel' command, top of all other commands."""

    keyword = 'steel'
    help = 'SteelScript commands'
    submodule = 'steelscript.commands'

    @property
    def subcommands(self):
        # In addition to looking in the submodule, look
        # for entry points labeled 'steel.commands'
        if not self._subcommands_loaded:
            super(SteelCommand, self).subcommands
            for obj in iter_entry_points(group='steel.commands', name=None):
                i = obj.load(obj)
                # See if the entry point has a Command defined
                # in __init__.py
                if hasattr(i, 'Command'):
                    self._load_command(i)
                else:
                    # If not, just create a simple command based
                    # on this submodule
                    cmd = BaseCommand(self)
                    cmd.keyword = obj.name
                    cmd.submodule = i.__name__
                    cmd.help = 'Commands for {mod} module'.format(mod=i.__name__)

        return self._subcommands


class InstallCommand(BaseCommand):

    keyword = 'install'
    help = 'Package installation'

    def add_options(self, parser):
        group = OptionGroup(parser, 'Package installation options')
        group.add_option(
            '-U', '--upgrade', action='store_true', default=False,
            help='Upgrade packages that are already installed')

        group.add_option(
            '-d', '--dir', action='store', default=None,
            help='Directory to use for installation')

        group.add_option(
            # Install packages from gitlab
            '-g', '--github', action='store_true',
            help="Install packages from github")

        group.add_option(
            # Install packages from gitlab
            '-G', '--gitlab', action='store_true',
            help=optparse.SUPPRESS_HELP)

        group.add_option(
            # Install packages from a git url
            '--giturl', action='store',
            help=optparse.SUPPRESS_HELP)

        group.add_option(
            '--develop', action='store_true',
            help='Combine with --gitlab to checkout packages')

        group.add_option(
            '-p', '--package', action='append', dest='packages',
            help='Package to install (may specify more than once)')

        # Install packages from gitlab
        group.add_option(
            '--appfwk', action='store_true',
            help='Install all application framework packages')

        group.add_option(
            '--pip-options', default='',
            help='Additional options to pass to pip')

        parser.add_option_group(group)

    def validate_args(self):
        if self.options.packages is None:
            self.options.packages = STEELSCRIPT_CORE
            if self.options.appfwk:
                self.options.packages.extend(STEELSCRIPT_APPFW)

        if self.options.develop:
            if not self.options.dir:
                console('Must specify a directory (--dir)')
                sys.exit(1)

            if self.options.upgrade:
                console('Cannot upgrade development packages, '
                        'use git directly')
                sys.exit(1)

    def main(self):
        if not is_root() and not in_venv():
            console(
                ('Running installation as user {username} may not have \n'
                 'correct privileges to install packages.  Consider \n'
                 'running as root or creating a virtualenv.\n')
                .format(username=username()))
            if not prompt_yn('Continue with installation anyway?',
                             default_yes=False):
                console('\n*** Aborting installation ***\n')

                if not check_virtualenv():
                    console('Install virtualenv:\n'
                            '$ sudo pip install virtualenv\n\n'
                            'Create a new virtual environment\n'
                            '$ virtualenv <name>\n\n'
                            'Activate the new virtal environment\n'
                            '$ source <name>/bin/activate\n\n')
                sys.exit(1)

        if self.options.giturl:
            self.install_git(self.options.giturl)

        elif self.options.gitlab:
            self.install_gitlab()

        elif self.options.github:
            self.install_github()

        elif self.options.dir:
            self.install_dir()

        else:
            self.install_pip()

    def prepare_appfwk(self):
        # Manually install django-admin-tools because it will
        # die with recent versions of pip
        shell(cmd=(('pip install {pip_options} '
                    '--allow-unverified django-admin-tools '
                    'django-admin-tools==0.5.1')
                   .format(pip_options=self.options.pip_options)),
              msg=('Installing django-admin-tools'))

        if not all([pkg_installed('numpy'), pkg_installed('pandas')]):
            import platform
            if platform.system() == 'Windows':
                console('Please install the packages `numpy` and `pandas`\n'
                        'manually using the instructions found here:\n'
                        'https://support.riverbed.com/apis/steelscript/'
                        'appfwk/install.html#detailed-installation\n')
                sys.exit(1)
            elif not exe_installed('gcc'):
                console('Unable to detect installed compiler `gcc`\n'
                        'which is required for installation of\n'
                        '`pandas` and `numpy` packages.')

                base_msg = ('The following commands should install\n'
                            'the dependencies, though they will need\n'
                            'root privileges:\n')

                if exe_installed('yum'):
                    console(base_msg +
                            '> sudo yum clean all\n'
                            '> sudo yum groupinstall "Development tools"\n'
                            '> sudo yum install python-devel\n')
                elif exe_installed('apt-get'):
                    console(base_msg +
                            '> sudo apt-get update\n'
                            '> sudo apt-get install build-essential python-dev\n')
                else:
                    console('Cannot determine appropriate package manager\n'
                            'for your OS.  Please run the `steel about -v`\n'
                            'command and post that information as a question\n'
                            'to the Splash community here:\n'
                            'https://splash.riverbed.com/community/'
                            'product-lines/steelscript\n')
                sys.exit(1)

    def install_git(self, baseurl):
        """Install packages from a git repository."""
        check_git()
        check_install_pip()
        for pkg in self.options.packages:
            if pkg_installed(pkg) and not self.options.upgrade:
                console('Package {pkg} already installed'.format(pkg=pkg))
                continue
            repo = '{baseurl}/{pkg}.git'.format(
                baseurl=baseurl, pkg=pkg.replace('.', '-'))

            if pkg == 'steelscript.appfwk':
                self.prepare_appfwk()

            if self.options.develop:
                # Clone the git repo
                outdir = os.path.join(self.options.dir, pkg.replace('.', '-'))
                shell(cmd=('git clone --recursive {repo} {outdir}'
                           .format(repo=repo, outdir=outdir)),
                      msg=('Cloning {repo}'.format(repo=repo)))

                # Install the requirements.txt
                reqfile = os.path.join(outdir, 'requirements.txt')
                if os.path.exists(reqfile):
                    shell(cmd=('pip install -r {reqfile} {pip_options} '
                               .format(reqfile=reqfile,
                                       pip_options=self.options.pip_options)),

                          msg=('Installing {pkg} requirements'.format(pkg=pkg)))

                # Now install this git repo in develop mode
                shell(cmd=('cd {outdir}; python setup.py develop'
                           .format(outdir=outdir)),
                      msg=('Installing {pkg}'.format(pkg=pkg)))
            else:
                shell(cmd=('pip install {pip_options} {upgrade}git+{repo}'
                           .format(repo=repo,
                                   upgrade=('-U --no-deps '
                                            if self.options.upgrade else ''),
                                   pip_options=self.options.pip_options)),
                      msg=('Installing {pkg}'.format(pkg=pkg)))

    def install_gitlab(self):
        """Install packages from gitlab internal to riverbed."""
        check_install_pip()
        self.install_git('https://gitlab.lab.nbttech.com/steelscript')

    def install_github(self):
        """Install packages from github.com/riverbed."""
        check_install_pip()
        self.install_git('https://github.com/riverbed')

    def install_dir(self):
        check_install_pip()
        if not self.options.dir:
            console('Must specify package directory (--dir)')
            sys.exit(1)

        for pkg in self.options.packages:
            if pkg_installed(pkg) and not self.options.upgrade:
                console('Package {pkg} already installed'.format(pkg=pkg))
                continue

            if pkg == 'steelscript.appfwk':
                self.prepare_appfwk()

            cmd = (('pip install {pip_options} {upgrade}--no-index '
                    '--find-links=file://{dir} {pkg}')
                   .format(dir=self.options.dir, pkg=pkg,
                           upgrade=('-U --no-deps' if self.options.upgrade else ''),
                           pip_options=self.options.pip_options))
            shell(cmd=cmd,
                  msg=('Installing {pkg}'
                       .format(pkg=pkg, dir=self.options.dir)))

    def install_pip(self):
        check_install_pip()
        for pkg in self.options.packages:

            if pkg_installed(pkg) and not self.options.upgrade:
                console('Package {pkg} already installed'.format(pkg=pkg))
                continue

            if pkg == 'steelscript.appfwk':
                self.prepare_appfwk()

            cmd = (('pip install {pip_options} {upgrade} {pkg}')
                   .format(pkg=pkg,
                           upgrade=('-U --no-deps' if self.options.upgrade else ''),
                           pip_options=self.options.pip_options))
            shell(cmd=cmd,
                  msg=('Installing {pkg}'
                       .format(pkg=pkg, dir=self.options.dir)))


class UninstallCommand(BaseCommand):

    keyword = 'uninstall'
    help = 'Uninstall all SteelScript packages'

    def add_options(self, parser):
        group = OptionGroup(parser, 'Package uninstall options')
        group.add_option(
            '--non-interactive', action='store_true', default=False,
            help='Remove packages without prompting for input')
        parser.add_option_group(group)

    def main(self):
        if not is_root() and not in_venv():
            console(
                ('Uninstallation as user {username} may not have \n'
                 'correct privileges to remove packages.  Consider \n'
                 'running as root or activating an existing virtualenv.\n')
                .format(username=username()))
            if not prompt_yn('Continue with installation anyway?',
                             default_yes=False):
                console('\n*** Aborting uninstall ***\n')
                sys.exit(1)

        self.uninstall()

    def uninstall(self):
        e = AvailableDistributions()
        pkgs = [x for x in e if x.startswith('steel')]
        pkgs.sort()

        if not self.options.non_interactive:
            if pkgs:
                console('The following packages will be removed:\n{pkgs}\n'
                        .format(pkgs='\n'.join(pkgs)))
                console('The `steel` command will be removed as part of this\n'
                        'operation.  To reinstall steelscript you can run\n'
                        '`pip install steelscript`, or follow an alternative\n'
                        'method described at http://pythonhosted.com/steelscript\n')

                if not prompt_yn('Continue with uninstall?', default_yes=False):
                    console('\n*** Aborting uninstall ***\n')
                    sys.exit(1)
            else:
                console('Nothing to uninstall.')

        for pkg in pkgs:
            self.remove_pkg(pkg)

    def remove_pkg(self, pkg):
        cmd = 'pip uninstall -y {pkg}'.format(pkg=pkg)
        shell(cmd=cmd, msg='Uninstalling {pkg}'.format(pkg=pkg))


def pkg_installed(pkg):
    try:
        out = shell('pip show {pkg}'.format(pkg=pkg),
                    allow_fail=True, save_output=True)
        return pkg in out
    except ShellFailed:
        return False


def exe_installed(exe):
    # linux/mac only
    try:
        shell('which {exe}'.format(exe=exe), allow_fail=True)
        return True
    except ShellFailed:
        return False


def prompt_yn(msg, default_yes=True):
    yn = prompt(msg, choices=['yes', 'no'],
                default=('yes' if default_yes else 'no'))
    return yn == 'yes'


def prompt(msg, choices=None, default=None, password=False):
    if choices is not None:
        msg = '%s (%s)' % (msg, '/'.join(choices))

    if default is not None:
        msg = '%s [%s]' % (msg, default)

    msg += ': '
    value = None

    while value is None:
        if password:
            value = getpass.getpass(msg)
        else:
            value = raw_input(msg)

        if not value:
            if default is not None:
                value = default
            else:
                print 'Please enter a valid response.'

        if choices and value not in choices:
            print ('Please choose from the following choices (%s)' %
                   '/'.join(choices))
            value = None

    return value


def add_log_options(parser):
    group = optparse.OptionGroup(parser, "Logging Parameters")
    group.add_option("--loglevel", help="log level: debug, warn, info, critical, error",
                     choices=LOG_LEVELS.keys(), default="info")
    group.add_option("--logfile", help="log file, use '-' for stdout", default=None)
    parser.add_option_group(group)


def start_logging(args):
    """Start up logging.

    This must be called only once and it will not work
    if logging.basicConfig() was already called."""

    global logging_initialized
    if logging_initialized:
        return

    logging_initialized = True

    # Peek into the args for loglevel and logfile
    logargs = []
    for i, arg in enumerate(args):
        if arg in ['--loglevel', '--logfile']:
            logargs.append(arg)
            logargs.append(args[i+1])
        elif re.match('--log(level|file)=', arg):
            logargs.append(arg)

    parser = OptionParser()
    add_log_options(parser)
    (options, args) = parser.parse_args(logargs)

    global LOGFILE
    if options.logfile == '-':
        LOGFILE = None
    else:
        if options.logfile is not None:
            LOGFILE = options.logfile
        else:
            LOGFILE = os.path.join(os.path.expanduser('~'), '.steelscript', 'steel.log')

        logdir = os.path.dirname(LOGFILE)
        if logdir and not os.path.exists(logdir):
            os.makedirs(logdir)

    logging.basicConfig(
        level=LOG_LEVELS[options.loglevel],
        filename=LOGFILE,
        format='%(asctime)s [%(levelname)-5.5s] (%(name)s) %(message)s')

    logger.info("=" * 70)
    logger.info("==== Started logging: %s" % ' '.join(sys.argv))


def try_import(m):
    """Try to import a module by name, return None on fail."""
    if not has_importlib:
        return None

    try:
        i = importlib.import_module(m)
        return i
    except ImportError:
        return None


def console(msg, lvl=logging.INFO, newline=True):
    # Log a message to both the log and print to the console
    logger.log(lvl, msg)
    m = (sys.stderr if lvl == logging.ERROR else sys.stdout)
    m.write(msg)
    if newline:
        m.write('\n')
    m.flush()


debug = partial(console, lvl=logging.DEBUG)


def shell(cmd, msg=None, allow_fail=False, exit_on_fail=True,
          env=None, cwd=None, save_output=False, log_output=True):
    """Run `cmd` in a shell and return the result.

    :raises ShellFailed: on failure

    """
    if msg:
        console(msg + '...', newline=False)

    def enqueue_output(out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    logger.info('Running command: %s' % cmd)
    proc = subprocess.Popen(cmd, shell=True, env=env, cwd=cwd, bufsize=1,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    q = Queue()
    t = Thread(target=enqueue_output, args=(proc.stdout, q))
    t.daemon = True  # thread dies with the program
    t.start()

    output = [] if save_output else None
    tail = deque(maxlen=10)

    def drain_to_log(q, output):
        stalled = False
        while not stalled:
            try:
                line = q.get_nowait()
                line = line.rstrip()
                if output is not None:
                    output.append(line)
                tail.append(line)
                if log_output:
                    logger.info('shell: %s' % line.rstrip())

            except Empty:
                stalled = True

    lastdot = time.time()
    interval = 0.002
    max_interval = 0.5
    while t.isAlive():
        now = time.time()
        if now - lastdot > 4 and msg:
            sys.stdout.write('.')
            sys.stdout.flush()
            lastdot = now
        drain_to_log(q, output)
        time.sleep(interval)
        interval = min(interval * 2, max_interval)

    t.join()
    proc.poll()
    drain_to_log(q, output)

    if proc.returncode > 0:
        if msg and not allow_fail:
            console('failed')
        logger.log((logging.INFO if allow_fail else logging.ERROR),
                   'Command failed with return code %s' % proc.returncode)

        if not allow_fail and exit_on_fail:
            console('Command failed: %s' % cmd)
            for line in tail:
                print '  ', line
            if LOGFILE:
                console('See log for details: %s' % (LOGFILE))
            sys.exit(1)
        if output is not None:
            output = '\n'.join(output)

        raise ShellFailed(proc.returncode, output)

    if msg:
        console('done')

    if save_output:
        if output:
            return '\n'.join(output)
        return ''
    return None


def username():
    try:
        return os.environ['USER']
    except KeyError:
        return os.environ['USERNAME']


def is_root():
    # detect if user has root or Administrator rights
    try:
        return os.getuid() == 0
    except AttributeError:
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() == 0
        except AttributeError:
            return False


def in_venv():
    # Check if we're in a virtualenv - only works on linux
    return 'VIRTUAL_ENV' in os.environ


def check_git():
    try:
        shell(cmd='git --version',
              msg='Checking if git is installed',
              allow_fail=True)
        return True
    except ShellFailed:
        console('no\ngit is not installed, please install git to continue',
                lvl=logging.ERROR)
        sys.exit(1)


def check_install_pip():
    try:
        out = shell('pip --version',
                    msg='Checking if pip is installed',
                    allow_fail=True, save_output=True)
        version = out.split()[1]

        if parse_version(version) < parse_version('1.4.0'):
            upgrade_pip()

        return
    except ShellFailed:
        pass

    console('no')
    shell('easy_install pip',
          msg='Installing pip via easy_install')


def upgrade_pip():
    try:
        shell('pip install --upgrade pip',
              msg='Upgrading pip to compatible version',
              allow_fail=True)
    except ShellFailed:
        console('unable to upgrade pip.  steelscript requires\n'
                'at least version `1.4.0` to be installed.',
                lvl=logging.ERROR)
        sys.exit(1)


def check_virtualenv():
    try:
        shell(cmd='virtualenv --version', allow_fail=True)
        return True
    except ShellFailed:
        return False


def run():
    # Main entry point as a script from setup.py
    # If run as a script directly

    # Create the main command
    cmd = SteelCommand()

    # Manually add commands in this module
    install = InstallCommand(cmd)
    uninstall = UninstallCommand(cmd)

    try:
        cmd.parse(sys.argv[1:])
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    run()
