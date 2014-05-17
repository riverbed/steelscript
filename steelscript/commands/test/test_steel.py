# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import os
import logging
import unittest
import tempfile
import shutil
from subprocess import CalledProcessError

from steelscript.commands.steel import shell


class TestSteel(unittest.TestCase):

    def test_help(self):
        out = shell('steel', exit_on_fail=False)
        self.assertTrue('Usage' in out)
        self.assertTrue('about' in out)

        out = shell('steel -h', exit_on_fail=False)
        self.assertTrue('Usage' in out)
        self.assertTrue('about' in out)


class TestAbout(unittest.TestCase):

    def test_about(self):
        out = shell('steel about', exit_on_fail=False)
        self.assertTrue('Installed SteelScript Packages' in out)
        self.assertFalse('Platform information' in out)

    def test_about_verbose(self):
        out = shell('steel about -v', exit_on_fail=False)
        self.assertTrue('Installed SteelScript Packages' in out)
        self.assertTrue('Platform information' in out)

        out = shell('steel about --verbose', exit_on_fail=False)
        self.assertTrue('Installed SteelScript Packages' in out)
        self.assertTrue('Platform information' in out)

    def test_about_help(self):
        out = shell('steel about -h', exit_on_fail=False)
        self.assertTrue('Usage' in out)

    def test_about_fail(self):
        with self.assertRaises(CalledProcessError):
            shell('steel about -k', exit_on_fail=False)
