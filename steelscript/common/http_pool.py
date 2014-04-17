# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


import httplib
from itertools import chain

__all__ = [ 'ConnectionPool' ]

class ResponseWrapper(object):
    def __init__(self, resp, finished):
        self.__resp = resp
        self.__finished = finished

        self.msg = self.__resp.msg
        self.version = self.__resp.version
        self.status = self.__resp.status
        self.reason = self.__resp.reason

    def read(self, *args):
        ret = self.__resp.read(*args)
        if (len(args) == 0 or len(ret) < args[0]) and self.__finished is not None:
            self.__finished()
            self.__finished = None
        return ret

    def getheader(self, *args, **kwargs):
        return self.__resp.getheader(*args, **kwargs)

    def getheaders(self, *args, **kwargs):
        return self.__resp.getheaders(*args, **kwargs)

    def fileno(self, *args, **kwargs):
        return self.__resp.fileno(*args, **kwargs)

    
class ConnectionPool(object):
    class NoFreeConnections(Exception): pass
    
    def __init__(self, *args, **kwargs):
        self._conn_args = args
        self._conn_kwargs = kwargs

        self._pool_size = 1
        if 'pool_size' in kwargs:
            self._pool_size = kwargs['pool_size']
            del kwargs['pool_size']
            
        self._connection_class = httplib.HTTPConnection
        if 'use_ssl' in kwargs:
            if kwargs['use_ssl']:
                self._connection_class = httplib.HTTPSConnection
            del kwargs['use_ssl']
        
        self._busy_connections = []
        self._free_connections = []
        self._current_connection = None

        # initialize with dubugging turned off
        self._debug_level = 0
        
    def connect(self):
        pass

    def close(self):
        pass

    def set_tunnel(self, *args, **kwargs): 
        raise NotImplementedError()

    def set_debuglevel(self, level): 
        self._debug_level = level

        if self._current_connection:
            self._current_connection.set_debuglevel(level)
        for conn in chain(self._free_connections, self._busy_connections):
            conn.set_debuglevel(level)

    def _start_connection(self):
        if self._current_connection is not None:
            raise httplib.ImproperConnectionState()

        try:
            self._current_connection = self._free_connections.pop()
        except IndexError:
            if len(self._busy_connections) >= self._pool_size:
                raise NoFreeConnections()
            #print 'create new connection (%d busy)' % len(self._busy_connections)
            self._current_connection = self._connection_class(*self._conn_args, **self._conn_kwargs)
            self._current_connection.connect()

            # if we have set the debug level, set it on new connections too
            if self._debug_level:
                self._current_connection.set_debug_level = self._debug_level
        
    def request(self, *args, **kwargs):
        self._start_connection()
        try:
            return self._current_connection.request(*args, **kwargs)
        except (httplib.HTTPException, IOError):
            self._current_connection = None
            raise

    def putrequest(self, *args, **kwargs):
        self._start_connection()
        try:
            return self._current_connection.putrequest(*args, **kwargs)
        except (httplib.HTTPException, IOError):
            self._current_connection = None
            raise

    def putheader(self, *args, **kwargs):
        if self._current_connection is None:
            raise httplib.ImproperConnectionState()
        return self._current_connection.putheader(*args, **kwargs)

    def endheaders(self, *args, **kwargs):
        if self._current_connection is None:
            raise httplib.ImproperConnectionState()
        try:
            return self._current_connection.endheaders(*args, **kwargs)
        except (httplib.HTTPException, IOError):
            self._current_connection = None
            raise

    def send(self, *args, **kwargs):
        if self._current_connection is None:
            raise httplib.ImproperConnectionState()
        return self._current_connection.send(*args, **kwargs)

    def _recycle(self, conn):
        self._busy_connections.remove(conn)
        self._free_connections.append(conn)
        
    def getresponse(self):
        if self._current_connection is None:
            raise httplib.ImproperConnectionState()

        conn = self._current_connection
        self._current_connection = None
        self._busy_connections.append(conn)

        try:
            resp = conn.getresponse()
            return ResponseWrapper(resp, lambda: self._recycle(conn))
        except httplib.HTTPException:
            self._busy_connections.remove(conn)
            raise

