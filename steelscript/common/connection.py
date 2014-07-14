# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import os
import ssl
import json
import httplib
import logging
import tempfile
import urlparse
from xml.etree import ElementTree

import requests
import requests.exceptions
from requests.utils import default_user_agent
from requests.adapters import HTTPAdapter
from requests.structures import CaseInsensitiveDict
from requests.packages.urllib3.util import parse_url
from requests.packages.urllib3.poolmanager import PoolManager
from pkg_resources import get_distribution

from steelscript.common.exceptions import RvbdException, RvbdHTTPException

logger = logging.getLogger(__name__)
rest_logger = logging.getLogger('REST')

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


def scrub_passwords(data):
    if hasattr(data, 'iteritems'):
        result = {}
        for (k,v) in data.iteritems():
            if k.lower() in ('password', 'authenticate', 'cookie'):
                result[k] = "********"
            else:
                result[k] = scrub_passwords(data[k])
        return result
    elif isinstance(data, list):
        result = []
        for i in data:
            result.append(scrub_passwords(i))
        return result
    else:
        return data


class Connection(object):
    """ Handle authentication and communication to remote machines. """

    REST_DEBUG = 0
    REST_BODY_LINES = 0

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

        if p.port and port and p.port != port:
            raise RvbdException('Mismatched ports provided.')
        elif not p.port and port:
            hostname = hostname + ':' + str(port)

        if not p.scheme:
            # default to https, except when port 80 specified
            if parse_url(hostname).port == '80':
                logger.info("Connection defaulting to 'http://' scheme.")
                hostname = 'http://' + hostname
            else:
                logger.info("Connection defaulting to 'https://' scheme.")
                hostname = 'https://' + hostname

        self.hostname = hostname
        self._ssladapter = False

        self.conn = requests.session()
        self.conn.auth = auth
        self.conn.verify = verify
        self._reauthenticate_handler = reauthenticate_handler
        self.set_user_agent()

        # store last full response
        self.response = None

        logger.debug("Connection initialized for %s" % self.hostname)

    def __repr__(self):
        return '<{0} to {1}>'.format(self.__class__.__name__, self.hostname)

    def get_url(self, path):
        """ Returns a fully qualified URL given a path. """
        return urlparse.urljoin(self.hostname, path)

    def set_user_agent(self, extra=None):
        version = get_distribution('steelscript').version
        ua = '%s SteelScript/%s' % (default_user_agent(), version)
        if extra:
            ua = '%s %s' % (ua, extra)
        self.conn.headers['User-Agent'] = ua

    def request(self, method, path, body=None, params=None,
                 extra_headers=None, **kwargs):
        return self._request(method, path, body, params, extra_headers, **kwargs)

    def _request(self, method, path, body=None, params=None,
                 extra_headers=None, raw_json=None, stream=False,
                 **kwargs):
        p = parse_url(path)
        if not p.host:
            path = self.get_url(path)

        try:
            rest_logger.info('%s %s' % (method, str(path)))
            if params:
                rest_logger.info('Parameters: ')
                for k,v in params.iteritems():
                    rest_logger.info('... %s: %s' % (k,v))


            #logger.debug('Body: %s' % (body))

            if self.REST_DEBUG >= 1 and extra_headers:
                rest_logger.info('Extra request headers: ')
                for k,v in extra_headers.iteritems():
                    rest_logger.info('... %s: %s' % (k,v ))
            if self.REST_DEBUG >=2 and body:
                rest_logger.info('Request body: ')
                if raw_json:
                    if (path.endswith('login')):
                        debug_body = json.dumps(scrub_passwords(raw_json), indent=2)
                    else:
                        debug_body = json.dumps(raw_json, indent=2)
                else:
                    debug_body = body
                lines = debug_body.split('\n')
                for line in lines[:self.REST_BODY_LINES]:
                    rest_logger.info('... %s' % line)
                if len(lines) > self.REST_BODY_LINES:
                    rest_logger.info('... <truncated %d lines>' % (len(lines) - 20))

            r = self.conn.request(method, path, data=body, params=params,
                                  headers=extra_headers, stream=stream, **kwargs)

            if r.request.url != path:
                rest_logger.info('Full URL: %s' % r.request.url)

            if self.REST_DEBUG >= 1 and extra_headers:
                rest_logger.info('Request headers: ')
                for k,v in scrub_passwords(r.request.headers).iteritems():
                    rest_logger.info('... %s: %s' % (k,v ))

            if stream:
                rest_logger.info('Response Status %s, streaming content' %
                                 (r.status_code))
            else:
                rest_logger.info('Response Status %s, %d bytes' %
                                 (r.status_code, len(r.content)))

            if self.REST_DEBUG >= 1 and extra_headers:
                rest_logger.info('Response headers: ')
                for k,v in r.headers.iteritems():
                    rest_logger.info('... %s: %s' % (k,v ))

            if self.REST_DEBUG >=2 and not stream and r.text:
                rest_logger.info('Response body: ')
                try:
                    debug_body = json.dumps(r.json(), indent=2)
                    lines = debug_body.split('\n')
                except:
                    lines = r.text.split('\n')

                for line in lines[:self.REST_BODY_LINES]:
                    rest_logger.info('... %s' % line)
                if len(lines) > self.REST_BODY_LINES:
                    rest_logger.info('... <truncated %d lines>' % (len(lines) - 20))

        except (requests.exceptions.SSLError,
                requests.exceptions.ConnectionError):
            if self._ssladapter:
                # If we've already applied an adapter, this is another problem
                raise

            # Otherwise, mount adapter and retry the request
            # See #152536 - Versions of openssl cause handshake failures
            self.conn.mount('https://', SSLAdapter(ssl.PROTOCOL_TLSv1))
            self._ssladapter = True
            logger.info('SSL error -- retrying with TLSv1')
            r = self.conn.request(method, path, data=body,
                                  params=params, headers=extra_headers)

        # check if good status response otherwise raise exception
        if not r.ok:
            exc = RvbdHTTPException(r, r.text, method, path)
            if (self._reauthenticate_handler is not None and
                exc.error_id in ('AUTH_INVALID_SESSION',
                                 'AUTH_EXPIRED_TOKEN')):
                logger.debug('session timed out -- reauthenticating')
                handler = self._reauthenticate_handler
                self._reauthenticate_handler = None
                handler()
                logger.debug('session reauthentication succeeded -- retrying')
                r = self._request(method, path, body, params,
                                  extra_headers, raw_json=raw_json, **kwargs)
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

    def json_request(self, method, path, body=None,
                     params=None, extra_headers=None, raw_response=False):
        """ Send a JSON request and receive JSON response. """
        if extra_headers:
            extra_headers = CaseInsensitiveDict(extra_headers)
        else:
            extra_headers = CaseInsensitiveDict()
        extra_headers['Content-Type'] = 'application/json'
        extra_headers['Accept'] = 'application/json'

        raw_json = body
        if body is not None:
            body = json.dumps(body, cls=self.JsonEncoder)
        else:
            body = ''

        r = self._request(method, path, body, params, extra_headers,
                          raw_json=raw_json)

        if r.status_code == 204 or len(r.content) == 0:
            return None  # no data
        if raw_response:
            return json.loads(r.text),r
        return json.loads(r.text)

    def xml_request(self, method, path, body=None,
                    params=None, extra_headers=None, raw_response=False):
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

        r = self._request(method, path, body, params, extra_headers)

        t = r.headers.get('Content-type', None)
        if t.find('text/xml') == -1:
            raise RvbdException('unexpected content type %s' % t)

        tree = ElementTree.fromstring(r.text.encode('ascii', 'ignore'))

        if raw_response:
            return tree, r

        return tree

    def upload(self, path, data, method="POST", params=None, extra_headers=None):
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
        r = self._request(method, path, data, params=params,
                          extra_headers=extra_headers)
        if r.status_code == 204:
            return  # no data
        elif r.status_code == 201:
            # created resource
            return {'Location-Header': r.headers.get('location', '')}
        return r.text

    def download(self, url, path=None, overwrite=False, method='GET',
                 extra_headers=None, params=None):
        """Download a file from a remote URI and save it to a local path.

        `url` is the url of the file to download.

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

        # Initiate the request
        # XXX Handle cases where a Keep-Alive header is passed back in Response
        # include "Connection: Close" as part of the request header
        # otherwise a Keep-Alive response from the server will hang and block
        # our connection until the system timeout (defaults to 100sec in one
        # implementation)
        #
        extra_headers = CaseInsensitiveDict(Connection='Close')
        r = self._request(method, url, None, params, extra_headers, stream=True)

        try:
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
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()

        finally:
            r.close()

        return path

    def add_headers(self, headers):
        self.conn.headers.update(headers)
