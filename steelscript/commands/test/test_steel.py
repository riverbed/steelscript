# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import os
import logging
import sys
import tempfile
import shutil

from steelscript.commands.steel import shell, ShellFailed

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

class TestSteel(unittest.TestCase):

    def shell(self, cmd):
        if cmd.startswith('steel' or cmd.startswith(self.steel)):
            opts=' --loglevel debug --logfile -'
        else:
            opts=''
        return shell('{cmd}{opts}'.format(cmd=cmd, opts=opts),
                     exit_on_fail=False, save_output=True)


class TestHelp(TestSteel):

    def test_help(self):
        out = self.shell('steel')
        self.assertTrue('Usage' in out)
        self.assertTrue('about' in out)

        out = self.shell('steel -h')
        self.assertTrue('Usage' in out)
        self.assertTrue('about' in out)


class TestAbout(TestSteel):

    def test_about(self):
        out = self.shell('steel about')
        self.assertTrue('Installed SteelScript Packages' in out)
        self.assertFalse('Platform information' in out)

    def test_about_verbose(self):
        out = self.shell('steel about -v')
        self.assertTrue('Installed SteelScript Packages' in out)
        self.assertTrue('Platform information' in out)

        out = self.shell('steel about --verbose')
        self.assertTrue('Installed SteelScript Packages' in out)
        self.assertTrue('Platform information' in out)

    def test_about_help(self):
        out = self.shell('steel about -h')
        self.assertTrue('Usage' in out)

    def test_about_fail(self):
        with self.assertRaises(ShellFailed):
            self.shell('steel about -k')
