# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/reschema/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.

import os
import re
import logging
import unittest
import tempfile
import shutil
import logging
from subprocess import CalledProcessError

import steelscript.commands.steel
from steelscript.commands.steel import shell

logger = logging.getLogger(__name__)

class TestInstallGitlab(unittest.TestCase):

    def setUp(self):
        self.venv = tempfile.mkdtemp()
        self.env = {}
        current_venv = None
        for k,v in os.environ.iteritems():
            if k == 'VIRTUAL_ENV':
                current_venv = v
                continue

            elif ( 'VIRTUALENV' in k or
                   'VIRTUAL_ENV' in k or
                   k == 'PATH'):
                continue

            self.env[k] = v

        path = os.environ['PATH']
        if current_venv and current_venv in path:
            m = re.search('(.*)%s[^:]*:?(.*)' % current_venv, path)
            if m:
                path = ':'.join([e for e in m.groups() if e])
        self.env['PATH'] = path
        shell('virtualenv {venv}'.format(venv=self.venv),
              env=self.env, exit_on_fail=False)

        self.steel = os.path.abspath(
            os.path.splitext(steelscript.commands.steel.__file__)[0]) + '.py'


    def shell(self, cmd):
        return shell('source {venv}/bin/activate; {cmd}'
                     .format(venv=self.venv, cmd=cmd),
                     env=self.env, exit_on_fail=False)

    def tearDown(self):
        #shutil.rmtree(self.venv)
        pass

    def test_install_all(self):
        logger.info("--- test_install_all")
        out = self.shell('pip freeze')
        self.assertFalse('steel' in out)

        with self.assertRaises(CalledProcessError):
            out = self.shell('steel -h')

        out = self.shell('{steel} -h'.format(steel=self.steel))
        self.assertTrue('Usage' in out)

        out = self.shell('{steel} install -G'.format(steel=self.steel))
        self.assertTrue('Installing steelscript' in out)

        out = self.shell('steel -h')
        self.assertTrue('Usage' in out)

        out = self.shell('which steel')
        self.assertTrue('{venv}/bin/steel'.format(venv=self.venv) in out)

        out = self.shell('steel about')
        self.assertTrue('steelscript.netprofiler' in out)
        self.assertTrue('steelscript.netshark' in out)

    def test_install_just_steelscript(self):
        logger.info("--- test_install_just_steelscript")
        out = self.shell('pip freeze')
        self.assertFalse('steel' in out)

        out = self.shell('{steel} install -G -p steelscript'
                         .format(steel=self.steel))
        self.assertTrue('Installing steelscript' in out)

        out = self.shell('steel about')
        self.assertFalse('steelscript.netprofiler' in out)
        self.assertFalse('steelscript.netshark' in out)


if __name__ == '__main__':
    logging.basicConfig(filename='test.log', level=logging.DEBUG)
    unittest.main()
