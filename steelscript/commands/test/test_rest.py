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

from steelscript.commands.steel import shell, ShellFailed
from steelscript.commands.test.test_steel import TestSteel

class TestRest(TestSteel):

    def rest(self, lines):
        (fd, filename) = tempfile.mkstemp()
        f = os.fdopen(fd, 'w')
        for line in lines:
            f.write(line + '\n')
        f.write('quit\n')
        f.close()
        return self.shell('steel rest -f %s' % filename)

    def test_help(self):
        out = self.rest(['help'])
        self.assertTrue('Perform an HTTP GET' in out)

    def test_get(self):
        out = self.rest(['connect http://httpbin.org/',
                         'GET /get'])
        self.assertTrue('Issuing GET' in out)
        self.assertTrue('application/json' in out)
        self.assertTrue('"args": {}' in out)

    def test_get_x(self):
        out = self.rest(['connect http://httpbin.org/',
                         'GET /get x=1'])
        self.assertTrue('Issuing GET' in out)
        self.assertTrue('application/json' in out)
        self.assertTrue('"x": "1"' in out)

    def test_get_xy(self):
        out = self.rest(['connect http://httpbin.org/',
                         'GET /get x=1 y=2'])
        self.assertTrue('Issuing GET' in out)
        self.assertTrue('application/json' in out)
        self.assertTrue('"x": "1"' in out)
        self.assertTrue('"y": "2"' in out)

    def test_get_hdr(self):
        out = self.rest(['connect http://httpbin.org/',
                         'GET /get XRVBD-X:1'])
        self.assertTrue('Issuing GET' in out)
        self.assertTrue('application/json' in out)
        self.assertTrue('"Xrvbd-X": "1"' in out)

    def test_post_json(self):
        out = self.rest(['connect http://httpbin.org/',
                         'POST /post',
                         '{ "a": 1 }',
                         '.'])
        self.assertTrue('Issuing POST' in out)
        self.assertTrue('application/json' in out)
        self.assertTrue('"a": 1' in out)

    def test_post_text(self):
        out = self.rest(['connect http://httpbin.org/',
                         'mode text',
                         'POST /post',
                         '{ "a": 1 }',
                         '.'])
        self.assertTrue('Issuing POST' in out)
        self.assertTrue('application/json' not in out)
        self.assertTrue('"data": "{ \\"a\\": 1 }"' in out)

if __name__ == '__main__':
    logging.basicConfig(filename="test.log",
                        level=logging.DEBUG)
    unittest.main()
