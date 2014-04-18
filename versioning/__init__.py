# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/sleepwalker/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.

from __future__ import unicode_literals, print_function, division
import re
from subprocess import Popen, PIPE
import os

"""
This module contains code for interacting with git repositories. It is
used to determine an appropriate version number from either the local
git repository tags or from a version file.
"""

def verify_repository():
    """Raise an error if this source file is not in tracked by git."""

    f = os.path.dirname(os.path.abspath(__file__))
    process = Popen(['git', 'ls-files', f, '--error-unmatch'],
                    stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    if stderr:
        # Not a git repo
        raise EnvironmentError(stderr)


def call_git_branch():
    """Return 'git branch' output."""
    process = Popen(['git', 'branch'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    if stderr:
        # Not a git repo
        raise EnvironmentError(stderr)
    else:
        return stdout.strip()


def get_branch(input=None):
    """Parse branch from 'git branch' output.

    :param input: Return string from 'git branch' command
    """
    if input is None:
        input = call_git_branch()

    line = [ln for ln in input.split('\n') if ln.startswith('*')][0]
    return line.split()[-1]


def call_git_describe(abbrev=None):
    """Return 'git describe' output.

    :param abbrev: Integer to use as the --abbrev value for git describe
    """
    cmd = ['git', 'describe']

    # --abbrev and --long are mutually exclusive 'git describe' options
    if abbrev is not None:
        cmd.append('--abbrev={0}'.format(abbrev))
    else:
        cmd.append('--long')

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    if stderr:
        # Not a git repo
        raise EnvironmentError(stderr)
    else:
        return stdout.strip()


def parse_tag():
    """Parse version info from 'git describe' and return as dict.

    A typical full git tag contains four pieces of information: the repo name,
    the version, the number of commits since the last tag, and the SHA-1 hash
    that identifies the commit.

    :return: A dict with items 'version', 'commits', and 'sha'

    """
    long_tag = call_git_describe()
    base_tag = call_git_describe(abbrev=0)

    # Parse number of commits and sha
    try:
        raw_version_str = long_tag.replace(base_tag, '')
        commits, sha = [part for part in raw_version_str.split('-') if part]
    except ValueError:
        # Tuple unpacking failed, so probably an incorrect tag format was used.
        print('Parsing error: The git tag seems to be malformed.\n---')
        raise

    return {'version': base_tag,
            'commits': commits,
            'sha': sha.strip(), }


def get_version(v_file='RELEASE-VERSION'):
    """Return <tag>.post<commits> style version string.

    :param v_file: Fallback path name to a file where release_version is saved
    """

    try:
        verify_repository()
        git_info = parse_tag()
        branch = get_branch()
        assert branch == 'master'
        if git_info['commits'] == '0':
            version = git_info['version']
        else:
            version = '%s.post%s' % (git_info['version'], git_info['commits'])

        with open(v_file, 'w') as f:
            f.write(version)

    except EnvironmentError:
        # Not a git repository, so fall back to reading RELEASE-VERSION
        with open(v_file, 'r') as f:
            version = f.read()

    except AssertionError:
        print('Release version string can only be derived from master branch.'
              '\n---')
        raise EnvironmentError('Current branch not master: %s' % branch)

    return version
