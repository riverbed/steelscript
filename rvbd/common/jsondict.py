# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript-portal/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.

import json
import inspect

class JsonDict(dict):
    _default = None
    _required = None

    """
    Creates a dictionary, setting attributes for each toplevel key in
    the dictionary.  This allows simpler access to the top-level keys
    using dotted notation rather than the square brackets access

    The object is dict and can be maniuplated and iterated just like a
    dict, including nested dictionaries.  

    Example:
      >>> d = JsonDict({'foo': 1,
                        'bar': 'This is the bar',
                        'baz': { 'fozzle': 10,
                                 'frobble': 'Flounder'}})
      >>> d.foo
      1
      >>> d['foo']
      1
      >>> d
      {'foo': 1,
       'bar': 'This is the bar',
       'baz': { 'fozzle': 10,
                'frobble': 'Flounder'}}

      >>> type(d.baz)
      rvbd.common.jsondict.JsonDict
      >>> d.baz.fozzle
      10
    """
    # We do not need to override the 'hasattr' as internally this
    # method invokes 'getattr' method and if 'getattr' returns
    # AttributeError then 'hasattr' returns False else it returns True.

    def __init__(self, dict=None, default=None, **kwargs):
        """Create a new JsonDict object.

        `dict` is an optional dictionary to initialize from

        `default` is an optional structure used to define defaults
            as well as validate future assignments

        Additional keyword arguments are parsed as if passed
        to __setattr__.  
        """
        super(JsonDict, self).__init__()
        if default:
            self._default = default
        else:
            default = None
            for c in reversed(inspect.getmro(self.__class__)):
                try:
                    cd = c._default
                except:
                    continue
                if cd is not None:
                    if default is None:
                        default = {}
                    for key,value in cd.iteritems():
                        default[key] = value
            self._default = default

        self.update(self._default)
        self.update(dict)
        self.update(kwargs)

        if self._required is not None:
            for key in self._required:
                if self.__getattr__(key) is None:
                    raise KeyError("Required key not specified: %s" % '.'.join(key.split("__")))

    def __dir__(self):
        return self.keys()
        
    def __str__(self):
        """Return the json-encoded form of the dictionary."""
        return json.dumps(self)

    @classmethod
    def loads(cls, s):
        """Create a JsonDict object from a json-encoded string."""
        o = cls()
        o.parse(s)
        return o
    
    def parse(self, s):
        """Update the object from a json-encoded string."""
        d = json.loads(s)
        self.update(d)
        
    def update(self, dict):
        """Update the object from a dict."""
        if dict is not None:
            for k,v in dict.iteritems():
                self.__setattr__(k, v)
    
    def __getattr__(self, key):
        """
        Return the value associated with the specified key.  Keys starting
        with an underscore are assumed to be standard attributes.  All other
        keys are treated as members of the dictionary.

        The key may also reference nested dictionaries using '__' to split
        key names at each level.

        The following representations are equivalent:

        >>> d = JsonDict({'name' : { 'first' : 'John' }})
        >>> d['name']['first']
        'John'
        >>> d.name.first
        'John'
        >>> d.name__first
        'John'
        
        This last form using '__' is useful as part of initialization.
        """

        # Treat keys leading with '_' as standard attributes
        if key[0] == '_':
            return object.__getattr__(self, key)

        # All other keys are assumed to be part of the dictionary
        
        # Treat "__" as a separator like a '.'
        #   so x.a__b ==> x.a.b
        keyparts = key.split("__")

        # Navigate to the right nested object
        obj = self
        for k in keyparts:
            #print "looking at %s" % k
            if isinstance(obj, list):
                obj = obj[int(k)]
            elif isinstance(obj, dict):
                if (k not in obj):
                    raise KeyError(key)
                obj = obj[k]
            else:
                raise KeyError(key)
                
        return obj
    
    def __setattr__(self, key, value):
        """
        Set the value associated with the specified key.  Keys starting
        with an underscore are assigned as standard attributes.  All others
        are assigned to the dictionary object.  

        The key may also reference nested dictionaries using '__' to split
        key names at each level.

        See __getattr__ as an example.
        """
        
        #print "setattr: self <<%s>> : setattr(%s => %s)" % (str(self), key, value)

        # Turn "obj.<key> = <value>" into "obj['<key>'] = <value>
        if key[0] == '_':
            # Treat keys starting with an underscore as normal attributes
            return object.__setattr__(self, key, value)

        # Treat "__" as a separator like a '.'
        #   so x.a__b ==> x.a.b
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        keyparts = key.split("__")

        # Navigate to the parent object to be set. 
        obj = self
        for key in keyparts[:-1]:
            if ((not isinstance(obj, dict)) or
                ((obj._default is not None) and (key not in obj._default))):
                raise KeyError("Invalid key: '%s'" % key)

            if (key not in obj) or (not isinstance(obj[key], dict)):
                obj[key] = JsonDict()
                if obj._default is not None:
                    obj[key]._default = obj._default[key]

            obj = obj[key]

        key = keyparts[-1]

        if ((not isinstance(obj, dict)) or
            ((obj._default is not None) and (key not in obj._default))):
            raise KeyError("Invalid key: '%s'" % key)

        obj[key] = self._decode(value, obj._default[key] if obj._default is not None else None)

    def _decode(self, value, default):
        """Internal function to decode a value, replacing standard dicts with
        JsonDict."""
        #print "decode(%s, %s)" % (value, default)
        if isinstance(value, dict):
            newvalue = JsonDict(dict=value, default=default)
        elif isinstance(value, list):
            newvalue = []
            for item in value:
                newvalue.append(self._decode(item, None))
        else:
            if isinstance(value, unicode):
                newvalue = value.encode('utf-8')
            else:
                newvalue = value
        
        return newvalue

