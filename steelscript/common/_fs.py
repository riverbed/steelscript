# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.



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


class SteelScriptDir(object):
    """Manages the user dependent steelscript directory used
    to store user relevant configuration and data
    """
    # TODO - add cleanup operations
    def __init__(self, *components, **kwargs):
        self.basedir = kwargs.get('directory')
        self.component = os.path.join(*components)

        if self.basedir is None and platform.system() == 'Windows':
            self.basedir = os.path.join(
                os.environ['APPDATA'],
                'steelscript',
                self.component)
        elif self.basedir is None and platform.system() == 'Linux':
            self.basedir = os.path.join(
                os.environ['HOME'],
                '.steelscript', self.component)
        elif self.basedir is None and platform.system() == 'Darwin':
            self.basedir = os.path.join(
                os.environ['HOME'],
                '.steelscript',
                self.component)
        ensure_dir(self.basedir)

    def isfile(self, filename, prefix=''):
        return os.path.isfile(os.path.join(self.basedir, prefix, filename))

    def get_files(self):
        return os.listdir(self.basedir)

    def get_config(self, filename):
        """Return SteelScriptConfig file for the filename specified
        """
        # TODO: support subdirectories
        return SteelScriptConfig(self.basedir, filename)

    def get_data(self, filename):
        """Return SteelScriptData file for the filename specified
        """
        # TODO: support subdirectories
        return SteelScriptData(self.basedir, filename)


class SteelScriptFile(object):
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


class SteelScriptConfig(SteelScriptFile):
    """File object for JSON configuration files
    """
    def __init__(self, *args, **kwargs):
        super(SteelScriptConfig, self).__init__(*args, **kwargs)

    def read(self):
        if os.path.isfile(self.fullpath):
            with open(self.fullpath, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = None

    def write(self):
        with open(self.fullpath, 'w') as f:
            json.dump(self.data, f)


class SteelScriptData(SteelScriptFile):
    """File object for pickled data storage
    """
    def __init__(self, *args, **kwargs):
        super(SteelScriptData, self).__init__(*args, **kwargs)

    def read(self):
        if os.path.isfile(self.fullpath):
            with open(self.fullpath, 'r') as f:
                self.data = pickle.load(f)
        else:
            self.data = None

    def write(self):
        with open(self.fullpath, 'w') as f:
            pickle.dump(self.data, f)
