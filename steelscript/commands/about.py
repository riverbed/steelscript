#!/usr/bin/env python

# Copyright (c) 2019-2024 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.commands.steel import BaseCommand
from importlib.metadata import distribution, distributions
import sys
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
            dist = distribution('steelscript')
        except importlib.metadata.PackageNotFoundError:
            print("Package not found: 'steelscript'")
            print("Check the installation")
            sys.exit(1)

        # Get packages with prefix steel (ex. steelscript.netshark)
        all_distributions = list(distributions())
        steel_pkgs = [dist.name for dist in all_distributions if dist.name.startswith('steel')]
        egg_info_pkgs = []
        egg_link_pkgs = []
        corrupted_pkgs = []

        for p in steel_pkgs:
            dist = distribution(p)
            location = str(dist.locate_file(""))
            if location.endswith('site-packages'):            
                egg_info_pkgs.append(p)
            else:
                egg_link_pkgs.append(p)

        if egg_info_pkgs and egg_link_pkgs:
            corrupted_pkgs = egg_link_pkgs

        print("")
        print("Installed SteelScript Packages")
        print("Core packages:")
        core_pkgs = [dist.name for dist in all_distributions if dist.name.startswith('steel') and 'appfwk' not in dist.name]
        core_pkgs.sort()
        for p in core_pkgs:
            dist = distribution(p)
            if p in corrupted_pkgs:
                print('  %-40s  corrupted' % dist.name)
                continue
            print('  %-40s  %s' % (dist.name, dist.version))

        print("")
        print("Application Framework packages:")
        appfwk_pkgs = [dist.name for dist in all_distributions if dist.name.startswith('steel') and 'appfwk' in dist.name]

        if appfwk_pkgs:
            appfwk_pkgs.sort()
            for p in appfwk_pkgs:
                dist = distribution(p)
                if p in corrupted_pkgs:
                    print('  %-40s  corrupted' % (dist.name))
                    continue
                print('  %-40s  %s' % (dist.name, dist.version))
        else:
            print("  None")

        print("")
        print("REST tools and libraries:")
        all_pkgs = [dist.name for dist in all_distributions]
        installed_rest = set(['reschema', 'sleepwalker']).intersection(set(all_pkgs))
        rest_pkgs = [distribution(p) for p in installed_rest]
        if rest_pkgs:
            for dist in rest_pkgs:
                print('  %-40s  %s' % (dist.name, dist.version))
        else:
            print("  None")

        print("")
        print("Paths to source:")
        paths = [os.path.dirname(p) for p in steelscript.__path__]

        for dist in rest_pkgs:
            location = str(dist.locate_file(""))
            if location not in paths:
                paths.append(location)

        paths.sort()
        for p in paths:
            print("  %s" % p)

        if corrupted_pkgs:
            print("")
            print("WARNING: Corrupted installation detected")
            print("Instructions to fix corrupted packages:")
            print("1. pip uninstall <corrupted_package>")
            print("2. pip install <corrupted_package>")
            print("   or do the following:")
            print("      cd <source_directory_of_corrupted_package>")
            print("      pip install .")

        if self.options.verbose:
            print("")
            print("Python information:")
            print('  Version      :', platform.python_version())
            print('  Version tuple:', platform.python_version_tuple())
            print('  Compiler     :', platform.python_compiler())
            print('  Build        :', platform.python_build())
            print('  Architecture :', platform.architecture())

            print("")
            print("Platform information:")
            print('  platform :', platform.platform())
            print('  system   :', platform.system())
            print('  node     :', platform.node())
            print('  release  :', platform.release())
            print('  version  :', platform.version())
            print('  machine  :', platform.machine())
            print('  processor:', platform.processor())

            print("")
            print("Python path:")
            print(sys.path)
        else:
            print("")
            print("(add -v or --verbose for further information)")
