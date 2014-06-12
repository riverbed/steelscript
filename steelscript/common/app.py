# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.common.service import UserAuth, OAuth
import steelscript.common.connection
from steelscript.commands.steel import BaseCommand

import optparse
import logging
import sys
import os


class Application(BaseCommand):
    """ Base class for command-line applications

        This provides the framework but should be subclassed to
        add any customization needed for a particular device.

        Actual scripts should inherit from the device-specific
        subclass rather than this script.
    """
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        self.has_conn_options = False
        self.has_log_options = False
        self.auth = None

    def run(self):
        self.parse(sys.argv[1:])

    def add_standard_options(self, conn=True, log=True):
        if conn:
            group = optparse.OptionGroup(self.parser, "Connection Parameters")
            group.add_option("-P", "--port", dest="port",
                             help="connect on this port")
            group.add_option("-u", "--username", help="username to connect with")
            group.add_option("-p", "--password", help="password to connect with")
            group.add_option("--oauth", help="OAuth Access Code, in place of "
                             "username/password")
            group.add_option("-A", "--api_version", dest="api_version",
                             help="api version to use unconditionally")
            self.parser.add_option_group(group)
            self.has_conn_options = True

        if log:
            group = optparse.OptionGroup(self.parser, "REST Logging")
            group.add_option("--rest-debug", type='int', default=0,
                             help="Log REST info (1=hdrs, 2=body)")
            group.add_option("--rest-body-lines", type=int, default=20,
                             help="Number of lines of request/response body to log")
            self.parser.add_option_group(group)
            self.has_log_options = True

    def validate_args(self):
        """ Hook for subclasses to add their own option/argument validation
        """
        super(Application, self).validate_args()

        if self.has_conn_options:
            if self.options.oauth and (self.options.username or
                                       self.options.password):
                self.parser.error('Username/Password are mutually exclusive '
                                  'from OAuth tokens, please choose only '
                                  'one method.')
            elif self.options.oauth:
                self.auth = OAuth(self.options.oauth)
            else:
                self.auth = UserAuth(self.options.username,
                                     self.options.password)

        if self.has_log_options:
            steelscript.common.connection.Connection.REST_DEBUG = (
                self.options.rest_debug)
            steelscript.common.connection.Connection.REST_BODY_LINES = (
                self.options.rest_body_lines)

    def main(self):
        print ("Not implemented")


class Logger(object):

    @classmethod
    def add_options(cls, parser):
        group = optparse.OptionGroup(parser, "Logging Parameters")
        group.add_option("--loglevel", help="log level",
                         choices=_log_levels.keys(), default="warning")
        group.add_option("--logfile", help="log file", default=None)
        parser.add_option_group(group)

    @classmethod
    def start_logging(cls, options):
        """Start up logging.

        This must be called only once and it will not work
        if logging.basicConfig() was already called."""

        cfg_options = {
            'level': _log_levels[options.loglevel],
            'format': "%(asctime)s [%(levelname)-5.5s] (%(name)s) %(msg)s"
        }

        if options.logfile is not None:
            cfg_options['filename'] = options.logfile

        logging.basicConfig(**cfg_options)

        logger = logging.getLogger(__name__)

        logger.info("=" * 70)
        logger.info("==== Started logging: %s" % ' '.join(sys.argv))
