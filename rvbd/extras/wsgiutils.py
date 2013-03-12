# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



from urlparse import parse_qs
import urllib
import json
import httplib
import os
import errno
import re

class Response:
    def __init__(self, status_code, ctype, body, other_headers=None):
        self.status = '%u %s' % (status_code, httplib.responses[status_code])
        self.body = body
        self.headers = other_headers
        if self.headers is None:
            self.headers = {}

        self.headers['Access-Control-Allow-Origin'] = '*'
        self.headers['Content-type'] = ctype
        self.cacheable = False

    def set_cacheable(self, cacheable):
        self.cacheable = cacheable

    def send(self, start_response):
        response_headers = self.headers.copy()

        if self.cacheable:
            response_headers['Cache-control'] = 'no-store'
            response_headers['Pragma'] = 'no-cache'
        
        start_response(self.status, response_headers.items())
        return self.body

class SimpleResponse(Response):
    def __init__(self, status_code):
        Response.__init__(self, status_code, 'text/plain',
                          [httplib.responses[status_code]],
                          {})

class StringResponse(Response):
    def __init__(self, body):
        Response.__init__(self, 200, 'text/plain', [body], {})

class IterableResponse(Response):
    def __init__(self, ctype, iterable, other_headers=None):
        Response.__init__(self, 200, ctype, iterable, other_headers)

class JsonResponse(Response):
    def __init__(self, obj, other_headers=None):
        Response.__init__(self, 200, 'application/json',
                          [json.dumps(obj)], other_headers)

class WebError(Exception, Response):
    def __init__(self, status_code, body):
        Response.__init__(self, status_code, 'text/plain', [body])

def wsgiwrapper(fn, env, start_response, **kwargs):
    ''' Bridge between wsgi and the various Response objects
    defined in ``rvbd.extras.wsgiutils``.  The idea is that the
    main wsgi handler is a one-liner that calls this function
    and ``fn`` is a handler that receives standard wsgi requests
    but may optionally return an instance of ``Response``
    (or one of its subclasses) or raise ``WebError`` (or again,
    one of its subclasses).  This wrapper will take care of
    marshalling the response or error into the wsgi response
    procedure. '''
    
    try:
        result = fn(env, start_response, **kwargs)
    except WebError, we:
        result = we

    #XXX 
    if hasattr(result, 'next'):
        return result

    if not isinstance(result, Response):
        result = WebError(501, 'uh oh')
    return result.send(start_response)

def get_post_data(environ):
    """!
    Helper function to get the post data into a dict.
    @param environ the WSGI environment variables
    @return dict of post data
    """
    data = {}

    try:
        length = int(environ.get('CONTENT_LENGTH', '0'))
    except ValueError:
        length = 0

    if length > 0:
        content = environ['wsgi.input'].read(length)
        data = parse_qs(content)

    return data

def get_query_params(environ):
    """!
    Helper function to get query parameters into a dict.
    @param environ the WSGI environment variables
    @return dict of query parameters
    """
    return parse_qs(environ['QUERY_STRING'])

def parse_params(s, expected = ()):
    D = {}
    if len(s) > 0:
        for a in s.split('&'):
            name, value = a.split('=', 1)
            value = urllib.unquote_plus(value)
            D[name] = value
        
    for e in expected:
        if e not in D:
            raise WebError(400, 'missing %s parameter' % e)
    return D
    

def static_file_handler(local_path):
    ''' Return a WSGI handler that will serve up local files from
    ``local_path``.  Intended to be used from ``WSGIRouter`` so
    that the leading portion of the url path (e.g., /static) has
    already been stripped and the remainder of the path is stored
    in env['router.args'].

    See ``examples/web/main.py`` for an example of typical usage.
    '''
    def handler(env, start_response):
        method = env['REQUEST_METHOD']
        if method != 'GET':
            raise WebError(405, 'cannot %s on %s' % (method, env['PATH_INFO']))

        #XXX
        if 'router.args' in env and 'path' in env['router.args']:
            path = env['router.args']['path']
        else:
            path = env['PATH_INFO']
            
        fname = local_path + '/' + path
        try:
            fp = open(fname, 'r')
        except IOError, e:
            if e.errno == errno.ENOENT:
                raise WebError(404, 'file does not exist')
            raise e

        typemap = { '.html': 'text/html',
                    '.js': 'text/javascript',
                    '.css': 'text/css' }
        try:
            idx = fname.rindex('.')
            ctype = typemap[fname[idx:]]
        except (ValueError, KeyError):
            ctype = 'text/plain'

        headers = [
            ('Content-Type', ctype),
            ('Content-Length', str(os.stat(fname).st_size))
            ]

        start_response('200 OK', headers)
        return fp

    return handler

# a simple regexp-based url router.
# Taken from http://docs.webob.org/en/latest/do-it-yourself.html#routing
class WSGIRouter(object):
    def __init__(self):
        self.routes = []

    var_regex = re.compile(r'''
      \{          # The exact character "{"
      (\w+)       # The variable name (restricted to a-z, 0-9, _)
      (?::([^}]+))? # The optional :regex part
      \}          # The exact character "}"
      ''', re.VERBOSE)

    @classmethod
    def template_to_regex(cls, template):
        regex = ''
        last_pos = 0
        for match in cls.var_regex.finditer(template):
            regex += re.escape(template[last_pos:match.start()])
            var_name = match.group(1)
            expr = match.group(2) or '[^/]+'
            expr = '(?P<%s>%s)' % (var_name, expr)
            regex += expr
            last_pos = match.end()
        regex += re.escape(template[last_pos:])
        regex = '^%s$' % regex
        return regex
 

    def connect(self, template, handler, **kwargs):
        """Connects URLs matching a template to a handler application.
        
        Args:
        template: A template string, consisting of literal text and template
        expressions of the form {label[: regex]}, where label is the mandatory
        name of the expression, and regex is an optional regular expression.
        handler: A WSGI application to execute when the template is matched.
        **kwargs: Additional keyword arguments to pass along with those parsed
        from the template.
        """
        route_re = re.compile(self.template_to_regex(template))
        self.routes.append((route_re, handler, kwargs))

    def route(self, environ, start_response, **kwargs):
        for regex, handler, routekwargs in self.routes:
            match = regex.match(environ['PATH_INFO'])
            if match:
                environ['router.args'] = dict(routekwargs)
                environ['router.args'].update(match.groupdict())
                return handler(environ, start_response, **kwargs)
        raise WebError(404, 'unknown resource %s\n' % environ['PATH_INFO'])

