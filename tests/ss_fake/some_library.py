# coding: utf-8
#
# Copyright 2014 Riverbed Technology, Inc.
# All Rights Reserved. Confidential.

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
