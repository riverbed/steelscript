# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from __future__ import (absolute_import, unicode_literals, print_function,
                        division)

import logging


class FakeLibraryClass(object):

    def __init__(self):

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.info("Initializing FakeLibraryClass")

    def do_something(self):
        self.log.info("Doing something...")

    def do_something_trivial(self):
        self.log.debug("Doing something trivial...")

    def do_something_stupid(self):
        self.log.warning("Doing something stupid")

    def do_something_fatal(self):
        self.log.critical("Doing something fatal")
