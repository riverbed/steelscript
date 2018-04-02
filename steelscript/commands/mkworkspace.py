# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os
import sys
import shutil
import steelscript
from optparse import OptionGroup
from pkg_resources import (get_distribution, AvailableDistributions,
                           DistributionNotFound)

from steelscript.commands.steel import (BaseCommand, prompt, console,
                                        shell, check_git, ShellFailed)


README_CONTENT = """
This is a workspace that you can use to run pre-created example scripts,
or to create your own scripts interacting with the SteelScript packages.

To collect examples run 'python collect_examples.py.' You can also overwrite
the examples you have already collected with the '--overwrite' option.

If no examples are found, that means there are no SteelScript packages
installed with /examples in their root directory, or /examples contains no
files.
"""

COLLECT_EXAMPLES_CONTENT = """import os
from optparse import OptionParser
from steelscript.commands.mkworkspace import Command

# Parse arguments
parser = OptionParser()
parser.add_option("--overwrite",
                  action="store_true", dest="overwrite", default=False,
                  help="overwrite edited examples with collected examples")
(options, args) = parser.parse_args()

# Get the file's current directory
dirpath = os.path.dirname(os.path.realpath(__file__))
# Collect all the examples into that directory
Command.collect_examples(dirpath, options.overwrite)
"""

GITIGNORE = """
*~
*.pyc
*.swp
.DS_Store
"""


class Command(BaseCommand):
    help = 'Create new workspace for running and creating SteelScript scripts'

    def add_options(self, parser):
        group = OptionGroup(parser, 'Make workspace options')
        group.add_option('-d', '--dir', action='store',
                         help='Optional path for new workspace location')
        group.add_option('--git', action='store_true',
                         help='Initialize project as new git repo')

        parser.add_option_group(group)

    @classmethod
    def mkdir(cls, dirname):
        """Create directory if it doesn't already exist."""
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def create_file(self, dirname, filename, content):
        """Create a file according to some basic specifications."""
        fname = os.path.join(dirname, filename)
        if not os.path.exists(fname):
            console('Writing {0} file {1} ... '.format(filename, fname),
                    newline=False)
            with open(fname, 'w') as f:
                f.write(content)
            console('done.')
        else:
            console('File already exists, skipping writing the file.')

    def create_workspace_directory(self, dirpath):
        """Create a workspace directory with a readme and management script."""
        # Make directory
        console('Creating project directory %s ...' % dirpath)
        self.mkdir(dirpath)

        self.create_file(dirpath, 'README.md', README_CONTENT)
        self.create_file(dirpath, 'collect_examples.py',
                         COLLECT_EXAMPLES_CONTENT)

    def initialize_git(self, dirpath):
        """If git installed, initialize project folder as new repo."""
        try:
            check_git()
        except ShellFailed:
            return

        # we have git, lets make a repo
        shell('git init', msg='Initializing project as git repo',
              cwd=dirpath)
        fname = os.path.join(dirpath, '.gitignore')
        with open(fname, 'w') as f:
            f.write(GITIGNORE)
        shell('git add .',
              msg=None,
              cwd=dirpath)
        shell('git commit -a -m "Initial commit."',
              msg='Creating initial git commit',
              cwd=dirpath)

    @classmethod
    def collect_examples(cls, dirpath, overwrite=False):
        """Copy examples from installed steelscript packages into workspace.

        :param dirpath: The absolute path to the directory the examples
        should be copied into.
        :param overwrite: If True, all edited examples will be overwritten with
        examples found in the installed packages /examples directories.
        """
        try:
            get_distribution('steelscript')
        except DistributionNotFound:
            console("Package not found: 'steelscript'")
            console("Check the installation")
            return

        examples_root = os.path.join(sys.prefix, 'share', 'doc',
                                     'steelscript', 'examples')
        # If the packages were installed normally, examples will be located in
        # the virtualenv/share/docs/steelscript/examples and if not they will
        # be in the packages root directories in /examples
        if os.path.exists(examples_root) and os.listdir(examples_root):
            cls._cp_examples_from_docs(dirpath, overwrite)
        else:
            cls._cp_examples_from_src(dirpath, overwrite)

    @classmethod
    def _cp_examples_from_docs(cls, dirpath, overwrite):
        """Copy all examples and notebooks from the virtualenv."""
        e = AvailableDistributions()
        # Get packages with prefix steel (ex. steelscript.netshark)
        steel_pkgs = [x for x in e if x.startswith('steel')]
        # Remove the 'steelscript.' prefix
        no_prefix_pkgs = [x.split('.', 1)[1]
                          if '.' in x else x for x in steel_pkgs]
        docs_root = os.path.join(sys.prefix, 'share', 'doc', 'steelscript')

        # process examples and notebooks
        for kind in ('examples', 'notebooks'):
            root = os.path.join(docs_root, kind)
            paths = [os.path.join(root, p) for p in no_prefix_pkgs
                     if os.path.exists(os.path.join(root, p))]
            dst_paths = [os.path.join(dirpath, kind,
                                      '{}-{}'.format(cls.path_leaf(p), kind))
                         for p in paths]

            cls._cp_files(kind, paths, dst_paths, overwrite)

    @classmethod
    def _cp_examples_from_src(cls, dirpath, overwrite):
        """Copy all examples and notebooks from steelscript root dirs."""
        # Get the paths of installed packages (ex /src/steelscript-netprofiler)
        pkg_paths = [os.path.dirname(p) for p in steelscript.__path__]

        for kind in ('examples', 'notebooks'):
            paths = [os.path.join(p, kind) for p in pkg_paths
                     if os.path.exists(os.path.join(p, kind))]

            mkname = lambda x: (cls.path_leaf(x) + '-' + kind).split('-', 1)[1]
            dst_paths = [os.path.join(dirpath, kind,
                                      mkname(os.path.dirname(p)))
                         for p in paths]

            cls._cp_files(kind, paths, dst_paths, overwrite)

    @classmethod
    def _cp_files(cls, kind, src_paths, dst_paths, overwrite):
        if src_paths:
            console("Collecting {} from installed packages ... ".format(kind),
                    newline=False)

            for src, dst in zip(src_paths, dst_paths):
                cls.mkdir(dst)
                cls.copy_all(src, dst, overwrite)

            console("done")
        else:
            console("WARNING: No {} were found".format(kind))

    @classmethod
    def path_leaf(cls, path):
        """:returns the name of the last file/directory in the given path"""
        head, tail = os.path.split(path)
        return tail or os.path.basename(head)

    @classmethod
    def copy_all(cls, src_dir, dest_dir, overwrite):
        """Copy all files inside src_dir into dest_dir."""
        src_files = os.listdir(src_dir)
        if not overwrite:
            dest_files = os.listdir(dest_dir)
            src_files = list(set(src_files) - set(dest_files))

        for file_name in src_files:
            full_file_name = os.path.join(src_dir, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, dest_dir)

    def main(self):
        console('Generating new SteelScript workspace...')

        dirpath = self.options.dir
        while not dirpath:
            default = os.path.join(os.getcwd(), 'steelscript-workspace')
            dirpath = prompt('\nEnter path for workspace files',
                             default=default)

        dirpath = os.path.abspath(dirpath)
        if os.path.exists(dirpath):
            console('Workspace directory already exists, aborting.')
            return

        self.create_workspace_directory(dirpath)
        self.collect_examples(dirpath, True)
        if self.options.git:
            self.initialize_git(dirpath)

        console('\n*****\n')
        console('SteelScript workspace created.')
