# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import os
import sys
import glob
import shutil
import importlib.resources

def link_pkg_dir(pkgname, src_path, dest_dir, symlink=True,
                 replace=True, buf=None):
    """Create a link from a resource within an installed package.

    :param pkgname: name of installed package
    :param src_path: relative path within package to resource
    :param dest_dir: absolute path to location to link/copy
    :param symlink: create a symlink or copy files
    :param replace: if True, will unlink/delete before linking
    :param buf: IO buffer to send debug statements, if None uses sys.stdout
    """
    if buf is None:
        debug = sys.stdout.write
    else:
        debug = buf

    src_dir = importlib.resources.files(pkgname) / src_path

    if os.path.islink(dest_dir) and not os.path.exists(dest_dir):
        debug(' unlinking %s ...\n' % dest_dir)
        os.unlink(dest_dir)

    if os.path.exists(dest_dir):
        if not replace:
            return

        if os.path.islink(dest_dir):
            debug(' unlinking %s ...\n' % dest_dir)
            os.unlink(dest_dir)
        else:
            debug(' removing %s ...\n' % dest_dir)
            shutil.rmtree(dest_dir)

    if symlink:
        debug(' linking %s --> %s\n' % (src_dir, dest_dir))
        os.symlink(src_dir, dest_dir)
    else:
        debug(' copying %s --> %s\n' % (src_dir, dest_dir))
        shutil.copytree(src_dir, dest_dir)


def link_pkg_files(pkgname, src_pattern, dest_dir, symlink=True,
                   replace=True, buf=None):
    """Create links for files from a resource within an installed package.

    :param pkgname: name of installed package
    :param src_pattern: relative path within package to file resource,
        can be a glob pattern
    :param dest_dir: absolute path to location to link/copy, symlinks
        will be made inside this dir rather than linking to the dir itself
    :param symlink: create a symlink or copy files
    :param replace: if True, will unlink/delete before linking
    :param buf: IO buffer to send debug statements, if None uses sys.stdout
    """
    if buf is None:
        debug = sys.stdout.write
    else:
        debug = buf

    src_dir = importlib.resources.files(pkgname) / src_pattern

    src_files = glob.glob(src_dir)

    if os.path.islink(dest_dir):
        # avoid putting files within a symlinked path
        debug(' skipping linked directory %s ...\n' % dest_dir)
        return

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for f in src_files:
        fn = os.path.basename(f)
        dest_file = os.path.join(dest_dir, fn)

        if os.path.exists(dest_file) and not replace:
            debug(' skipping file %s ...\n' % dest_file)
            continue

        if os.path.islink(dest_file):
            debug(' unlinking %s ...\n' % dest_file)
            os.unlink(dest_file)
        elif os.path.exists(dest_file):
            debug(' removing %s ...\n' % dest_file)
            os.unlink(dest_file)

        if symlink:
            debug(' linking %s --> %s\n' % (f, dest_file))
            os.symlink(f, dest_file)
        else:
            debug(' copying %s --> %s\n' % (f, dest_file))
            shutil.copy(f, dest_file)
