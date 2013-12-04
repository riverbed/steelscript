# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript-portal/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.

import os
import ssl
import json
import shutil
import httplib
import logging
import tempfile
import urlparse
from xml.etree import ElementTree

import requests
import requests.exceptions
from requests.adapters import HTTPAdapter
from requests.structures import CaseInsensitiveDict
from requests.packages.urllib3.util import parse_url
from requests.packages.urllib3.poolmanager import PoolManager

from rvbd.common.exceptions import RvbdException, RvbdHTTPException

logger = logging.getLogger(__name__)


class SSLAdapter(HTTPAdapter):
    """ An HTTPS Transport Adapter that uses an arbitrary SSL version. """
    # handle https connections that don't like to negotiate
    # see https://lukasa.co.uk/2013/01/Choosing_SSL_Version_In_Requests/
    def __init__(self, ssl_version=None, **kwargs):
        self.ssl_version = ssl_version

        super(SSLAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=self.ssl_version)


class Connection(object):
    """ Handle authentication and communication to remote machines. """

    HTTPLIB_DEBUGLEVEL = 0
    DEBUG_MSG_BODY = 0

    def __init__(self, hostname, auth=None, port=None, verify=True,
                 reauthenticate_handler=None):
        """ Initialize new connection and setup authentication

            `hostname` - include protocol, e.g. "https://host.com"
            `auth` - authentication object, see below
            `port` - optional port to use for connection
            `verify` - require SSL certificate validation.

            Authentication:
            For simple basic auth, passing a tuple of (user, pass) is
            sufficient as a shortcut to an instance of HTTPBasicAuth.
            This auth method will trigger a check  to ensure
            the protocol is using SSL to connect (though cert verification
            may still be turned off to avoid errors with self-signed certs).

            OAuth2 will require the ``requests-oauthlib`` package and
            an instance of the `OAuth2Session` object.

            netrc config files will be checked if auth is left as None.
            If no authentication is provided for the hostname in the
            netrc file, or no file exists, an error will be raised
            when trying to connect.
        """
        p = parse_url(hostname)
        if not p.scheme:
            msg = 'Scheme must be provided (e.g. https:// or http://).'
            raise RvbdException(msg)
        else:
            if p.port and port and p.port != port:
                raise RvbdException('Mismatched ports provided.')
            elif not p.port and port:
                hostname = hostname + ':' + str(port)

        self.hostname = hostname
        self._ssladapter = False

        if self.HTTPLIB_DEBUGLEVEL > 0:
            self.set_debuglevel()

        self.conn = requests.session()
        self.conn.auth = auth
        self.conn.verify = verify
        self._reauthenticate_handler = reauthenticate_handler

        # store last full response
        self.response = None

        logger.debug("Connection initialized for %s" % self.hostname)

    def __repr__(self):
        return '<{0} to {1}>'.format(self.__class__.__name__, self.hostname)

    def set_debuglevel(self, level=None):
        if level is None:
            level = self.HTTPLIB_DEBUGLEVEL

        logger.debug("Setting HTTPLIB_DEBUGLEVEL to %d" % level)

        if parse_url(self.hostname).scheme == 'https':
            httplib.HTTPSConnection.debuglevel = level
        else:
            httplib.HTTPConnection.debuglevel = level

    def get_url(self, uri):
        """ Returns a fully qualified URL given a URI. """
        return urlparse.urljoin(self.hostname, uri)

    def _request(self, method, uri, body=None, params=None,
                 extra_headers=None, **kwargs):
        p = parse_url(uri)
        if not p.host:
            uri = self.get_url(uri)

        try:
            r = self.conn.request(method, uri, data=body, 
                                  params=params, headers=extra_headers, **kwargs)
        except (requests.exceptions.SSLError, 
                requests.exceptions.ConnectionError):
            if self._ssladapter:
                # If we've already applied an adapter, this is another problem
                raise

            # Otherwise, mount adapter and retry the request
            self.conn.mount('https://', SSLAdapter(ssl.PROTOCOL_TLSv1))
            self._ssladapter = True
            logger.debug('SSL error -- retrying with TLSv1')
            r = self.conn.request(method, uri, data=body,
                                  params=params, headers=extra_headers)

        self.response = r

        # check if good status response otherwise raise exception
        if not r.ok:
            exc = RvbdHTTPException(r, r.text, method, uri)
            if (self._reauthenticate_handler is not None and
                exc.error_id in ('AUTH_INVALID_SESSION',
                                 'AUTH_EXPIRED_TOKEN')):
                logger.debug('session timed out -- reauthenticating')
                handler = self._reauthenticate_handler
                self._reauthenticate_handler = None
                handler()
                logger.debug('session reauthentication succeeded -- retrying')
                r = self._request(method, uri, body, params,
                                  extra_headers, **kwargs)
                # successful connection, reset token if previously unset
                self._reauthenticate_handler = handler
                return r

            else:
                raise exc

        return r

    class JsonEncoder(json.JSONEncoder):
        """ Handle more object types if first encoding doesn't work. """
        def default(self, obj):
            try:
                res = super(Connection.JsonEncoder, self).default(obj)
            except TypeError:
                try:
                    res = obj.to_dict()
                except AttributeError:
                    res = obj.__dict__
            return res

    def json_request(self, method, uri, body=None, 
                     params=None, extra_headers=None):
        """ Send a JSON request and receive JSON response. """
        if extra_headers:
            extra_headers = CaseInsensitiveDict(extra_headers)
        else:
            extra_headers = CaseInsensitiveDict()
        extra_headers['Content-Type'] = 'application/json'
        extra_headers['Accept'] = 'application/json'

        if body is not None:
            body = json.dumps(body, cls=self.JsonEncoder)
        else:
            body = ''

        r = self._request(method, uri, body, params, extra_headers)
        if r.status_code == 204 or len(r.content) == 0:
            return None  # no data
        return r.json()

    def xml_request(self, method, uri, body=None, 
                    params=None, extra_headers=None):
        """Send an XML request to the host.  
        
        The Content-Type and Accept headers are set to text/xml.  In addition,
        any response will be XML-decoded as an xml.etree.ElementTree.  The body
        is assumed to be an XML encoded text string and is inserted into the
        HTTP payload as-is.
        """
        if extra_headers:
            extra_headers = CaseInsensitiveDict(extra_headers)
        else:
            extra_headers = CaseInsensitiveDict()

        extra_headers['Content-Type'] = 'text/xml'
        extra_headers['Accept'] = 'text/xml'

        r = self._request(method, uri, body, params, extra_headers)

        t = r.headers.get('Content-type', None)
        if t != 'text/xml':
            raise RvbdException('unexpected content type %s' % t)

        tree = ElementTree.parse(r).getroot()

        if self.DEBUG_MSG_BODY:
            logger.debug('Response body:\n' + str(tree) + '\n')

        return tree

    def upload(self, uri, data, method="POST", params=None, extra_headers=None):
        """Upload raw data to the given URL path with the given content type.

        `data` may be either a string or a python file object.

        `extra_headers` is a dictionary of additional HTTP headers to send
            with the request (e.g.  Content-Type, Content-Disposition)

        `params` is a dictionary of URL parameters to attach to the request.
            The keys and values will be urlencoded.

        `method` defaults to "POST", but can be overridden if the API requires
            another method such as "PUT" to be used instead.

        Returns location information if resource has been created,
        otherwise the response body (if any).
        """
        r = self._request(method, uri, data, params=params,
                            extra_headers=extra_headers)
        if r.status_code == 204:
            return  # no data
        elif r.status_code == 201:
            # created resource
            return {'Location-Header': r.headers.get('location', '')}
        return r.text

    def download(self, uri, path=None, overwrite=False, method='GET',
                 extra_headers=None, params=None):
        """Download a file from a remote URI and save it to a local path.
        
        `uri` is the url of the file to download.

        `path` is an optional path on the local filesystem to save the 
        downloaded file.  It can be:

            - a complete path
            - a directory

        In the first case the file will have the specified name and extension.
        In the second case the filename will be retrieved by the
        'Content-Disposition' HTTP header.  If a path cannot be determined, a
        ValueError is raised.

        `overwrite` if True will save the downloaded file to `path` no matter
            if the file already exists.
        
        `method` is the HTTP method used for the request.
        
        `extra_headers` is a dictionary of headers to use for the request.

        `params` is a dictionary of parameters for the request.
        """
        
        filename = None

        # try to determine the filename
        if path is None:
            directory = tempfile.mkdtemp()
        else:
            if os.path.isdir(path):
                directory = path
            elif path[-1] == os.sep:
                # we got a path which is a directory that doesn't exists
                msg = "{0} directory does not exist.".format(path)
                raise ValueError(msg)
            else:
                #last case, we got a full path of a file
                directory, filename = os.path.split(path)

        # Get request
        r = self._request(method, uri, None, params, extra_headers, stream=True)

        # Check if the user specified a file name
        if filename is None:
            # Retrieve the file name form the HTTP header
            filename = r.headers.get('Content-Disposition', None)
            if filename is not None:
                filename = filename.split('=')[1]

        if not filename:
            raise ValueError("{0} is not a valid path. Specify a full path "
                             "for the file to be created".format(path))
        # Compose the path
        path = os.path.join(directory, filename)

        # Check if the local file already exists
        if os.path.isfile(path) and not overwrite:
            raise RvbdException('the file %s already exists' % path)

        # Stream the remote file to the local file
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=2048):
                if chunk:
                    f.write(chunk)
            #f.write(r.content)
        return path

    def add_headers(self, headers):
        self.conn.headers.update(headers)
