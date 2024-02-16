# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import os
import ssl
import json
import errno
import urllib.request
import urllib.parse
import urllib.error
import socket
import logging
import tempfile
import requests
import mimetypes
import requests.exceptions
import warnings
from os.path import basename
from xml.etree import ElementTree
from requests.utils import default_user_agent
from requests.adapters import HTTPAdapter
from requests.structures import CaseInsensitiveDict
from requests.packages.urllib3.util import parse_url
from requests.packages.urllib3.poolmanager import PoolManager

from steelscript.common.exceptions import RvbdException, RvbdHTTPException, \
    RvbdConnectException

logger = logging.getLogger(__name__)
rest_logger = logging.getLogger('REST')

# TODO: Fix properly. Temporary following warning will just be logged "InsecureRequestWarning: Unverified HTTPS request is being made to host 'beta32rle2aanet.aternity-ims.net'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings"
logging.captureWarnings(True)

warnings.catch_warnings()
warnings.simplefilter('once')


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
        for (k, v) in data.items():
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


def test_tcp_conn(dest, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        rcode = s.connect_ex((dest, port))
    except Exception as e:
        raise RvbdConnectException("Exception raised in test_tcp_conn({2}, "
                                   "{3}) type: {0}, message {1}"
                                   "".format(type(e), str(e), dest, port))
    finally:
        s.close()

    if rcode == 0:
        return True
    else:
        err_name = errno.errorcode.get(rcode, "UnknownError")
        raise RvbdConnectException("Socket errno raised on connection "
                                   "attempt: {0}".format(err_name),
                                   errno=rcode,
                                   errname=err_name)


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
        self.cookies = None

        # store last full response
        self.response = None

        logger.debug("Connection initialized for %s" % self.hostname)

    def __repr__(self):
        return '<{0} to {1}>'.format(self.__class__.__name__, self.hostname)

    def __del__(self):
        # cleanup after ourselves
        self.conn.close()

    def get_url(self, path):
        """ Returns a fully qualified URL given a path. """
        return urllib.parse.urljoin(self.hostname, path)

    def set_user_agent(self, extra=None):
        #TODO: replace hardcoded version (but without adding a dependency on the distribution package version)
        version = '3.0'
        ua = '%s SteelScript/%s' % (default_user_agent(), version)
        if extra:
            ua = '%s %s' % (ua, extra)
        self.conn.headers['User-Agent'] = ua

    def request(self, method, path, body=None, params=None,
                extra_headers=None, **kwargs):
        return self._request(method, path, body, params,
                             extra_headers, **kwargs)

    def _request(self, method, path, body=None, params=None,
                 extra_headers=None, raw_json=None, stream=False,
                 files=None, **kwargs):
        p = parse_url(path)
        if not p.host:
            path = self.get_url(path)
        try:
            rest_logger.info('%s %s' % (method, str(path)))
            if params:
                rest_logger.info('Parameters: ')
                for k, v in params.items():
                    rest_logger.info('... %s: %s' % (k, v))

            if self.REST_DEBUG >= 1 and extra_headers:
                rest_logger.info('Extra request headers: ')
                for k, v in extra_headers.items():
                    rest_logger.info('... %s: %s' % (k, v))
            if self.REST_DEBUG >= 2 and body:
                rest_logger.info('Request body: ')
                if raw_json:
                    if path.endswith('login'):
                        debug_body = json.dumps(
                            scrub_passwords(raw_json), indent=2,
                            cls=self.JsonEncoder)
                    else:
                        logger.debug("raw_json: %s" % raw_json)
                        debug_body = json.dumps(
                            raw_json, indent=2, cls=self.JsonEncoder)
                else:
                    if files and isinstance(body, dict):
                        debug_body = json.dumps(body, indent=2,
                                                cls=self.JsonEncoder)
                    else:
                        debug_body = body
                lines = debug_body.split('\n')
                for line in lines[:self.REST_BODY_LINES]:
                    rest_logger.info('... %s' % line)
                if len(lines) > self.REST_BODY_LINES:
                    rest_logger.info('... <truncated %d lines>'
                                     % (len(lines) - 20))

            r = self.conn.request(method, path, data=body, params=params,
                                  headers=extra_headers,
                                  stream=stream,
                                  files=files,
                                  cookies=self.cookies, **kwargs)

            if r.request.url != path:
                rest_logger.info('Full URL: %s' % r.request.url)

            if self.REST_DEBUG >= 1 and extra_headers:
                rest_logger.info('Request headers: ')
                for k, v in scrub_passwords(r.request.headers).items():
                    rest_logger.info('... %s: %s' % (k, v))

            if stream:
                rest_logger.info('Response Status %s, streaming content' %
                                 r.status_code)
            else:
                rest_logger.info('Response Status %s, %d bytes' %
                                 (r.status_code, len(r.content)))

            if self.REST_DEBUG >= 1 and extra_headers:
                rest_logger.info('Response headers: ')
                for k, v in r.headers.items():
                    rest_logger.info('... %s: %s' % (k, v))

            if self.REST_DEBUG >= 2 and not stream and r.text:
                rest_logger.info('Response body: ')
                try:
                    debug_body = json.dumps(r.json(), indent=2,
                                            cls=self.JsonEncoder)
                    lines = debug_body.split('\n')
                except:
                    lines = r.text.split('\n')

                for line in lines[:self.REST_BODY_LINES]:
                    rest_logger.info('... %s' % line)
                if len(lines) > self.REST_BODY_LINES:
                    rest_logger.info('... <truncated %d lines>'
                                     % (len(lines) - 20))

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
                                  params=params, headers=extra_headers,
                                  cookies=self.cookies, files=files)

        # check if good status response otherwise raise exception
        if not r.ok:
            exc = RvbdHTTPException(r, r.text, method, path)
            if (self._reauthenticate_handler is not None and
                exc.error_id in ('AUTH_REQUIRED',
                                 'AUTH_INVALID_SESSION',
                                 'AUTH_EXPIRED_TOKEN',
                                 'AUTH_INVALID_CREDENTIALS')):
                logger.debug('session timed out -- reauthenticating')
                # clean any stale cookies from session
                self._clear_cookies()
                handler = self._reauthenticate_handler
                self._reauthenticate_handler = None
                handler()
                logger.debug('session reauthentication succeeded -- retrying')
                r = self._request(method, path, body=body, params=params,
                                  extra_headers=extra_headers,
                                  raw_json=raw_json,
                                  files=files, **kwargs)
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

    def _clear_cookies(self):
        self.conn.headers.pop('Cookie', None)
        if self.cookies:
            self.cookies.clear_session_cookies()
        self.conn.cookies.clear_session_cookies()

    def _prepare_headers(self, headers):
        if headers:
            return CaseInsensitiveDict(headers)
        else:
            return CaseInsensitiveDict()

    def json_request(self, method, path, body=None, params=None,
                     extra_headers=None, raw_response=False):
        """ Send a JSON request and receive JSON response. """

        extra_headers = self._prepare_headers(extra_headers)
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
            data = None  # no data
        else:
            data = json.loads(r.text)

        if raw_response:
            return data, r
        return data

    def xml_request(self, method, path, body=None,
                    params=None, extra_headers=None, raw_response=False):
        """Send an XML request to the host.

        The Content-Type and Accept headers are set to text/xml.  In addition,
        any response will be XML-decoded as an xml.etree.ElementTree.  The body
        is assumed to be an XML encoded text string and is inserted into the
        HTTP payload as-is.
        """
        extra_headers = self._prepare_headers(extra_headers)
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

    def urlencoded_request(self, method, path, body=None, params=None,
                           extra_headers=None, raw_response=False):
        """Send a request with url encoded parameters in body"""
        extra_headers = self._prepare_headers(extra_headers)
        extra_headers['Content-Type'] = 'application/x-www-form-urlencoded'
        extra_headers['Accept'] = 'application/json'

        body = urllib.parse.urlencode(body)

        return self._request(method, path, body, params, extra_headers)

    def upload_file(self, path, files, body=None, params=None,
                    extra_headers=None, file_headers=None, field_name='file',
                    raw_response=False):
        """
        Executes a POST to upload a file or files.

        :param path: The full or relative URL of the file upload API
        :param files: Can be a string that is the full path to a file to be
               uploaded OR it can be a tuple/list of strings that are each the
               full path to a file to be uploaded.
        :param body: Optional body. If present must be a dictionary.
        :param params: optional URL params
        :param extra_headers: Optional headers
        :param file_headers: Optional headers to include with the multipart
               file data. Default is {'Expires': '0'}. Pass in an empty dict
               object if you would not like to include any file_headers in the
               multipart data.
        :param field_name: The name of the form field on the destination that
               will receive the posted multipart data. Default is 'file'
        :param raw_response: False (defualt) results in the function returning
               only the decoded JSON response present in the response body. If
               set to True then the funciton will return a tuple of the decoded
               JSON body and the full response object. Set to True if you
               want to inspect the result code or response headers.
        :return: See 'raw_response' for details on the returned data.
        """

        # the underlying request object will add the correct content type
        # header
        extra_headers = self._prepare_headers(extra_headers)
        extra_headers['Accept'] = 'application/json'

        # by default add a zero expiration header.
        if file_headers is None:
            file_headers = {'Expires': '0'}

        # body must be a dict object for this call.
        if (body is not None) and (not isinstance(body, dict)):
            raise RvbdException("The 'body' argument must either be None or a "
                                "dict")
        # Open all of the files
        xfiles = dict()
        if isinstance(files, str):
            try:
                xfiles[basename(files)] = {'file': open(files, 'rb')}
            except IOError:
                raise RvbdException("Could not open '{0}' for read in binary "
                                    "mode. Please check path.".format(files))
        elif isinstance(files, (list, tuple)):
            for file in files:
                try:
                    xfiles[basename(file)] = {'file': open(file, 'rb')}
                except IOError:
                    raise RvbdException("Could not open '{0}' for read in "
                                        "binary mode. Please check path."
                                        "".format(file))
        else:
            raise RvbdException("upload_file 'files' argument must be a "
                                "string or list type (list, tuple). {0} is "
                                "not a valid files argument."
                                "".format(type(files)))

        # build the multipart content from the files
        if len(xfiles) == 1:
            # single file is a dict object
            for f in xfiles:
                mtype, _ = mimetypes.guess_type(f)
                if mtype and list(file_headers.keys()):
                    req_files = {field_name: (f,
                                              xfiles[f]['file'],
                                              mtype,
                                              file_headers)}
                elif mtype and not list(file_headers.keys()):
                    req_files = {field_name: (f,
                                              xfiles[f]['file'],
                                              mtype)}
                else:
                    req_files = {field_name: (f,
                                              xfiles[f]['file'])}

        elif len(xfiles) > 1:
            # multiple files is a list
            req_files = list()
            for f in xfiles:
                mtype, _ = mimetypes.guess_type(f)
                if mtype and list(file_headers.keys()):
                    req_files.append((field_name, (f,
                                                   xfiles[f]['file'],
                                                   mtype,
                                                   file_headers)
                                      ))
                elif mtype and not list(file_headers.keys()):
                    req_files.append((field_name, (f,
                                                   xfiles[f]['file'],
                                                   mtype)
                                      ))
                else:
                    req_files.append((field_name, (f,
                                                   xfiles[f]['file'])
                                      ))
        else:
            raise RvbdException("At least one valid file required. Files was: "
                                "{0}".format(files))

        # send the files
        r = self._request("POST", path, body, params, extra_headers,
                          files=req_files)

        if r.status_code == 204 or len(r.content) == 0:
            data = None  # no data
        else:
            data = json.loads(r.text)

        if raw_response:
            return data, r
        return data

    def upload(self, path, data, method="POST", params=None,
               extra_headers=None):
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
                # last case, we got a full path of a file
                directory, filename = os.path.split(path)

        # Initiate the request
        # XXX Handle cases where a Keep-Alive header is passed back in Response
        # include "Connection: Close" as part of the request header
        # otherwise a Keep-Alive response from the server will hang and block
        # our connection until the system timeout (defaults to 100sec in one
        # implementation)
        #
        extra_headers = self._prepare_headers(extra_headers)
        extra_headers['Connection'] = 'Close'
        r = self._request(method, url, None, params, extra_headers,
                          stream=True)

        try:
            # Check if the user specified a file name
            if filename is None:
                # Retrieve the file name form the HTTP header
                filename = r.headers.get('Content-Disposition', None)
                if filename is not None:
                    filename = filename.split('=')[1]

            if not filename:
                raise ValueError("{0} is not a valid path. Specify a full path"
                                 " for the file to be created".format(path))
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
