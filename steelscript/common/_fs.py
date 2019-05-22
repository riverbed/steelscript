# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import os
import json
import platform

try:
    import pickle as pickle
except ImportError:
    import pickle


def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)


class SteelScriptDir(object):
    """Manage user dependent steelscript directory for configuration and data.
    """
    # TODO - add cleanup operations
    def __init__(self, *components, **kwargs):
        """Initialize user local SteelScriptDir object

        By default, the location of this directory will be inside
        a folder named `.steelscript` in the users home directory.
        The specific path varies depending on Operating System.

        This base dir can be overridden by including a ``directory`` keyword
        argument.

        :param components: arguments which will be interpreted
            as hierarchy of folders
        :param directory: optional kwarg which indicates the base directory
            to use.  Any specified components will be appended to this
            location.
        """
        self.basedir = kwargs.get('directory')
        if components:
            self.component = os.path.join(*components)
        else:
            self.component = ''

        if self.basedir is None:
            if platform.system() == 'Windows':
                self.basedir = os.path.join(
                    os.environ['APPDATA'],
                    'steelscript',
                    self.component)
            else:
                self.basedir = os.path.join(
                    os.environ['HOME'],
                    '.steelscript',
                    self.component)
        else:
            self.basedir = os.path.join(self.basedir, self.component)

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
    """Base Class for SteelScript file storage objects."""
    def __init__(self, path, filename):
        self.path = path
        self.filename = filename
        self.fullpath = os.path.join(self.path, filename)
        self.data = None
        self.version = 0
        self.read()

    def read(self):
        """Override method"""
        pass

    def write(self):
        """Override method"""
        pass


class SteelScriptConfig(SteelScriptFile):
    """File object for JSON configuration files."""
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
    """File object for pickled data storage."""
    def __init__(self, *args, **kwargs):
        super(SteelScriptData, self).__init__(*args, **kwargs)

    def read(self):
        if os.path.isfile(self.fullpath):
            with open(self.fullpath, 'rb') as f:
                data = pickle.load(f)

            if 'CACHE_VERSION' in data:
                self.version = data['CACHE_VERSION']
                self.data = data['data']
            else:
                self.data = data

        else:
            self.data = None

    def write(self):
        with open(self.fullpath, 'wb') as f:
            pickle.dump({'CACHE_VERSION': self.version,
                         'data': self.data}, f)
