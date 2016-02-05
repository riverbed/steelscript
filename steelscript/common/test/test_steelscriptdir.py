# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.common import _fs as fs

import os
import shutil
import logging
import unittest
import tempfile


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)-5.5s] %(msg)s")


class SteelScriptDirTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.tmphomedir = tempfile.mkdtemp()
        os.environ['HOME'] = self.tmphomedir

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        shutil.rmtree(self.tmphomedir)

    def test_empty_default_basedir(self):
        ssdir = fs.SteelScriptDir('np', 'data')

        self.assertEqual(len(ssdir.get_files()), 0)

        tail = os.path.join('steelscript', 'np', 'data')
        self.assertTrue(ssdir.basedir.endswith(tail))
        self.assertTrue(ssdir.basedir.startswith(self.tmphomedir))

    def test_empty_basedir(self):
        ssdir = fs.SteelScriptDir('np', 'data', directory=self.tmpdir)

        self.assertEqual(len(ssdir.get_files()), 0)

        tail = os.path.join('np', 'data')
        self.assertTrue(ssdir.basedir.endswith(tail))
        self.assertTrue(ssdir.basedir.startswith(self.tmpdir))

    def test_empty_components(self):
        ssdir = fs.SteelScriptDir(directory=self.tmpdir)

        self.assertEqual(len(ssdir.get_files()), 0)
        self.assertEqual(os.path.abspath(ssdir.basedir),
                         os.path.abspath(self.tmpdir))


class SteelScriptFileTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.ssdir = fs.SteelScriptDir('np', 'data', directory=self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_empty_configfile(self):
        ssfile = self.ssdir.get_config('empty_file.txt')

        self.assertEqual(ssfile.data, None)

    def test_empty_datafile(self):
        ssfile = self.ssdir.get_data('empty_file.txt')

        self.assertEqual(ssfile.data, None)
        self.assertEqual(ssfile.version, 0)

    def test_empty_file(self):
        ssdir = fs.SteelScriptDir('np', 'data')

        self.assertEqual(len(ssdir.get_files()), 0)

        tail = os.path.join('steelscript', 'np', 'data')
        self.assertTrue(ssdir.basedir.endswith(tail))

    def test_simple_datafile(self):
        # open and create new file
        ssfile = self.ssdir.get_data('empty_file.txt')
        ssfile.read()

        self.assertEqual(ssfile.data, None)
        self.assertEqual(ssfile.version, 0)

        data = {x: x for x in range(20)}
        ssfile.data = data
        ssfile.version = 1
        ssfile.write()

        self.assertEqual(len(self.ssdir.get_files()), 1)

        # re-open file and verify contents
        ssfile = self.ssdir.get_data('empty_file.txt')
        ssfile.read()

        self.assertEqual(ssfile.data, data)
        self.assertEqual(ssfile.version, 1)
