import os
import re
import base64
import logging
import readline
import atexit
import shlex
import json
import pydoc
import optparse
import pickle
from collections import namedtuple

from steelscript.common.connection import Connection
from steelscript.common import UserAuth
from steelscript.common.app import Application
from steelscript.commands.steel import BaseCommand

logger = logging.getLogger(__name__)

HistoryContext = namedtuple('HistoryContext', 'name filename obj')

class HistoryManager(object):
    """Manage multiple readline history contexts.

    This manager allows multiple history contexts to be
    defined and switching between contexts.  Since the relationship
    between readline and raw_input() is implied, and readline
    does not support such capability directly, this is
    accomplished by manually manipulating the readline
    history when context is switched.

    """

    def __init__(self):
        self.contexts = {}
        self.current = None

    def add_context(self, name, filename, obj=False):
        """Add a new history context.

        :param str name: unique name for this context

        :param str filename: file to store history in

        :param bool obj: if True, store history as a pickled
            object instead of as text

        The ``obj`` property allows saving mutli-line
        history entries.
        """
        self.contexts[name] = HistoryContext(name=name, filename=filename,
                                             obj=obj)

    def set_context(self, name):
        """Set the current history context.

        This swaps in a new history context by loading
        the history from the contexts filename.  The
        old context's history is saved first.
        """

        if name not in self.contexts:
            raise ValueError("Invalid history context: %s" % name)

        if self.current:
            if name == self.current.name:
                return
            self.save()

        self.current = self.contexts[name]

        try:
            readline.clear_history()
            if self.current.obj:
                with open(self.current.filename, 'r') as f:
                    lines = pickle.load(f)

                for line in lines:
                    readline.add_history(line)

            else:
                readline.read_history_file(self.current.filename)
        except IOError:
            pass

    def save(self):
        """Save the current context's history."""
        if self.current is None:
            raise ValueError("No context set.")

        if self.current.obj:
            lines = []
            for i in range(readline.get_current_history_length()+1):
                line = readline.get_history_item(i)
                if line:
                    lines.append(str(line))
            with open(self.current.filename, 'w') as f:
                pickle.dump(lines, f)
        else:
            readline.write_history_file(self.current.filename)


class RootCommand(BaseCommand):
    # Root command for all REST commands

    def usage(self, fromchild=False):
        return ''


class RestCommand(BaseCommand):
    # Base class for all REST related commands

    def __init__(self, rest, *args, **kwargs):
        super(RestCommand, self).__init__(*args, **kwargs)
        self.rest = rest

    def add_options(self, parser):
        parser.version = None

    def version(self):
        return None

class Connect(RestCommand):
    keyword = 'connect'
    help = 'Establish a new connection to a remote server'

    def add_positional_args(self):
        super(Connect, self).add_positional_args()
        self.add_positional_arg('host', 'Server hostname or IP address')

    def add_options(self, parser):
        group = optparse.OptionGroup(self.parser, "Connection Parameters")
        group.add_option("-P", "--port", dest="port",
                         help="connect on this port")
        group.add_option("-u", "--username", help="username to connect with")
        group.add_option("-p", "--password", help="password to connect with")

        # OAuth is currently part of the Service class which is not used
        # here -- need to rework the code a bit to get that working

        #group.add_option("--oauth", help="OAuth Access Code, in place of "
        #                 "username/password")
        group.add_option("-A", "--api_version", dest="api_version",
                         help="api version to use unconditionally")
        parser.add_option_group(group)
        super(Connect, self).add_options(parser)

    def main(self):
        if self.options.username:
            auth = UserAuth(self.options.username,
                            self.options.password)
        else:
            auth = None

        self.rest.connect(self.options.host, self.options.port, auth)


class Method(RestCommand):
    # Base class for all REST API method commands

    help = """Add URL parameters as <param>=<value>.
Add custom headers as <header>:<value>"""

    def add_positional_args(self):
        super(Method, self).add_positional_args()
        self.add_positional_arg('path', 'Full URL path')

    def main(self):
        if self.rest.conn is None:
            print "Not connected - use 'connect HOST'"
            return

        self.rest.history.set_context('body')
        try:
            if self.readbody:
                lines = []
                if self.rest.interactive:
                    print 'Provide body text, enter "." on a line by itself to finish'
                    if self.rest.jsonmode:
                        print 'Request must be JSON, use double quotes for strings'

                while True:
                    try:
                        line = self.rest.raw_input_no_history("")
                    except EOFError:
                        print ""
                        break
                    except KeyboardInterrupt:
                        print "(aborted)"
                        return

                    if line == '.':
                        break
                    elif line == '.json':
                        self.rest.jsonmode = True
                        continue
                    elif line == '.text':
                        self.rest.jsonmode = False
                        continue

                    lines.append(line)

                if self.rest.jsonmode:
                    body = json.loads('\n'.join(lines))
                    readline.add_history(json.dumps(body, indent=4))
                else:
                    body = '\n'.join(lines)
                    readline.add_history(body)
            else:
                body = None

            if self.args > len(self.positional_args):
                params = {}
                headers = {}

                for arg in self.args:
                    m = re.match('[^:=]*([:=])', arg)
                    if not m or m.group(1) not in ':=':
                        raise ('Invalid argument, expected either k=v for URL param, '
                               'or k:v for header')

                    (k,v) = arg.split(m.group(1), 1)
                    if m.group(1) == ':':
                        headers[k] = v
                    else:
                        params[k] = v
            else:
                headers = None
                params = None

            print "Issuing %s" % self.keyword
            outputlines = None
            if self.rest.jsonmode:
                (data, resp) = self.rest.conn.json_request(
                    self.keyword, path=self.options.path, body=body, params=params,
                    extra_headers=headers, raw_response=True)

                if data is not None:
                    outputlines = json.dumps(data, indent=4)

            else:
                resp = self.rest.conn._request(self.keyword, path=self.options.path,
                                               body=body, params=params,
                                               extra_headers=headers)
                if resp.content:
                    if (  'content-type' in resp.headers and
                          resp.headers['content-type'] == 'application/json'):
                        outputlines = json.dumps(json.loads(resp.content), indent=4)
                    else:
                        outputlines = resp.text

            print "HTTP Status %s: %s bytes" % (resp.status_code, len(resp.content))
            if outputlines is not None:
                count = len(outputlines.split('\n'))
                try:
                    (rows, columns) = os.popen('stty size', 'r').read().split()
                    rows = int(rows)
                except:
                    rows = -1

                if self.rest.interactive and count >= rows:
                    pydoc.pager(outputlines)
                else:
                    print(outputlines)
        finally:
            self.rest.history.set_context('cmd')


class GET(Method):
    keyword = 'GET'
    help = 'Perform an HTTP GET\n\n' + Method.help
    readbody = False


class DELETE(Method):
    keyword = 'DELETE'
    help = 'Perform an HTTP DELETE\\n' + Method.help
    readbody = False


class POST(Method):

    keyword = 'POST'
    help = """Perform an HTTP POST.

You will be prompted to enter the request body.  Use 'mode' to
change the defulat request body format as 'json' or 'text'.

""" + Method.help
    readbody = True


class PUT(Method):

    keyword = 'PUT'
    help = """Perform an HTTP PUT.

You will be prompted to enter the request body.  Use 'mode' to
change the defulat request body format as 'json' or 'text'.

""" + Method.help
    readbody = True


class Help(RestCommand):

    keyword = 'help'
    help = 'Verbose instructions'

    def main(self):
        print """
This shell provides an interactive session for issuing REST calls
to a remote server.

Issue a 'connect <host>' to establish a connection to a remote host.
Once connected, use GET/POST/PUT/DELETE to issue REST calls to the
remote host.

All methods accept parameters via <param>=<value> and headers
for this call via <header>:<value>.

For HTTP methods that require a body, you will be prompted to enter
the body on a separate line.

Available commands:
"""
        w = max([len(sub.keyword) for sub in self.rest.cmd.subcommands])
        for sub in self.rest.cmd.subcommands:
            print "  %-*s  %s" % (w, sub.keyword, sub.help.split('\n')[0])
        print ""

class Mode(RestCommand):

    keyword = 'mode'
    help = 'Change default body encoding'

    def add_positional_args(self):
        super(Mode, self).add_positional_args()
        self.add_positional_arg('mode', 'Input type: json or text')

    def main(self):
        self.rest.jsonmode = (self.options.mode == 'json')


class Command(Application):

    help = "Interactive shell for issuing REST commands"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.conn = None
        self.filelines = []
        self.interactive = True
        self.jsonmode = True

    def parse_args(self):
        super(Command, self).parse_args()

    def add_positional_args(self):
        super(Command, self).add_positional_args()
        #self.add_positional_arg('host', 'Rest hostname or IP address')

    def add_options(self, parser):
        parser.add_option('-f', '--file', help='Read commands from a file')
        super(Command, self).add_options(parser)
        self.add_standard_options(conn=False, log=True)

    def connect(self, host, port, auth=None):
        self.conn = Connection(host, port=port, verify=False)

        if auth is not None:
            # Use HTTP Basic authentication
            s = base64.b64encode("%s:%s" % (auth.username, auth.password))
            self.conn.add_headers({'Authorization': 'Basic %s' % s})
            logger.info("Authenticated using BASIC")

    def raw_input_no_history(self, prompt):
        if self.filelines:
            return self.filelines.pop(0)
        else:
            input = raw_input(prompt)
            readline.remove_history_item(readline.get_current_history_length()-1)
            return input

    def main(self):

        self.history = HistoryManager()
        history = self.history
        history.add_context('cmd', os.path.join(os.path.expanduser('~'),
                                                '.steelscript/rest-cmd-history'))
        history.add_context('body', os.path.join(os.path.expanduser('~'),
                                                 '.steelscript/rest-obj-history'), obj=True)

        history.set_context('cmd')
        atexit.register(HistoryManager.save, history)

        cmd = RootCommand()
        self.cmd = cmd
        GET(self, cmd)
        POST(self, cmd)
        PUT(self, cmd)
        DELETE(self, cmd)
        Connect(self, cmd)
        Help(self, cmd)
        Mode(self, cmd)

        if self.options.file:
            with open(self.options.file, 'r') as f:
                self.filelines = [line.rstrip() for line in f]

        print "REST Shell ('help' or 'quit' when done)"
        print "Current mode is 'json', use 'mode text' to switch to raw text"
        while True:
            if self.filelines:
                line = self.filelines.pop(0)
                self.interactive = False
                print "Command: %s" % line
            else:
                try:
                    if self.conn is not None:
                        prompt = "%s> " % self.conn.hostname
                    else:
                        prompt = "> "
                    line = raw_input(prompt)
                    self.interactive = True
                except EOFError:
                    print ""
                    break

            if not line:
                continue

            args = shlex.split(line)

            if args[0].lower() == 'quit':
                break

            logger.info('Command: %s' % line)
            try:
                cmd.parse(args)
            except SystemExit as e:
                pass
            except Exception as e:
                print "Command raised an error, see log for traceback:\n%s\n" % str(e)
                logger.exception("Command raised an error")
