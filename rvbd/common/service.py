# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


"""
This module defines the Service class and associated authentication classes.
The Service class is not instantiated directly, but is instead subclassed
to implement handlers for particular REST namespaces.

For example, the Shark is based on Service using the "shark" namespace, and
will provide the necessary methods to interface with the REST resources available
within that namespace.

If a device or appliance implements multiple namespaces, each namespace will
be exposed by a separate child class.  The Cascade Express product implements
both the "profiler" and "shark" namespaces.  These will be exposed via Shark
and Profiler classes respectively, both based on the the Service class.
A script that interacts with both namespaces must instantiate two separate
objects.  
"""

from __future__ import absolute_import

import base64
import logging

import rvbd.common.connection
from rvbd.common.exceptions import RvbdException

from rvbd.common.api_helpers import APIVersion

__all__ = ['Service', 'Auth', 'UserAuth', 'OAuth', 'RvbdException']

logger = logging.getLogger(__name__)


class Auth(object):
    BASIC = 1
    COOKIE = 2
    OAUTH = 3


class UserAuth(object):
    """This class is used for both Basic and Cookie based authentication
    which rely on username and password."""
    def __init__(self, username, password, method=None):
        """Define an authentication method using `username` and `password`.
        By default this will be used for both Basic as well as Cookie
        based authentication methods (whichever is supported by the target).
        Authentication can be restricted by setting the `method` to
        either `Auth.BASIC` or `Auth.COOKIE`.
        """
        self.username = username
        self.password = password
        if method:
            self.methods = [method]
        else:
            self.methods = [Auth.BASIC, Auth.COOKIE]

    def __repr__(self):
        return '<UserAuth username: %s password: %s>' % (self.username, 
                                                         '*'*len(self.password))


class OAuth(object):
    """This class is used for OAuth based authentication with relies
    on an OAuth access token."""

    def __init__(self, access_code):
        """Define an OAuth based authentication method using `access_code`.
        The method is automatically set to `Auth.OAUTH`."""
        
        self.access_code = access_code
        self.methods = [Auth.OAUTH]


class Service(object):
    """This class is the main interface to interact with a device via REST
    and provides the following functionality:
    
    - Connection management
    - Resource requests and responses
    - Authentication
    - "common" resources

    A connection is established as soon as the an instance of this object
    is created.  Requests can be made via the `Service.conn` property.
    """
    def __init__(self, service, host=None, port=None, auth=None,
                 force_ssl=None, versions=None):
        """Establish a connection to the named host.

        `host` is the name or IP address of the device to connect to

        `port` is the TCP port to use for the connection.  This may be either
            a single port or a list of ports.  If left unset, the port will
            automatically be determined.

        `auth` defines the authentication method and credentials to use
            to access the device.  See UserAuth and OAuth.  If set to None,
            connection is not authenticated.
            
        `force_ssl` when set to True will only allow SSL based connections.
            If False, only allow non-SSL connections.  If set to None
            (the default) try SSL first, then try non-SSL.
        
        `versions` is the API versions that the caller can use.
            if unspecified, this will use the latest version supported
            by both this implementation and service requested.  This does
            not apply to the "common" resource requests.
        """

        self.service = service
        self.host = host
        self.port = port

        #Connection object.  Use this to make REST requests to the device.
        self.conn = None

        self.force_ssl = force_ssl

        logger.info("New service %s for host %s" % (self.service, self.host))

        self.connect(self.force_ssl)
        self.check_api_versions(versions)

        if auth is not None:
            self.authenticate(auth)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.logout()

    def connect(self, ssl):
        if self.conn is not None and hasattr(self.conn, 'close'):
            self.conn.close()

        cls = self._get_connection_class()
        self.conn = cls(self.host, self.port, ssl, reauthenticate_handler=self.reauthenticate,
                        test_resource="/api/common/1.0/ping")

    def logout(self):
        """End the authenticated session with the device."""
        if self.conn:
            self.conn.del_headers(['Authorization', 'Cookie'])

    def check_api_versions(self, api_versions):
        """Check that the server supports the given API versions."""
        if self.conn is None:
            raise RvbdException("Not connected")

        try:
            supported_versions = self._get_supported_versions()
        except:
            logger.warning("Failed to retrieved supported versions")
            return False
        
        if supported_versions is None:
            return False

        logger.debug("Server supports the following services: %s" %
                     (",".join([str(v) for v in supported_versions])))
        
        for v in api_versions:
            if v in supported_versions:
                self.api_version = v
                logger.debug("Service '%s' supports version '%s'" % (self.service, v))
                return True

        raise RvbdException("API version(s) %s not supported (supported version(s): %s)" %
                           (', '.join([str(v) for v in api_versions]),
                            ', '.join([str(v) for v in supported_versions])))

    def _get_supported_versions(self):
        """Get the common list of services and versions supported."""
        # uses the GL7 'services' resource.
        url = '/api/common/1.0/services'
        services = self.conn.json_request(url, 'GET')

        for service in services:
            if service['id'] == self.service:
                return [APIVersion(v) for v in service['versions']]

        return None

    def _detect_auth_methods(self):
        """Get the list of authentication methods supported."""
        # uses the GL7 'auth_info' resource
        url = '/api/common/1.0/auth_info'

        try:
            auth_info = self.conn.json_request(url, method='GET')
            logger.info("Supported authentication methods: %s" %
                        (','.join(auth_info['supported_methods'])))
            self._supports_auth_basic  = ("BASIC" in auth_info['supported_methods'])
            self._supports_auth_cookie = ("COOKIE" in auth_info['supported_methods'])
            self._supports_auth_oauth  = ("OAUTH_2_0" in auth_info['supported_methods'])
        except:
            logger.warning("Failed to retrieve auth_info, assuming basic")
            self._supports_auth_basic  = True
            self._supports_auth_cookie = False
            self._supports_auth_oauth  = False
            
    def _get_connection_class(self):
        """Internal function to return the class used to instantiate a connection"""
        return rvbd.common.connection.Connection

    def authenticate(self, auth):
        """Authenticate with device using the defined authentication method.
        This sets up the appropriate authentication headers to access
        restricted resources.

        `auth` must be an instance of either UserAuth or OAuth."""
        
        assert auth is not None

        self.auth = auth
        self._detect_auth_methods()

        if self._supports_auth_oauth and Auth.OAUTH in self.auth.methods:
            # TODO fix for future support to handle appropriate triplets
            code = self.auth.access_code
            url = '/api/common/1.0/oauth/token'
            data = {
                'grant_type': 'access_code',
                'assertion': code
                }
            answer = self.conn.json_request(url, 'POST', params=data)
            token = answer['access_token']
            st = token.split('.')
            if len(st) == 1:
                auth_header = 'Bearer %s' % token
            elif len(st) == 3:
                auth_header = 'SignedBearer %s' % token
            else:
                raise RvbdException('Unknown OAuth response from server: %s' % st)
            self.conn.add_headers({'Authorization': auth_header})
            logger.info('Authenticated using OAUTH2.0')

        elif self._supports_auth_cookie and Auth.COOKIE in self.auth.methods:
            url = '/api/common/1.0/login'
            data = {
                "username": self.auth.username,
                "password": self.auth.password
                }

            answer = self.conn.json_request(url, 'POST', data=data)

            # we're good, set up our http headers for subsequent
            # requests!
            self.conn.add_headers({'Cookie': answer['session_key'] + "=" + answer['session_id']})

            logger.info("Authenticated using COOKIE")

        elif self._supports_auth_basic and Auth.BASIC in self.auth.methods:

            # Use HTTP Basic authentication
            s = base64.b64encode("%s:%s" % (self.auth.username, self.auth.password))
            self.conn.add_headers({'Authorization': 'Basic %s' % s})

            logger.info("Authenticated using BASIC")

        else:
            raise RvbdException("No supported authentication methods")

    def reauthenticate(self):
        """Retry the authentication method"""
        self.authenticate(self.auth)

    def ping(self):
        """Ping the service.  On failure, this raises an exception"""

        res = self.conn.request('/api/common/1.0/ping', method="GET")

        # drain the response object...
        res.read()

        return True
