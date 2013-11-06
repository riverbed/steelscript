# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.


"""
This module contains the Connection class, which is the underlying object
for communicating with a device via REST.
"""

from __future__ import absolute_import

import httplib
import socket
import errno
import logging
import xml.etree.ElementTree as ElementTree
import json
import copy
import urllib
import shutil
import os
import re
import tempfile

from rvbd.common.exceptions import RvbdException, RvbdHTTPException
from rvbd.common.utils import DictObject
from rvbd.common.http_pool import ConnectionPool

__all__ = ['Connection']

logger = logging.getLogger(__name__)


class Connection(object):
    """This class handles all HTTP/HTTPS communication with a device,
    including connection management, connection pooling, XML and JSON
    requests and responses.  This class is normally instantiated
    by a `Service` object, but may be used separately as needed.

    Authentication is not handled directly by this class.  The caller
    must set the appropriate headers for authentication either
    using the `extra_headers` parameter or by calling the `add_headers`
    method.  The latter will affect all subsequent requests.
    """

    HTTPLIB_DEBUGLEVEL = 0
    DEBUG_MSG_BODY = 0

    def __init__(self, hostname, port=None, force_ssl=True, pool_size=1,
                 reauthenticate_handler=None, test_resource=None):
        """Create a connection to the requested host.

        `hostname` is the name or IP address of the device to connect to

        `port` is the TCP port to use for the connection.  This may be either
            a single port or a list of ports to try.  By default, ports
            443 and 80 will be tried.

        `force_ssl` when set to True will only allow SSL based connections.
            If False, only allow non-SSL connections.  If set to None
            (the default) try SSL first, then try non-SSL.

        `pool_size` is the number of simultaneous connections to establish as
            part of a connection pool.  Default is 1.

        `reauthenticate_handler`, if set, should contain callable that is
         invoked if a request returns a session expiration error.
         If the call succeeds, then the request is retried once.
        """

        self.hostname = hostname
        if port is None:
            self.ports = [443, 80]
        elif isinstance(port, list):
            self.ports = port
        else:
            self.ports = [port]
        self.force_ssl = force_ssl

        self.conn = None
        self.port = None
        self.ssl = None
        self.test_resource = test_resource

        self._pool_size = pool_size
        self._reauthenticate_handler = reauthenticate_handler

        self._headers = {}

        logger.debug(
            "Connection with port=%s force_ssl=%s" %
            (port, force_ssl))

        for p in self.ports:
            if self._tryconnect(p):
                break
        if self.port is None:
            raise RvbdException(
                'cannot connect to %s on port(s) %s' %
                (self.hostname,
                 self.ports))

    def __repr__(self):
        return '<{0} to {1}>'.format(self.__class__.__name__, self.hostname)

    def _reset_connection(self, hostname, port, ssl):
        logger.debug("Attempting to connect to %s:%s, ssl %s, pool %d" %
                     (hostname, port, ssl, self._pool_size))

        if self._pool_size > 1:
            self.conn = ConnectionPool(hostname, port=port,
                                       use_ssl=ssl, pool_size=self._pool_size)
        else:
            if ssl:
                cls = httplib.HTTPSConnection
            else:
                cls = httplib.HTTPConnection
            self.conn = cls(hostname, port=port)
            self.conn.connect()

    def _tryconnect(self, port):
        """Try connecting to the given port, both with and without SSL.

        Upon success, set self.port and self.ssl and return True.

        If a connection cannot be established, return False.
        Any other exceptions (eg, a bogus hostname) are raised
        to the caller.

        Note that this method does not authenticate to the appliance.
        """

        # this helper function does all the work of trying to connect
        # and determine the protocol information on the given port
        # with a given ssl setting.
        #
        # it abstracts the details of distinguishing errors to using
        # the wrong ssl setting from "real" errors so the main logic
        # below can simply make a guess about the right ssl setting and
        # simply call this function again if it guesses wrong.
        #
        class SSLMismatch(Exception):
            pass

        def attempt(port, ssl):
            try:
                self._reset_connection(self.hostname, port, ssl)
                # Test the connection with *any* resource -- it need not be
                # a valid resource, just something that will verify
                # connectivity
                if self.test_resource:
                    rsc = "/foobar" if self.test_resource \
                                    is True else self.test_resource
                    self.conn.request("GET", rsc)
                    resp = self.conn.getresponse()

                    if resp.status == 302:
                        loc = resp.getheader("location", "")
                        if loc and re.match("^https", loc):
                            raise SSLMismatch()

                    if (self.test_resource is not True) and (resp.status == 404):
                        # If test resource fail the connection if the test resource
                        # is not found
                        return False

                    # drain the response
                    resp.read()

                self.ssl = ssl
                self.port = port

                if self.HTTPLIB_DEBUGLEVEL > 0:
                    logger.debug("Setting HTTPLIB_DEBUGLEVEL to %d" % self.HTTPLIB_DEBUGLEVEL)
                    self.conn.set_debuglevel(self.HTTPLIB_DEBUGLEVEL)

                logger.info("Connection established to %s://%s:%s" %
                            (("https" if ssl else "http"), self.hostname, self.port))
                return True

            except httplib.BadStatusLine:
                if not self.ssl:
                    # oops.. the server is expecting SSL and we're not
                    raise SSLMismatch()

                # something else...
                raise

            except socket.gaierror:
                logger.error("Not a valid host %s" % self.hostname)
                raise ValueError('{0} is not a valid address or host'.format(self.hostname))

            except socket.error, e:

                # if nothing is listening on the given port then we
                # can immediately return failure.
                if e.errno == errno.ECONNREFUSED:
                    logger.debug("Connection refused")
                    return False
                if ssl and e.errno == errno.EPERM:
                    # we're trying to use ssl on a non-ssl port...
                    raise SSLMismatch()

                # something else...
                raise

            return False

        # self.force_ssl is tri-state: True:use ssl, False:don't use ssl, None: try with/without ssl
        if self.force_ssl is not None:
            try:
                return attempt(port, self.force_ssl)
            except SSLMismatch:
                return False

        # we don't know if we're supposed to use ssl or not.  make a
        # guess about what to try and if it fails, try the opposite.
        ssl = port in (443, 61898)
        try:
            return attempt(port, ssl)
        except SSLMismatch:
            try:
                return attempt(port, not ssl)
            except SSLMismatch:
                return False

    def _request(self, urlpath, method, body, headers):
        """Internal request method that will retry on failure as directed."""
        retry = True
        while True:
            try:
                logger.debug('Issuing %s request to: %s' % (method, str(urlpath)))
                if body is not None and '"password":' in repr(body):
                    clean_body = '<username and password hidden>'
                    self.conn.set_debuglevel(0)
                else:
                    clean_body = body
                logger.debug('Values are: \n headers: {0} \n body: {1}'.format(headers, clean_body))
                self.conn.request(method, urlpath, body=body, headers=headers)

                # reset debug level
                self.conn.set_debuglevel(self.HTTPLIB_DEBUGLEVEL)
                resp = self.conn.getresponse()
                return resp
                
            except httplib.ResponseNotReady, e:
                # User probably forgot to drain the response
                raise RvbdException('Cannot send request, exception httplib.ResponseNotReady - '
                                    'usually means response from last request was not drained with read()')

            except httplib.CannotSendRequest, e:
                if not retry or self._pool_size != 1:
                    raise e

            except httplib.BadStatusLine, e:
                # stupid httplib is supposed to put the status line in e.line
                # which should be the empty string when the server closes
                # the connection.  but the BadStausLine constructor uses
                # repr(line) for the empty string so we explicitly test for
                # it here.  gag.
                if (not retry) or (e.line != "''"):
                    raise e

            except:
                raise

            retry = False
            # If we got this far, we're going to retry
            logger.info('Resetting connection')
            self._reset_connection(self.hostname, self.port, self.ssl)
                    
    def request(self, urlpath, method='GET', body='', params=None,
                extra_headers=None):
        """Send a generic HTTP request to the host.  

        On success, the httplib response object is returned.  Any
        pending data must be read by the caller.

        On failure, an exception is raised.  Any data on the response object is
        drained before failing.

        `urlpath` is the full path of the resource from the initial slash.
            For example "/api/common/1.0/ping"
            
        `method` is the HTTP method to use.  Default is GET.

        `body` is the full text to send as the body of the message as is.

        `params` is a dictionary of URL parameters to attach to the request.
            The keys and values will be urlencoded.

        `extra_headers` is a dictionary of additional HTTP headers to send
            with the request.
        """

        if params:
            urlpath = "%s?%s" % (urlpath, urllib.urlencode(params))

        logger.debug("http %s on url %s" % (method, urlpath))

        # XXXCJ - need to "lowercase" all headers to make sure there are
        # no duplicates due to changed capitalization
        # ie, Content-type vs Content-Type???
        headers = copy.copy(self._headers)
        if extra_headers is not None:
            headers.update(extra_headers)

        #fix for bug http://bugs.python.org/issue14721
        if body == '' or body is None:
            if 'content-length' not in headers:
                headers['content-length'] = "0"
        elif method == 'GET':
            raise ValueError("data cannot be included for %s requests" % method)

        # XXXWP - We can't set  the  content  length  calling  len(body)  since
        # body might be a python file object and this would raise an exception.
        # In thise case we let httplib setting the content length in the method
        # HTTPConnection._set_content_length()
        # else:
        #     headers['content-length'] = str(len(body))

        if isinstance(body, str) and self.DEBUG_MSG_BODY > 0:
            trunc = ''
            if len(body) > self.DEBUG_MSG_BODY:
                trunc = ' (truncated)'

            logger.debug('Request body:\n%s%s\n' %
                         (body[:self.DEBUG_MSG_BODY], trunc))

        self.last_http_response = None
        res = self._request(urlpath, method, body, headers)
        logger.debug('Response status: %d' % res.status)
        self.last_http_response = res

        if not (200 <= res.status <= 399):
            # have to read the response (even if it's an error)
            # so that we don't mess up the next request on the same connection
            data = res.read()

            # Try to parse the response as either an XML or JSON encoded error
            exc = RvbdHTTPException(res, data, method, urlpath)

            # If the session expired and there is a configured handler
            # to reauthenticate, try to do so. Temporarily clear the
            # handler to avoid infinite recursion or multiple attempts
            # to reauthenticate.
            if (self._reauthenticate_handler is not None and
                exc.error_id in ('AUTH_INVALID_SESSION', 'AUTH_EXPIRED_TOKEN')):

                logger.debug('session timed out -- reauthenticating')
                handler = self._reauthenticate_handler
                self._reauthenticate_handler = None
                handler()

                # Reissue the request. The params are already encoded
                # into the urlpath so don't include them again
                logger.debug('session reauthentication succeeded -- retrying operation')
                res = self.request(urlpath, method, body, params=None, extra_headers=extra_headers)
                if (200 <= res.status <= 399):
                    logger.info('operation retry success!')
                    self._reauthenticate_handler = handler
                    return res
                else:
                    # Not reached!
                    logger.error('unreachable code path in connection.request after retry')
                    assert False
            else:
                raise exc

        return res

    def xml_request(self, urlpath, method='GET', body='', params=None,
                    extra_headers=None):
        """Send an XML request to the host.  
        
        This is similar to `request` except the Content-Type and Accept headres
        are set to text/xml.  In addition, any response will be XML-decoded as
        an xml.etree.ElementTree.  The body is assumed to be an XML encoded
        text string and is inserted into the HTTP payload as-is.
        """

        # XXX/demmer for consistency this should handle the case where
        # body is an ElementTree.Element
        if extra_headers is None:
            extra_headers = {}

        extra_headers['Content-Type'] = 'text/xml'
        extra_headers['Accept'] = 'text/xml'

        resp = self.request(urlpath, method=method, body=body,
                            params=params, extra_headers=extra_headers)
        t = resp.getheader('Content-type')
        if t != 'text/xml':
            raise RvbdException('unexpected content type %s' % t)

        tree = ElementTree.parse(resp).getroot()

        if self.DEBUG_MSG_BODY:
            logger.debug('Response body:\n' + str(tree) + '\n')

        return tree

    class JsonEncoder(json.JSONEncoder):
        def default(self, obj):
            try:
                res = super(Connection.JsonEncoder, self).default(obj)
            except TypeError:
                try:
                    res = obj.to_dict()
                except AttributeError:
                    res = obj.__dict__

            return res

    def json_request(self, urlpath, method='GET', data=None, params=None,
                     extra_headers=None):
        """Send a JSON request to the host.
        
        For POST/PUT requests, the `data` parameter will be JSON-encoded before
        transmission.  For all requests, the response is JSON-decoded using the
        DictObject class before returning.
        """

        if data is not None:
            body = json.dumps(data, cls=self.JsonEncoder)
        else:
            body = ''

        if extra_headers is None:
            extra_headers = {}

        extra_headers['Content-Type'] = 'application/json'
        extra_headers['Accept'] = 'application/json'

        resp = self.request(urlpath, method=method, body=body,
                            params=params, extra_headers=extra_headers)

        data = resp.read()

        if self.DEBUG_MSG_BODY > 0:
            trunc = ''
            if len(data) > self.DEBUG_MSG_BODY:
                trunc = ' (truncated)'

            logger.debug('Response body:\n%s%s\n' %
                         (data[:self.DEBUG_MSG_BODY], trunc))

        # In some cases the device may return a 200 with no actual data
        # if it needs to set some headers in the response that modify
        # the client behavior (e.g. Rvbd-Shark-Status), so check for
        # both status code of 204 or an empty data response
        if resp.status == 204 or len(data) == 0:
            return  # no data

        t = resp.getheader('Content-type')
        if t is not None and t.find('application/json'):
            raise RvbdException('unexpected content type %s' % t)

        return json.loads(data, object_hook=DictObject.create_from_dict)

    def upload(self, urlpath, data, method="POST", params=None, extra_headers=None):
        """Upload raw data to the given URL path with the given content type.

        `data` may be either a string or a python file object.

        `extra_headers` is a dictionary of additional HTTP headers to send
            with the request (e.g.  Content-Type, Content-Disposition)

        `params` is a dictionary of URL parameters to attach to the request.
            The keys and values will be urlencoded.

        `method` defaults to "POST", but can be overridden if the API requires another
            method such as "PUT" to be used instead.

        Returns location information if resource has been created,
        otherwise the response body (if any).
        """
        resp = self.request(urlpath, method, data, params=params,
                            extra_headers=extra_headers)
        data = resp.read()
        if resp.status == 204:
            return  # no data
        elif resp.status == 201:
            # created resource
            return {'Location-Header': resp.getheader('location', '')}
        return data

    def download(self, urlpath, path=None, overwrite=False, method='GET', extra_headers=None, params=None):
        """Download a file from a remote URI and save it to a local path.
        
        `urlpath` is the url of the file to download.

        `path` is an optional path on the local filesystem to save the downloaded file.
        It can be:

            - a complete path
            - a directory

        In the first case the file will have the specified name and extension. In the second case
        the filename will be retrieved by the 'Content-Disposition' HTTP header.
        If a path cannot be determined, a ValueError is raised.

        `overwrite` if True will save the downloaded file to `path` no matter if the file
                    already exists.
        
        `method` is the HTTP method used for the request.
        
        `extra_headers` is a dictionary of headers to use for the request.

        `params` is a dictionary of parameters for the request.
        """
        
        filename = None

        # try to determine the filename
        if path is None:
            # we didn't got a path from, create a temp directory to
            # store the file
            directory = tempfile.mkdtemp()
        else:
            # we got a path which is a directory maybe, check that it's valid
            if os.path.isdir(path):
                # it's valid, we have a directory to store the file in
                directory = path
            elif path[-1] == os.sep:
                # we got a path which is a directory that doesn't exists
                raise ValueError("{0} directory does not exists, create it first".format(path))
            else:
                #last case, we got a full path of a file
                directory, filename = os.path.split(path)

        # Get request
        resp = self.request(urlpath, method=method, params=params, extra_headers=extra_headers)

        # Check if the user specified a file name
        if filename is None:
            # Retrieve the file name form the HTTP header
            filename = resp.getheader('Content-Disposition').split('=')[1]

        if not filename:
            raise ValueError("{0} is not a valid path. "
                             "Specify a full path for the file to be created".format(path))
        # Compose the path
        path = os.path.join(directory, filename)

        # Check if the local file already exists
        if os.path.isfile(path) and not overwrite:
            raise RvbdException('the file %s already exists' % path)

        # Open the local file
        with open(path, 'wb') as fd:
            # Save the remote file to the local file
            shutil.copyfileobj(resp, fd)
        return path

    def add_headers(self, headers):
        """Add the dictionary HEADERS to the list of customer headers for all requests"""
        self._headers.update(headers)

    def del_headers(self, headers):
        """Drop any custom headers in the list of header names in HEADERS"""
        for h in headers:
            if h in self._headers:
                del self._headers[h]
