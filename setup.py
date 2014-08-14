# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os
import sys

try:
    from setuptools import setup, find_packages, Command
    packagedata = True
except ImportError:
    from distutils.core import setup
    from distutils.cmd import Command
    packagedata = False

    def find_packages(where='steelscript', exclude=None):
        return [p for p, files, dirs in os.walk(where) if '__init__.py' in files]

from gitpy_versioning import get_version


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

        print '%s written.' % bootstrap


install_requires = [
    'requests>=2.1.0',
    'importlib'
]

if sys.platform == 'win32':
    install_requires.append('pyreadline') # readline subsitute for Windows


setup_args = {
    'name':               'steelscript',
    'namespace_packages': ['steelscript'],
    'version':            get_version(),
    'author':             'Riverbed Technology',
    'author_email':       'eng-github@riverbed.com',
    'url':                'http://pythonhosted.org/steelscript',
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

    'classifiers': (
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking',
    ),

    'packages': find_packages(exclude=('gitpy_versioning',)),

    'entry_points': {
        'console_scripts': [
            'steel = steelscript.commands.steel:run'
        ]
    },

    'install_requires': install_requires,

    'cmdclass': {
        'mksteel': MakeSteel,
    }

}

if packagedata:
    setup_args['include_package_data'] = True

setup(**setup_args)
