# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.


import os
import json
import platform

try:
    import cPickle as pickle
except ImportError:
    import pickle


def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)


class FlyscriptDir(object):
    """Manages the user dependent flyscript directory used
    to store user relevant configuration and data
    """
    # TODO - add cleanup operations
    def __init__(self, *components, **kwargs):
        self.basedir = kwargs.get('directory')
        self.component = os.path.join(*components)

        if self.basedir is None and platform.system() == 'Windows':
            self.basedir = os.path.join(
                os.environ['APPDATA'],
                'flyscript',
                self.component)
        elif self.basedir is None and platform.system() == 'Linux':
            self.basedir = os.path.join(
                os.environ['HOME'],
                '.flyscript', self.component)
        elif self.basedir is None and platform.system() == 'Darwin':
            self.basedir = os.path.join(
                os.environ['HOME'],
                '.flyscript',
                self.component)
        ensure_dir(self.basedir)

    def isfile(self, filename, prefix=''):
        return os.path.isfile(os.path.join(self.basedir, prefix, filename))

    def get_files(self):
        return os.listdir(self.basedir)

    def get_config(self, filename):
        """Return FlyscriptConfig file for the filename specified
        """
        # TODO: support subdirectories
        return FlyscriptConfig(self.basedir, filename)

    def get_data(self, filename):
        """Return FlyscriptData file for the filename specified
        """
        # TODO: support subdirectories
        return FlyscriptData(self.basedir, filename)


class FlyscriptFile(object):
    """Base Class for Flyscript file storage objects
    """
    def __init__(self, path, filename):
        self.path = path
        self.filename = filename
        self.fullpath = os.path.join(self.path, filename)
        self.data = None
        self.read()

    def read(self):
        """Override method"""
        pass

    def write(self):
        """Override method"""
        pass


class FlyscriptConfig(FlyscriptFile):
    """File object for JSON configuration files
    """
    def __init__(self, *args, **kwargs):
        super(FlyscriptConfig, self).__init__(*args, **kwargs)

    def read(self):
        if os.path.isfile(self.fullpath):
            with open(self.fullpath, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = None

    def write(self):
        with open(self.fullpath, 'w') as f:
            json.dump(self.data, f)


class FlyscriptData(FlyscriptFile):
    """File object for pickled data storage
    """
    def __init__(self, *args, **kwargs):
        super(FlyscriptData, self).__init__(*args, **kwargs)

    def read(self):
        if os.path.isfile(self.fullpath):
            with open(self.fullpath, 'r') as f:
                self.data = pickle.load(f)
        else:
            self.data = None

    def write(self):
        with open(self.fullpath, 'w') as f:
            pickle.dump(self.data, f)
