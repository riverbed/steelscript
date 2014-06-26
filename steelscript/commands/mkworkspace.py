# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os
import shutil
import ntpath
import steelscript
import pkg_resources

from steelscript.commands.steel import (BaseCommand, prompt, console, debug,
                                        shell, check_git, ShellFailed)


README_CONTENT = """
This is a workspace that you can use to run pre-created example scripts,
or to create your own scripts interacting with the Steelscript modules.

To collect examples run 'python collect_examples.py.' You can also overwrite
the examples you have already collected with the '--overwrite' option.

If no examples are found, that means there are no Steelscript modules installed
with /examples in their root directory, or /examples contains no files.
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
    help = 'Create new workspace for running and creating Steelscript scripts'

    def add_options(self, parser):
        parser.add_option('-d', '--dir', action='store',
                          help='Optional path for new workspace location')
        parser.add_option('-v', '--verbose', action='store_true',
                          help='Extra verbose output')
        parser.add_option('--git', action='store_true',
                          help='Initialize project as new git repo')

    def debug(self, msg, newline=False):
        if self.options.verbose:
            debug(msg, newline=newline)

    @classmethod
    def mkdir(cls, dirname):
        """Creates directory if it doesn't already exist."""
        if not os.path.exists(dirname):
            os.mkdir(dirname)

    def create_readme(self, dirname):
        """Creates local settings configuration."""
        fname = os.path.join(dirname, 'README.md')
        if not os.path.exists(fname):
            console('Writing README file %s ... ' % fname, newline=False)
            with open(fname, 'w') as f:
                f.write(README_CONTENT)
            console('done.')
        else:
            console('Skipping local settings generation.')

    def create_workspace_directory(self, dirpath):
        """Creates workspace directory and copies/creates necessary files."""
        # Make directory
        console('Creating project directory %s ...' % dirpath)
        self.mkdir(dirpath)

        # Write README.md
        fname = os.path.join(dirpath, 'README.md')
        if not os.path.exists(fname):
            console('Writing README file %s ... ' % fname, newline=False)
            with open(fname, 'w') as f:
                f.write(README_CONTENT)
            console('done.')
        else:
            console('Skipping local settings generation.')

        # Write collect_examples.py
        fname = os.path.join(dirpath, 'collect_examples.py')
        if not os.path.exists(fname):
            console('Writing collect_examples file %s ... ' % fname, newline=False)
            with open(fname, 'w') as f:
                f.write(COLLECT_EXAMPLES_CONTENT)
            console('done.')
        else:
            console('Skipping local settings generation.')

    def initialize_git(self, dirpath):
        """If git installed, initialize project folder as new repo.
        """
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
        """Copies all examples from steelscript-*/examples into the workspace
        :param dirpath: The absolute path to the directory the examples
        should be copied into.
        :param overwrite: If True, all edited examples will be overwritten with
        examples found in the installed modules /examples directories.
        """
        try:
            dist = pkg_resources.get_distribution('steelscript')
        except pkg_resources.DistributionNotFound:
            console("Package not found: 'steelscript'")
            console("Check the installation")
            return

        console("Collecting examples from installed modules ... ", newline=False)

        pkg_paths = (os.path.dirname(p) for p in steelscript.__path__)
        example_paths = (p for p in pkg_paths if os.path.exists(os.path.join(p, 'examples')))
        new_dir = None
        for p in example_paths:
            new_dir = cls.path_leaf(p) + '-examples'
            new_dir_path = os.path.join(dirpath, new_dir)
            cls.mkdir(new_dir_path)
            cls.copy_all(os.path.join(p, 'examples'), new_dir_path, overwrite)

        console("done")
        if new_dir is None:
            console("WARNING: No examples were found")

    @classmethod
    def path_leaf(cls, path):
        """:returns the name of the last file/directory in the given path"""
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    @classmethod
    def copy_all(cls, src_dir, dest_dir, overwrite):
        """Copies all files inside src_dir into dest_dir"""
        src_files = os.listdir(src_dir)
        if not overwrite:
            dest_files = os.listdir(dest_dir)
            src_files = list(set(src_files) - set(dest_files))

        for file_name in src_files:
            full_file_name = os.path.join(src_dir, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, dest_dir)

    def main(self):
        console('Generating new Steelscript workspace...')

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
        console('Steelscript workspace created.')
