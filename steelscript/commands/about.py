#!/usr/bin/env python

# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.commands.steel import BaseCommand

import sys
import pkg_resources

import os.path
import platform
import steelscript


class Command(BaseCommand):
    help = 'Show information about SteelScript packages installed'

    def add_options(self, parser):
        super(Command, self).add_options(parser)
        parser.add_option(
            '-v', '--verbose', action='store_true', default=False,
            help='Show more detailed Python installation information')

    def main(self):
        try:
            dist = pkg_resources.get_distribution('steelscript')
        except pkg_resources.DistributionNotFound:
            print "Package not found: 'steelscript'"
            print "Check the installation"
            sys.exit(1)

        e = pkg_resources.AvailableDistributions()

        print ""
        print "Installed SteelScript Packages"
        print "Core packages:"
        core_pkgs = [x for x in e if x.startswith('steel') and 'appfwk' not in x]
        core_pkgs.sort()
        for p in core_pkgs:
            pkg = pkg_resources.get_distribution(p)
            print '  %-40s  %s' % (pkg.project_name, pkg.version)

        print ""
        print "Application Framework packages:"

        appfwk_pkgs = [x for x in e if x.startswith('steel') and 'appfwk' in x]
        if appfwk_pkgs:
            appfwk_pkgs.sort()
            for p in appfwk_pkgs:
                pkg = pkg_resources.get_distribution(p)
                print '  %-40s  %s' % (pkg.project_name, pkg.version)
        else:
            print "None."

        print ""
        print "Paths to source:"
        paths = [os.path.dirname(p) for p in steelscript.__path__]
        paths.sort()
        for p in paths:
            print "  %s" % p

        if self.options.verbose:
            print ""
            print "Python information:"
            print '  Version      :', platform.python_version()
            print '  Version tuple:', platform.python_version_tuple()
            print '  Compiler     :', platform.python_compiler()
            print '  Build        :', platform.python_build()
            print '  Architecture :', platform.architecture()

            print ""
            print "Platform information:"
            print '  platform :', platform.platform()
            print '  system   :', platform.system()
            print '  node     :', platform.node()
            print '  release  :', platform.release()
            print '  version  :', platform.version()
            print '  machine  :', platform.machine()
            print '  processor:', platform.processor()

            print ""
            print "Python path:"
            print sys.path
        else:
            print ""
            print "(add -v or --verbose for further information)"
