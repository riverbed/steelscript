#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.


import sys
import pkg_resources

try:
    dist = pkg_resources.get_distribution('steelscript.common')
except pkg_resources.DistributionNotFound:
    print "Package not found: 'steelscript.common'"
    print "Check the installation"
    sys.exit(1)


import os.path
import platform
import steelscript

pkgpath = os.path.dirname(steelscript.__file__)

e = pkg_resources.AvailableDistributions()

print ""
print "Path to source:\n  %s" % pkgpath
print ""
print "Installed SteelScript Packages"
print "Core packages:"
core_pkgs = [x for x in e if x.startswith('steel') and 'appfwk' not in x]
for p in core_pkgs:
    pkg = pkg_resources.get_distribution(p)
    print '%40s - %s' % (pkg.project_name, pkg.version)

print ""
print "Application Framework packages:"

appfwk_pkgs = [x for x in e if x.startswith('steel') and 'appfwk' in x]
if appfwk_pkgs:
    for p in appfwk_pkgs:
        pkg = pkg_resources.get_distribution(p)
        print '%40s - %s' % (pkg.project_name, pkg.version)
else:
    print "None."


if '-v' in sys.argv or '--verbose' in sys.argv:
    print ""
    print "Python information:"
    print 'Version      :', platform.python_version()
    print 'Version tuple:', platform.python_version_tuple()
    print 'Compiler     :', platform.python_compiler()
    print 'Build        :', platform.python_build()
    print 'Architecture :', platform.architecture()

    print ""
    print "Platform information:"
    print platform.platform()
    print 'system   :', platform.system()
    print 'node     :', platform.node()
    print 'release  :', platform.release()
    print 'version  :', platform.version()
    print 'machine  :', platform.machine()
    print 'processor:', platform.processor()

    print ""
    print "Python path:"
    print sys.path
else:
    print ""
    print "(add -v or --verbose for further information)"
