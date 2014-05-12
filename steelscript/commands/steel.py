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

from pkg_resources import iter_entry_points

import logging
logger = logging.getLogger('main')
logging.basicConfig(filename='.steel.log', level=logging.DEBUG)

STEELSCRIPT_CORE = ['steelscript',
                    'steelscript-netprofiler',
                    'steelscript-netshark']

STEELSCRIPT_APPFW = ['steelscript-appfwk',
                     'steelscript-appfwk-core',
                     'steelscript-appfwk-busines-hours']


class Failed(Exception):
    pass


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
            logger.warning("Module has no Command class: %s" % str(mod))
            return None

    def load_subcommands(self):
        # Look for *.py files in self.submodule and try to
        # construct a Command() object from each one.
        i = importlib.import_module(self.submodule)
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
        self.execute()

    def execute(self):
        self.parser.print_help()


class SteelCommand(BaseCommand):
    """The 'steel' command, top of all other commands."""

    keyword = 'steel'
    help = "SteelScript commands"
    submodule = 'steelscript.commands'

    @property
    def subcommands(self):
        # In addition to looking in the submodule, look
        # for entry points labeled 'steel.commands'
        if not self._subcommands_loaded:
            super(SteelCommand, self).subcommands
            for obj in iter_entry_points(group='steel.commands', name=None):
                i = obj.load(obj)
                self._load_command(i)

        return self._subcommands


def run():
    # Main entry point as a script from setup.py
    cmd = SteelCommand()

    try:
        cmd.parse(sys.argv[1:])
    except Failed:
        sys.exit(1)

if __name__ == '__main__':
    # If run as a script directly
    run()
