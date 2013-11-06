# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.


from rvbd.common.service import UserAuth, OAuth
import rvbd.common.connection

import optparse
import logging
import sys


_log_levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'critical': logging.CRITICAL,
    'error': logging.ERROR
}


class Application(object):
    """ Base class for command-line applications

        This provides the framework but should be subclassed to
        add any customization needed for a particular device.

        Actual scripts should inherit from the device-specific
        subclass rather than this script.
    """
    def __init__(self, main_fn=None):
        """ Base initialization """
        self._main = main_fn

        self.optparse = optparse.OptionParser()
        self.add_options(self.optparse)
        self._add_standard_options()

        self.options = None
        self.args = None
        self.auth = None

    def _add_standard_options(self):
        group = optparse.OptionGroup(self.optparse, "Connection Parameters")
        group.add_option("-P", "--port", dest="port",
                         help="connect on this port")
        group.add_option("", "--force-ssl",
                         dest="force_ssl", action='store_true',
                         help="force ssl to be used")
        group.add_option("", "--force-no-ssl",
                         dest="force_ssl", action='store_false',
                         help="force ssl to not be used")
        group.add_option("-u", "--username", help="username to connect with")
        group.add_option("-p", "--password", help="password to connect with")
        group.add_option("--oauth", help="OAuth Access Code, in place of "
                                         "username/password")
        group.add_option("-A", "--api_version", dest="api_version",
                         help="api version to use unconditionally")
        self.optparse.add_option_group(group)

        group = optparse.OptionGroup(self.optparse, "Logging Parameters")
        group.add_option("--loglevel", help="log level",
                         choices=_log_levels.keys(), default="warning")
        group.add_option("--logfile", help="log file", default=None)
        self.optparse.add_option_group(group)

        group = optparse.OptionGroup(self.optparse, "HTTP Logging Parameters")
        group.add_option(
            "--httplib-debuglevel",
            help="set httplib debug (low-level, lots of data)",
            type=int,
            default=0)
        group.add_option(
            "--debug-msg-body",
            help="number of bytes of message body to log",
            type=int,
            default=0)
        self.optparse.add_option_group(group)

    def add_options(self, parser):
        # this is here for subclasses to override, don't put
        # any log here
        pass

    @classmethod
    def start_logging(cls, loglevel=logging.WARNING, logfile=None):
        """Start up logging.

        This must be called only once and it will not work
        if logging.basicConfig() was already called."""

        options = {
            'level': loglevel,
            'format': "%(asctime)s [%(levelname)-5.5s] (%(name)s) %(msg)s"
        }

        if logfile is not None:
            options['filename'] = logfile

        logging.basicConfig(**options)

        logger = logging.getLogger(__name__)

        logger.info("=" * 70)
        logger.info("==== Started logging: %s" % ' '.join(sys.argv))

    def parse_args(self):
        """ Parses options and arguments and performs validation """
        (self.options, self.args) = self.optparse.parse_args()

        self._validate_auth()

        self.validate_args()

        rvbd.common.connection.Connection.HTTPLIB_DEBUGLEVEL =\
            self.options.httplib_debuglevel
        rvbd.common.connection.Connection.DEBUG_MSG_BODY =\
            self.options.debug_msg_body

    def _validate_auth(self):
        """Verify authentication method passed in and setup Auth object
        """
        if self.options.oauth and (self.options.username or
                                   self.options.password):
            self.optparse.error('Username/Password are mutually exclusive '
                                'from OAuth tokens, please choose only '
                                'one method.')
        elif self.options.oauth:
            self.auth = OAuth(self.options.oauth)
        else:
            self.auth = UserAuth(self.options.username, self.options.password)

    def validate_args(self):
        """ Hook for subclasses to add their own option/argument validation
        """
        pass

    def setup(self):
        """ Commands to run right after arguments have been parsed,
        but before main.
        """
        pass

    def run(self):
        """ Main execution point """
        self.parse_args()
        self.start_logging(_log_levels[self.options.loglevel],
                           self.options.logfile)

        self.setup()
 
        if self._main is None:
            ret = self.main()
        else:
            ret = self._main(self)

        if ret is None:
            ret = 0
        sys.exit(ret)

    def main(self):
        """ XXX document """
        raise NotImplementedError()


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
