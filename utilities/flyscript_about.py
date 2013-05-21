#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



import pkg_resources
import platform
import sys

try:
    dist = pkg_resources.get_distribution("flyscript")
    print "Package 'flyscript' version %s installed" % dist.version
except pkg_resources.DistributionNotFound:
    print "Package not found: 'flyscript'"
    print "Check the installation"
    #sys.exit(1)
    

import rvbd
import os.path, pkgutil

pkgpath = os.path.dirname(rvbd.__file__)

print ""
print "Path to source:\n  %s" % pkgpath
print ""
print "Modules provided:" 
for (loader, name, ispkg) in pkgutil.walk_packages([pkgpath]):
    print "  rvbd.%s" % name

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


