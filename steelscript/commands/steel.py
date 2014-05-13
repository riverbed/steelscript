#!/usr/bin/env python

import os
import sys
import subprocess
from subprocess import CalledProcessError
from collections import namedtuple
import optparse
from optparse import OptionParser, OptionGroup
import tempfile
import importlib
import glob
import inspect
import getpass

from pkg_resources import iter_entry_points

import logging
logger = logging.getLogger('main')
logfile = os.path.join(os.path.expanduser('~'), '.steelscript', 'steel.log')
logdir = os.path.dirname(logfile)
if not os.path.exists(logdir):
    os.mkdirs(logdir)
logging.basicConfig(filename=logfile, level=logging.DEBUG)

STEELSCRIPT_CORE = ['steelscript',
                    'steelscript.netprofiler',
                    'steelscript.netshark']

STEELSCRIPT_APPFW = ['steelscript.appfwk-core',
                     'steelscript.appfwk.business-hours']


class _Parser(OptionParser):
    """Custom OptionParser that does not re-flow the description."""
    def format_description(self, formatter):
        return self.description


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

        self._subcommands = []
        self._subcommands_loaded = False

        if parent:
            self.parent._subcommands.append(self)

    @property
    def subcommands(self):
        # On demand, load additional subcommands from self.submodule
        # if defined.
        if not self._subcommands_loaded:
            self._subcommands_loaded = True
            if self.submodule:
                self.load_subcommands()
        return self._subcommands

    def usage(self, fromchild=False):
        # Customize the usage string based on whether there are any
        # subcommands
        if self.parent:
            base = '%s %s' % (self.parent.usage(True), self.keyword)
        else:
            base = '%prog'

        if self.subcommands:
            if fromchild:
                return base
            return '%s [command] ...' % base
        else:
            return '%s [options]' % base

    def description(self):
        # Customize the description.  If there are subcommands,
        # build a help table.
        if self.help is not None:
            desc = self.help + '\n'
        else:
            desc = ''

        if self.subcommands:
            help_items = [(sc.keyword, sc.help) for sc in self.subcommands]
            help_items.sort(key=lambda item: item[0])
            maxkeyword = max([len(sc.keyword) for sc in self.subcommands])
            maxkeyword = max(10,maxkeyword)
            if desc:
                desc = desc + '\n'

            desc = desc + (
                'Sub Commands:\n\n' +
                '\n'.join(['  %-*s  %s' % (maxkeyword, item[0], item[1] or '')
                           for item in help_items]) +
                '\n')

        return desc

    def _load_command(self, mod):
        try:
            return mod.Command(self)
        except AttributeError:
            logger.warning('Module has no Command class: %s' % str(mod))
            return None
        except:
            raise

    def load_subcommands(self):
        # Look for *.py files in self.submodule and try to
        # construct a Command() object from each one.
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

            try:
                i = importlib.import_module(n)
            except ImportError:
                return None

            self._load_command(i)

    def add_args(self):
        pass

    def parse(self, args):
        def try_import(m):
            try:
                i = importlib.import_module(m)
                return i
            except ImportError:
                return None

        self.parser = _Parser(usage=self.usage(),
                              description=self.description())
        self.add_args()
        if len(args) > 0 and not args[0].startswith('-'):
            subcmds = [subcmd for subcmd in self.subcommands
                       if subcmd.keyword == args[0]]
            if subcmds:
                subcmds[0].parse(args[1:])
                return

            elif self.parent is None:
                i = (try_import('steelscript.commands.%s' % args[0]) or
                     try_import('steelscript.%s.commands' % args[0]))

                if i:
                    cmd = self._load_command(i)
                    if cmd:
                        cmd.parse(args[1:])
                        return

            elif self.submodule is not None:
                i = try_import('%s.%s' % (self.submodule, args[0]))

                if i:
                    cmd = i.Command(self)
                    cmd.parse(args[1:])
                    return

            print "Unknown command '%s'" % args[0]
            sys.exit(1)

        (self.options, self.args) = self.parser.parse_args(args)
        self.postprocess_options()
        self.execute()

    def postprocess_options(self):
        return True

    def prompt(self, msg, default=None, password=False):
        if default is not None:
            msg = '%s [%s]' % (msg, default)

        msg += ': '
        value = None

        while not value:
            if password:
                value = getpass.getpass(msg)
            else:
                value = raw_input(msg)

            if not value:
                if default:
                    value = default
                else:
                    print 'Please enter a valid response.'

        return value

    def execute(self):
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

    def add_args(self):
        group = OptionGroup(self.parser, 'Package installation options')
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
            '--branch', help='Specify a branch for git checkout')

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

        #group.add_option( '--pip-options',
        #    help='Additional options to pass to pip')

        self.parser.add_option_group(group)

    def postprocess_options(self):
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

    def execute(self):
        if self.options.gitlab:
            self.install_gitlab()

        if self.options.github:
            self.install_github()

    def pkg_installed(self, pkg):
        try:
            out = shell('pip show {pkg}'.format(pkg=pkg),
                        allow_fail=True)
            return pkg in out
        except CalledProcessError:
            return False

    def install_git(self, baseurl, branch=None):
        """Install packages from a git repository."""
        check_git()
        for pkg in self.options.packages:
            if self.pkg_installed(pkg) and not self.options.upgrade:
                console('Package {pkg} already installed'.format(pkg=pkg))
                continue
            repo = '{baseurl}/{pkg}.git'.format(
                baseurl=baseurl, pkg=pkg.replace('.','-'))
            if branch:
                baseurl = baseurl + '@' + branch

            if self.options.develop:
                outdir = os.path.join(self.options.dir, pkg)
                shell(cmd=('git clone --recursive {repo} {outdir}'
                           .format(repo=repo, outdir=outdir)),
                      msg=('Cloning {repo}'.format(repo=repo)))
                shell(cmd=('cd {outdir}; python setup.py develop'
                           .format(outdir=outdir)),
                      msg=('Installing {pkg}'.format(pkg=pkg)))
            else:
                shell(cmd=('pip install {upgrade}git+{repo}'
                           .format(repo=repo,
                                   upgrade=('-U --no-deps '
                                            if self.options.upgrade
                                            else ''))),
                      msg=('Installing {pkg}'.format(pkg=pkg)))


    def install_gitlab(self):
        """Install packages from gitlab internal to riverbed."""
        check_install_pip()
        self.install_git('https://gitlab.lab.nbttech.com/steelscript')

    def install_github(self):
        """Install packages from github.com/riverbed."""
        console('Packages not available from github.com yet, '
                'try -G/--gitlab for gitlab')
        sys.exit(1)
        check_install_pip()
        self.install_git('https://github.com/riverbed/steelscript')

    def install_dir(self):
        if not self.options.dir:
            console('Must specify package directory (--dir)')
            sys.exit(1)

        for pkg in self.options.packages:
            if self.pkg_installed(pkg) and not self.options.upgrade:
                console('Package {pkg} already installed'.format(pkg=pkg))
                continue
            cmd = (('pip install {upgrade}--no-index '
                    '--find-links=file://{dir} {pkg}')
                   .format(dir=self.options.dir, pkg=pkg,
                           upgrade=('-U ' if self.options.upgrade else '')))
            shell(cmd=cmd,
                  msg=('Installing {pkg} from {dir}'
                       .format(pkg=pkg, dir=self.options.dir)))


def console(msg, lvl=logging.INFO, newline=True):
    # Log a message to both the log and print to the console
    logger.log(lvl, msg)
    m = (sys.stderr if lvl == logging.ERROR else sys.stdout)
    sys.stderr.write(msg)
    if newline:
        sys.stderr.write('\n')
    sys.stderr.flush()


def shell(cmd, msg=None, allow_fail=False, exit_on_fail=True, env=None):
    """Run `cmd` in a shell and return the result.

    :raises CalledProcessError: on failure

    """
    if msg:
        console(msg + '...', newline=False)

    try:
        logger.info('Running command: %s' % cmd)
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                         shell=True, env=env)
        [logger.debug('shell: %s' % line) for line in output.split('\n') if line]
        if msg:
            console('done')
        return output
    except CalledProcessError, e:
        if msg and not allow_fail:
            console('failed')
        logger.log((logging.INFO if allow_fail else logging.ERROR),
                   'Command failed with return code %s' % e.returncode)

        [logger.debug('shell: %s' % line) for line in e.output.split('\n') if line]
        if exit_on_fail:
            console('Command failed: %s' % cmd)
            for line in e.output.split('\n')[-10:]:
                print '  ',line
            console('See log for details: %s' % (logfile))
            sys.exit(1)
        raise

def check_git():
    try:
        git_version = shell(cmd='git --version',
                            msg='Checking if git is installed',
                            allow_fail=True)
        return True
    except CalledProcessError:
        console('no\ngit is not installed, please install git to continue',
                lvl=logging.ERROR)
        sys.exit(1)


def check_install_pip():
    try:
        pip_version = shell('pip --version',
                            msg='Checking if pip is installed...',
                            allow_fail=True)
        return
    except CalledProcessError:
        pass

    console('no')
    shell('easy_install pip',
          msg='Installing pip via easy_install')


def run():
    # Main entry point as a script from setup.py
    cmd = SteelCommand()

    # Manually add commands in this module
    install = InstallCommand(cmd)

    try:
        cmd.parse(sys.argv[1:])
    except CalledProcessError:
        sys.exit(1)

if __name__ == '__main__':
    # If run as a script directly
    run()
