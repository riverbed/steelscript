# Copyright (c) 2021 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import sys
import itertools

from setuptools import setup, find_packages, Command
from setuptools.command.test import test as TestCommand

from gitpy_versioning import get_version


packagedata = True


class MakeSteel(Command):
    description = "Create a bootstrap steel.py script for distribution"
    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        path = 'steelscript/commands/steel.py'
        bootstrap = 'steel_bootstrap.py'
        with open(path) as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith('__VERSION__'):
                lines[i] = "__VERSION__ = '%s'" % get_version()

        with open(bootstrap, 'w') as f:
            f.writelines(lines)

        print(('{0} written.'.format(bootstrap)))


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        import shlex

        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


install_requires = [
    'requests>=2.21.0',
    'python-dateutil',
]

if sys.platform == 'win32':
    install_requires.append('pyreadline') # readline subsitute for Windows

# Additional dependencies
test = ['pytest', 'testfixtures', 'mock']
doc = ['sphinx', 'sphinx_rtd_theme']
setup_requires = ['pytest-runner']

setup_args = {
    'name':               'steelscript',
    'namespace_packages': ['steelscript'],
    'version':            get_version(),
    'author':             'Riverbed Technology',
    'author_email':       'community@riverbed.com',
    'url':                'https://community.riverbed.com',
    'license':            'MIT',
    'description':        'Core Python module for interacting with Riverbed devices',

    'long_description': '''SteelScript
===========

SteelScript is a collection of libraries and scripts in Python and JavaScript for
interacting with Riverbed Technology devices.

For a complete guide to installation, see:

http://pythonhosted.org/steelscript/
    ''',

    'platforms': 'Linux, Mac OS, Windows',

    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Networking',
    ],
    
    'python_requires': '>=3.9',

    'packages': find_packages(exclude=('gitpy_versioning', 'tests*')),

    'entry_points': {
        'console_scripts': [
            'steel = steelscript.commands.steel:run'
        ]
    },

    'install_requires': install_requires,
    'setup_requires': setup_requires,
    'extras_require': {
        'test': test,
        'doc': doc,
        'dev': [p for p in itertools.chain(test, doc)],
        'all': []
    },

    'cmdclass': {
        'mksteel': MakeSteel,
        'pytest': PyTest
    }

}

if packagedata:
    setup_args['include_package_data'] = True

setup(**setup_args)
