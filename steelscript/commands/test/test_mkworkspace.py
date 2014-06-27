# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import os
import sys
import ntpath
import shutil
import logging

from steelscript.commands.steel import shell, ShellFailed

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


def path_leaf(path):
    """:returns the name of the last file/directory in the given path"""
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def mkdir(dirname):
    """Creates directory if it doesn't already exist."""
    if not os.path.exists(dirname):
        os.mkdir(dirname)


def mk_dummy_file(dirpath, name):
    """Creates a dummy file with name and directory"""
    fname = os.path.join(dirpath, name)
    if not os.path.exists(fname):
        with open(fname, 'w') as f:
            f.write('This is a dummy file for testing')
    else:
        pass


class TestWorkspace(unittest.TestCase):
    """Simple test class which creates a temporary workspace for testing

    Before the tests are run, this class will make a workspace in the root
    directory of Steelscript as well as ten dummy example files to be used for
    testing. Then when all tests have finished, it will delete both the
    workspace and the examples files.

    The examples path is stored in TestWorkspace.tmp_examples_path.
    The workspace path is stored in TestWorkspace.tmp_workspace_path.
    """

    tmp_examples_path = os.path.join(sys.prefix, 'share', 'doc', 'steelscript',
                          'examples', 'steelscript')
    # The temporary workspace is located in the directory with all the temporary
    # example files.
    tmp_workspace_path = os.path.join(tmp_examples_path, 'test-workspace')

    @classmethod
    def setUpClass(cls):
        """Creates /examples in steelscript dir and makes a temp workspace"""
        # Create the directories that may or may not exist already
        mkdir(os.path.join(sys.prefix, 'share'))
        mkdir(os.path.join(sys.prefix, 'share', 'doc'))
        mkdir(os.path.join(sys.prefix, 'share', 'doc', 'steelscript'))
        mkdir(os.path.join(sys.prefix, 'share', 'doc',
                           'steelscript', 'examples'))
        # Make the directory which will contain all the examples. Then generate
        # ten dummy files and put it inside. Then make a workspace inside that
        # directory to be used for testing.
        mkdir(cls.tmp_examples_path)
        for i in range(10):
            mk_dummy_file(cls.tmp_examples_path, 'test_example_' + str(i) + '.py')
        cd = 'cd ' + cls.tmp_examples_path + ';'
        cls.shell(cd + 'steel mkworkspace -d ' + cls.tmp_workspace_path)

    @classmethod
    def tearDownClass(cls):
        """Deletes /examples and /test-workspace in steelscript"""
        shutil.rmtree(cls.tmp_examples_path)

    @classmethod
    def shell(cls, cmd):
        if cmd.startswith('steel' or cmd.startswith(cls.steel)):
            opts=' --loglevel debug --logfile -'
        else:
            opts=''
        return shell('{cmd}{opts}'.format(cmd=cmd, opts=opts),
                     exit_on_fail=False, save_output=True)


class TestWorkspaceFunctionality(TestWorkspace):
    def test_create_workspace(self):
        """Tests if all the correct files were created during mkworkspace"""
        # Test if the directory was made
        steel_ex_path = os.path.join(self.tmp_workspace_path,
                                     'steelscript-examples')
        self.assertTrue(os.path.exists(steel_ex_path))
        # Test if the dummy files were made
        dummy_files = os.listdir(steel_ex_path)
        self.assertEqual(len(dummy_files), 10)
        # Test if the readme and collect_examples were created
        readme_path = os.path.join(self.tmp_workspace_path, 'README.md')
        collect_ex_path = os.path.join(self.tmp_workspace_path,
                                       'collect_examples.py')
        self.assertTrue(os.path.exists(readme_path))
        self.assertTrue(os.path.exists(collect_ex_path))

    def test_collect_reports_script(self):
        """Makes sure all aspects of the collect_examples.py file work"""
        # Test that the examples directory is still there
        steel_ex_path = os.path.join(self.tmp_workspace_path,
                                     'steelscript-examples')
        self.assertTrue(os.path.exists(self.tmp_workspace_path))
        # Remove the examples directory, then use the
        # collect_examples script to get them back
        shutil.rmtree(steel_ex_path)
        cd = 'cd ' + self.tmp_workspace_path + ';'
        self.shell(cd + 'python collect_examples.py')
        dummy_files = os.listdir(steel_ex_path)
        self.assertEqual(len(dummy_files), 10)


    def test_overwrite_in_collect_reports_script(self):
        steel_ex_path = os.path.join(self.tmp_workspace_path,
                                     'steelscript-examples')
        # Test if the overwrite functionality works
        # First we will test that the file doesn't get overwritten
        file_path = os.path.join(steel_ex_path, 'test_example_1.py')
        test_file = open(file_path, 'r+')
        test_file.write('This file better not get overwritten')
        test_file.close()
        cd = 'cd ' + self.tmp_workspace_path + ';'
        self.shell(cd + 'python collect_examples.py')
        test_file = open(file_path)
        self.assertEqual(test_file.read(), 'This file better not get overwritten')
        test_file.close()
        # Now we test that the file does indeed get overwritten
        self.shell(cd + 'python collect_examples.py --overwrite')
        test_file = open(file_path)
        self.assertNotEqual(test_file.read(), 'This file better not get overwritten')
        # Now we celebrate because all the tests passed! :)

if __name__ == '__main__':
    logging.basicConfig(filename="test.log",
                        level=logging.DEBUG)
    unittest.main()
