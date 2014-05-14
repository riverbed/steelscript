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

class TestVirtualEnv(unittest.TestCase):

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


class TestInstallGitlab(TestVirtualEnv):

    def test_install_all(self):
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
        out = self.shell('pip freeze')
        self.assertFalse('steel' in out)

        out = self.shell('{steel} install -G -p steelscript'
                         .format(steel=self.steel))
        self.assertTrue('Installing steelscript' in out)

        out = self.shell('steel about')
        self.assertFalse('steelscript.netprofiler' in out)
        self.assertFalse('steelscript.netshark' in out)

    def test_install_develop(self):
        out = self.shell('pip freeze')
        self.assertFalse('steel' in out)

        # Install just 'steelscript' as a developer
        outdir = os.path.join(self.venv, 'src')
        out = self.shell(('{steel} install -G -p steelscript --develop '
                          '--dir {dir}')
                          .format(steel=self.steel, dir=outdir))
        self.assertTrue('Installing steelscript' in out)

        # Verify netprofiler is not installed
        out = self.shell('steel about')
        self.assertFalse('steelscript.netprofiler' in out)

        # Verify that an attempt to upgrade fails
        with self.assertRaises(CalledProcessError):
            out = self.shell(('{steel} install -G -p steelscript -U --develop '
                              '--dir {dir}')
                             .format(steel=self.steel, dir=outdir))

        # Install the rest of core packages, steelscript should be detected
        # as already installed
        out = self.shell(('{steel} install -G --develop --dir {dir}')
                          .format(steel=self.steel, dir=outdir))
        self.assertTrue('Package steelscript already installed' in out)
        self.assertTrue('Installing steelscript.netprofiler' in out)

        pkgdir = os.path.join(self.venv, 'pkgs')
        self.shell('mkdir {pkgdir}'.format(pkgdir=pkgdir))

        # Create distributions
        for pkg in steelscript.commands.steel.STEELSCRIPT_CORE:
            srcdir = os.path.join(outdir, pkg)
            out = self.shell('cd {srcdir}; python setup.py sdist'
                             .format(srcdir=srcdir))
            # Uninstall this pkg
            out = self.shell('pip uninstall -y {pkg}'.format(pkg=pkg))
            out = self.shell('cp {srcdir}/dist/* {pkgdir}'
                             .format(srcdir=srcdir, pkgdir=pkgdir))

        # Make sure no steel packages are installed at this point
        out = self.shell('pip freeze')
        self.assertFalse('steel' in out)

        # Now reinstall just steelscript from the pkgs directory
        out = self.shell(('{steel} install --dir {dir} -p steelscript')
                          .format(steel=self.steel, dir=pkgdir))
        self.assertTrue('Installing steelscript' in out)


class TestInstallLocalGit(TestVirtualEnv):

    def test_install_all(self):
        out = self.shell('pip freeze')
        self.assertFalse('steel' in out)

        with self.assertRaises(CalledProcessError):
            out = self.shell('steel -h')

        gitdir = os.path.join(self.venv, 'git')
        self.shell('mkdir {gitdir}'.format(gitdir=gitdir))

        relpath = os.path.abspath(__file__)
        for i in xrange(5):
            relpath = os.path.dirname(relpath)

        pkgs = steelscript.commands.steel.STEELSCRIPT_CORE
        pkgs.append('gitpy-versioning')
        for pkg in pkgs:
            pkg = pkg.replace('.', '-')
            pkgdir = os.path.join(relpath, pkg)
            self.assertTrue(os.path.exists(pkgdir))
            os.symlink(pkgdir, os.path.join(gitdir, pkg + '.git'))

        out = self.shell('{steel} install --giturl file://{gitdir}'
                         .format(steel=self.steel, gitdir=gitdir))
        self.assertTrue('Installing steelscript' in out)

        out = self.shell('steel -h')
        self.assertTrue('Usage' in out)

        out = self.shell('which steel')
        self.assertTrue('{venv}/bin/steel'.format(venv=self.venv) in out)

        out = self.shell('steel about')
        self.assertTrue('steelscript.netprofiler' in out)
        self.assertTrue('steelscript.netshark' in out)


if __name__ == '__main__':
    logging.basicConfig(filename="test.log",
                        level=logging.DEBUG)
    unittest.main()
