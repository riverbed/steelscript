# Copyright (c) 2018 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import json
import xml.etree.ElementTree as ElementTree

__all__ = ['RvbdException', 'RvbdHTTPException',
           'RvbdConnectException']


class RvbdException(Exception):
    def __init__(self, msg, **kwargs):
        tmp_message = kwargs.get('message', None)
        if isinstance(msg, str) and tmp_message is None:
            super().__init__(msg)
            self.message = msg
        elif isinstance(tmp_message, str):
            super().__init__(tmp_message)
            self.message = tmp_message
        else:
            self.message = ''

    def __str__(self):
        return "{0}".format(self.message)

    def __repr__(self):
        return ("RvbdException(message={0})".format(self.message))

class RvbdConnectException(RvbdException):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.errno = kwargs.get('errno', None)
        self.errname = kwargs.get('errname', None)


class RvbdHTTPException(RvbdException):
    def __init__(self, result, data, method, urlpath):
        super().__init__('HTTP {0} on {1} returned status {2} ({3})'
                         ''.format(method, urlpath, result.status_code,
                                   result.reason))

        self.status = result.status_code
        self.reason = result.reason
        self.xresult = result
        self.xdata = data
        self.xmethod = method
        self.xurlpath = urlpath
        # Try to parse the error structure (either XML or JSON)
        try:
            t = result.headers.get('Content-type', None)
            if t == 'text/xml':
                e = ElementTree.fromstring(data)
                if e.tag != 'error':
                    if e.tag == 'TraceStats':
                        self.error_id = None
                        self.error_text = e.get('Cause')
                    else:
                        msg = 'Unable to parse error message from server'
                        raise ValueError(msg)
                else:
                    self.error_id = e.get('error_id')
                    self.error_text = e.get('error_text')

            elif t is not None and 'application/json' in t:
                d = json.loads(data)
                # Handle Riverbed Case
                if set(('error_text', 'error_id')) == set(d.keys()):
                    self.error_text = d['error_text']
                    self.error_id = d['error_id']
                # ServiceNow case
                elif (('error' in d) and
                      (set(('message', 'detail')) ==
                       set(d['error'].keys()))):
                    self.error_text = d['error']['detail']
                    self.error_id = d['error']['message']
                # Don't know this format just grab the entire body.
                else:
                    self.error_text = data
            elif self.reason == 'Unauthorized':
                self.error_id = 'AUTH_REQUIRED'
                self.error_text = "Not authorized"
            else:
                self.error_id = None
                self.error_text = self.reason

            if self.error_text == "Not authorized":
                self.error_text += (
                    " You are not logged in. "
                    "Use the auth parameter to enter valid credentials or "
                    "authenticate using the .authenticate(auth) method."
                )

        except Exception as e:
            self.error_id = 'INVALID_ERROR_IDENTIFIER'
            self.error_text = e

    def __str__(self):
        return "{0} {1}".format(self.status, self.error_text)

    def __repr__(self):
        return ("RvbdHTTPException(result={result}, data={data}, "
                "method={method}, urlpath={urlpath})"
                "".format(result=self.xresult, data=self.xdata,
                          method=self.xmethod, urlpath=self.xurlpath))
