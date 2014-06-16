``steel`` Command
=================

Once the base ``steelscript`` package is installed, the ``steel`` shell command
is availble.  This command will normally be installed in your path so that you can
just run it from any directory.

The functions provided by ``steel`` depend on what additional packages are installed,
as each package may define additional sub-commands.

The base command from just ``steelscript`` provides the following subcommands:

* ``steel about`` - Show information about SteelScript packages installed
* ``steel install`` - Package installation
* ``steel rest`` - Interactive shell for issuing REST commands

Most subcommands accept two options that control logging:

.. code-block:: bash

   Logging Parameters:
     --loglevel=LOGLEVEL  log level: debug, warn, info, critical, error
     --logfile=LOGFILE    log file, use '-' for stdout

By default, the log level is set to ``info`` and logging is sent to
the file ``~/.steelscript/steel.log``.

In addition, many commands support detailed REST logging parameters:

.. code-block:: bash

   REST Logging:
     --rest-debug=REST_DEBUG
                         Log REST info (1=hdrs, 2=body)
     --rest-body-lines=REST_BODY_LINES
                         Number of lines of request/response body to log

``steel install``
-----------------

The ``install`` subcommand is used to install and upgrade pacakges.  There
are a number of installation options available:

.. code-block:: bash

   $  steel install -h
   Usage: steel install [options]

     Package installation

   Options:
     --version             show program's version number and exit
     -h, --help            show this help message and exit

     Package installation options:
       -U, --upgrade       Upgrade packages that are already installed
       -d DIR, --dir=DIR   Directory to use for installation
       -g, --github        Install packages from github
       --develop           Combine with --gitlab to checkout packages
       -p PACKAGES, --package=PACKAGES
                           Package to install (may specify more than once)
       --appfwk            Install all application framework packages
       --pip-options=PIP_OPTIONS
                           Additional options to pass to pip

``steel rest``
--------------

The ``rest`` subcommand starts an interactive shell for issuing REST
commands to a target server.  This is best shown by an example by
connecting to the test server at `httpbin.org <http://httpbin.org>`_.  This
freely available test server echos back information sent to it and
provides a nice way to demonstrate the features of the REST shell:

The REST shell support history even across sessions, allowing you to
scroll back through previous commands via up/down arrows and editing.
Use ``Ctrl-R`` to search backword for a command.

Connecting
~~~~~~~~~~

A connection must first be established using the ``connect`` command:

.. code-block:: bash

   $ steel rest
   REST Shell ('help' or 'quit' when done)
   Current mode is 'json', use 'mode text' to switch to raw text
   > connect http://httpbin.org/
   http://httpbin.org/>

This creates a Python requests session to the target server.  Basic
authentication is supported by adding ``-u <username> -p <password>``.

The prompt changes to show the server currently used for REST requests.

At any time a connection to a new server may be establshed using
``connect`` and the new server name.

Methods
~~~~~~~

The for basic HTTP methods are supported: GET, POST, PUT, DELETE.  Each
method takes the same parameters:

.. code-block:: bash

   http://httpbin.org/> GET -h
   Usage: GET <PATH> [options] ...

     Perform an HTTP GET

     Add URL parameters as <param>=<value>.
     Add custom headers as <header>:<value>

   Required Arguments:
     PATH        Full URL path

   Options:
     -h, --help  show this help message and exit

Let's try a simple GET of the path ``/get``.  The full URL will be
the current server plus the absolute path ``http://httpbin.org/get``:

.. code-block:: bash

   http://httpbin.org/> GET /get
   Issuing GET
   HTTP Status 200: 406 bytes
   {
       "origin": "208.70.199.4",
       "headers": {
           "X-Request-Id": "860f1a1c-642e-4aef-a673-aad538976475",
           "Accept-Encoding": "gzip, deflate",
           "Host": "httpbin.org",
           "Accept": "application/json",
           "User-Agent": "python-requests/2.3.0 CPython/2.7.3 Darwin/13.1.0",
           "Connection": "close",
           "Content-Type": "application/json"
       },
       "args": {},
       "url": "http://httpbin.org/get"
   }

Once the REST request is issued, any response from the server is
displayed.  Note that the above response including ``"origin"`` and
``"headers"`` is in the body of the response from httpbin_ -- this
server echos back information about the request in response to support
testing.  So the ``"headers"`` shows the request headers that were
automatically added to the outgoing request type.

Notice that the content-type is application/json -- this is the default
encoding for outgoing requests.  This applies primarily to PUT and POST
which will prompt for a BODY:

.. code-block:: bash

   http://httpbin.org/> POST /post
   Provide body text, enter "." on a line by itself to finish
   Request must be JSON, use double quotes for strings
   {
     "first": "Chris",
     "last": "White"
   }
   .

The after entering that last line with a period "." by it self, the
REST shell issues the POST request and displays the response from the
server:

.. code-block:: bash

   Issuing POST
   HTTP Status 200: 586 bytes
   {
       "files": {},
       "origin": "208.70.199.4",
       "form": {},
       "url": "http://httpbin.org/post",
       "args": {},
       "headers": {
           "Content-Length": "35",
           "Accept-Encoding": "gzip, deflate",
           "X-Request-Id": "36067711-b9a9-47b6-9f65-60202a1dffe7",
           "Host": "httpbin.org",
           "Accept": "application/json",
           "User-Agent": "python-requests/2.3.0 CPython/2.7.3 Darwin/13.1.0",
           "Connection": "close",
           "Content-Type": "application/json"
       },
       "json": {
           "last": "White",
           "first": "Chris"
       },
       "data": "{\"last\": \"White\", \"first\": \"Chris\"}"
   }

URL Parameters and Custom Headers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All methods support adding URL parameters and custom headers
on the same line as the method:

.. code-block:: bash

   http://httpbin.org/> GET /get x=1 y=2 X-Hdr:foo Y-Hdr:bar

The above will encode two URL parameters ``x`` and ``y`` and
will add two custom HTTP headers ``X-Hdr`` and ``Y-Hdr``.

JSON vs Text modes
~~~~~~~~~~~~~~~~~~

By default, the PUT/POST body is expected to be a JSON value.
If the target server instead requires raw text, this can be changed
by the ``mode`` command:

.. code-block:: bash

   http://httpbin.org/> POST /post
   Provide body text, enter "." on a line by itself to finish
   Any value allowed
   Here! Here!
   .
   Issuing POST
   HTTP Status 200: 475 bytes
   {
       "files": {},
       "origin": "208.70.199.4",
       "form": {},
       "url": "http://httpbin.org/post",
       "args": {},
       "headers": {
           "Content-Length": "29",
           "Accept-Encoding": "gzip, deflate",
           "X-Request-Id": "6d2076cc-0213-4d74-84fd-24e6c8a37112",
           "Host": "httpbin.org",
           "Accept": "*/*",
           "User-Agent": "python-requests/2.3.0 CPython/2.7.3 Darwin/13.1.0",
           "Connection": "close"
       },
       "json": null,
       "data": "Any value allowed\nHere! Here!"
   }

REST Logging
~~~~~~~~~~~~

Often it is useful to see the full details of each REST request and
response.  This is achieved using ``--rest-debug=<num>`` and
``--rest-body-lines=<num>``.

As a simple example, here's the full tracing for ``POST /post`` above
with full logging enabled:

.. code-block:: bash

    $ steel rest --logfile - --rest-debug=2 --rest-body-lines=10000
    2014-06-12 22:41:40,511 [INFO ] (steelscript.commands.steel) ======================================================================
    2014-06-12 22:41:40,511 [INFO ] (steelscript.commands.steel) ==== Started logging: /Users/cwhite/env/ss/bin/steel rest --logfile - --rest-debug=2 --rest-body-lines=10000
    REST Shell ('help' or 'quit' when done)
    Current mode is 'json', use 'mode text' to switch to raw text
    > connect http://httpbin.org/
    2014-06-12 22:41:44,171 [INFO ] (steelscript.commands.rest) Command: connect http://httpbin.org/
    http://httpbin.org/> POST /post
    2014-06-12 22:41:47,970 [INFO ] (steelscript.commands.rest) Command: POST /post
    Provide body text, enter "." on a line by itself to finish
    Request must be JSON, use double quotes for strings
    {
        "last": "White",
        "first": "Chris"
    }
    .
    Issuing POST
    2014-06-12 22:41:56,370 [INFO ] (REST) POST http://httpbin.org/post
    2014-06-12 22:41:56,371 [INFO ] (REST) Extra request headers:
    2014-06-12 22:41:56,371 [INFO ] (REST) ... Content-Type: application/json
    2014-06-12 22:41:56,371 [INFO ] (REST) ... Accept: application/json
    2014-06-12 22:41:56,371 [INFO ] (REST) Request body:
    2014-06-12 22:41:56,371 [INFO ] (REST) ... {
    2014-06-12 22:41:56,371 [INFO ] (REST) ...   "last": "White",
    2014-06-12 22:41:56,372 [INFO ] (REST) ...   "first": "Chris"
    2014-06-12 22:41:56,372 [INFO ] (REST) ... }
    2014-06-12 22:41:56,393 [INFO ] (requests.packages.urllib3.connectionpool) Starting new HTTP connection (1): httpbin.org
    2014-06-12 22:41:56,608 [INFO ] (REST) Request headers:
    2014-06-12 22:41:56,608 [INFO ] (REST) ... Content-Length: 35
    2014-06-12 22:41:56,608 [INFO ] (REST) ... Content-Type: application/json
    2014-06-12 22:41:56,608 [INFO ] (REST) ... Accept-Encoding: gzip, deflate
    2014-06-12 22:41:56,608 [INFO ] (REST) ... Accept: application/json
    2014-06-12 22:41:56,609 [INFO ] (REST) ... User-Agent: python-requests/2.3.0 CPython/2.7.3 Darwin/13.1.0
    2014-06-12 22:41:56,609 [INFO ] (REST) Response Status 200, 586 bytes
    2014-06-12 22:41:56,609 [INFO ] (REST) Response headers:
    2014-06-12 22:41:56,609 [INFO ] (REST) ... content-length: 586
    2014-06-12 22:41:56,609 [INFO ] (REST) ... server: gunicorn/18.0
    2014-06-12 22:41:56,609 [INFO ] (REST) ... connection: keep-alive
    2014-06-12 22:41:56,609 [INFO ] (REST) ... date: Fri, 13 Jun 2014 02:41:56 GMT
    2014-06-12 22:41:56,609 [INFO ] (REST) ... access-control-allow-origin: *
    2014-06-12 22:41:56,609 [INFO ] (REST) ... content-type: application/json
    2014-06-12 22:41:56,623 [INFO ] (REST) Response body:
    2014-06-12 22:41:56,623 [INFO ] (REST) ... {
    2014-06-12 22:41:56,623 [INFO ] (REST) ...   "files": {},
    2014-06-12 22:41:56,623 [INFO ] (REST) ...   "origin": "72.93.33.239",
    2014-06-12 22:41:56,623 [INFO ] (REST) ...   "form": {},
    2014-06-12 22:41:56,623 [INFO ] (REST) ...   "url": "http://httpbin.org/post",
    2014-06-12 22:41:56,623 [INFO ] (REST) ...   "args": {},
    2014-06-12 22:41:56,623 [INFO ] (REST) ...   "headers": {
    2014-06-12 22:41:56,623 [INFO ] (REST) ...     "Content-Length": "35",
    2014-06-12 22:41:56,623 [INFO ] (REST) ...     "Accept-Encoding": "gzip, deflate",
    2014-06-12 22:41:56,624 [INFO ] (REST) ...     "X-Request-Id": "aad9bb28-eaa1-4302-a248-a24bb4ea671f",
    2014-06-12 22:41:56,624 [INFO ] (REST) ...     "Host": "httpbin.org",
    2014-06-12 22:41:56,624 [INFO ] (REST) ...     "Accept": "application/json",
    2014-06-12 22:41:56,624 [INFO ] (REST) ...     "User-Agent": "python-requests/2.3.0 CPython/2.7.3 Darwin/13.1.0",
    2014-06-12 22:41:56,624 [INFO ] (REST) ...     "Connection": "close",
    2014-06-12 22:41:56,624 [INFO ] (REST) ...     "Content-Type": "application/json"
    2014-06-12 22:41:56,624 [INFO ] (REST) ...   },
    2014-06-12 22:41:56,624 [INFO ] (REST) ...   "json": {
    2014-06-12 22:41:56,624 [INFO ] (REST) ...     "last": "White",
    2014-06-12 22:41:56,624 [INFO ] (REST) ...     "first": "Chris"
    2014-06-12 22:41:56,624 [INFO ] (REST) ...   },
    2014-06-12 22:41:56,624 [INFO ] (REST) ...   "data": "{\"last\": \"White\", \"first\": \"Chris\"}"
    2014-06-12 22:41:56,624 [INFO ] (REST) ... }
    HTTP Status 200: 586 bytes
    {
        "files": {},
        "origin": "72.93.33.239",
        "form": {},
        "url": "http://httpbin.org/post",
        "args": {},
        "headers": {
            "Content-Length": "35",
            "Accept-Encoding": "gzip, deflate",
            "X-Request-Id": "aad9bb28-eaa1-4302-a248-a24bb4ea671f",
            "Host": "httpbin.org",
            "Accept": "application/json",
            "User-Agent": "python-requests/2.3.0 CPython/2.7.3 Darwin/13.1.0",
            "Connection": "close",
            "Content-Type": "application/json"
        },
        "json": {
            "last": "White",
            "first": "Chris"
        },
        "data": "{\"last\": \"White\", \"first\": \"Chris\"}"
    }
    http://httpbin.org/>
