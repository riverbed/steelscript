# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


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
      steelscript.common.datastructures.JsonDict
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
                    for key, value in cd.items():
                        default[key] = value
            self._default = default

        self.update(self._default)
        self.update(dict)
        self.update(kwargs)

        if self._required is not None:
            for key in self._required:
                if self.__getattr__(key) is None:
                    raise KeyError("Required key not specified: %s" %
                                   '.'.join(key.split("__")))

    def __dir__(self):
        return list(self.keys())

    def __str__(self):
        """Return the json-encoded form of the dictionary."""
        # handle un-encodable items with str operator
        return json.dumps(self, default=str)

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
            for k, v in dict.items():
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
            # print "looking at %s" % k
            if isinstance(obj, list):
                obj = obj[int(k)]
            elif isinstance(obj, dict):
                if k not in obj:
                    raise AttributeError(key)
                obj = obj[k]
            else:
                raise AttributeError(key)

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

        # print "setattr: self <<%s>> : setattr(%s => %s)" % (str(self), key,
        #                                                     value)

        # Turn "obj.<key> = <value>" into "obj['<key>'] = <value>
        if key[0] == '_':
            # Treat keys starting with an underscore as normal attributes
            return object.__setattr__(self, key, value)

        # Treat "__" as a separator like a '.'
        #   so x.a__b ==> x.a.b
        if isinstance(key, bytes):
            key = key.decode('utf-8')
        keyparts = key.split("__")

        # Navigate to the parent object to be set.
        obj = self
        for key in keyparts[:-1]:
            if ((not isinstance(obj, dict)) or
                    ((obj._default is not None) and
                     (key not in obj._default))):
                raise AttributeError("Invalid key: '%s'" % key)

            if (key not in obj) or (not isinstance(obj[key], dict)):
                obj[key] = JsonDict()
                if obj._default is not None:
                    obj[key]._default = obj._default[key]

            obj = obj[key]

        key = keyparts[-1]

        if ((not isinstance(obj, dict)) or
                ((obj._default is not None) and (key not in obj._default))):
            raise AttributeError("Invalid key: '%s'" % key)

        obj[key] = self._decode(value, obj._default[key]
                                if obj._default is not None else None)

    def _decode(self, value, default):
        """Internal function to decode a value, replacing standard dicts with
        JsonDict."""
        # print "decode(%s, %s)" % (value, default)
        if isinstance(value, dict):
            newvalue = JsonDict(dict=value, default=default)
        elif isinstance(value, list):
            newvalue = []
            for item in value:
                newvalue.append(self._decode(item, None))
        else:
            if isinstance(value, bytes):
                newvalue = value.decode('utf-8')
            else:
                newvalue = value

        return newvalue


class DictObject(dict):
    """
    Creates an object from a custom dictionary, setting attributes
    for each toplevel key in the dictionary.  This allows simpler
    access to the top-level keys:

    Example:
      >>> d = DictObject({'foo': 1,
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

    The object is dict and can be maniuplated and iterated just like a dict.
    Note that only the top-level keys are converted to attributes.  Values that
    are dicts are still stored as dicts, thus must be accessed using [].

      >>> type(d.baz)
      dict
      >>> d.baz['fozzle']
      10
    """
    # This works by overriding the
    # the 'getattr' and 'setattr' methods.

    # We do not need to override the 'hasattr' as internally this
    # method invokes 'getattr' method and if 'getattr' returns
    # AttributeError then 'hasattr' returns False else it returns True.

    @staticmethod
    def create_from_dict(data):
        """Convert a dictionary into a DictObject instance.

        In the process, this converts all unicode strings to regular strings.
        """

        if data is None:
            # if we aren't given a dict, just return an empty object
            return DictObject()

        def _decode_list(data):
            rv = []
            for item in data:
                if isinstance(item, bytes):
                    item = item.decode('utf-8')
                elif isinstance(item, list):
                    item = _decode_list(item)
                elif isinstance(item, dict):
                    item = _decode_dict(item)
                rv.append(item)
            return rv

        def _decode_dict(data):
            rv = DictObject()
            for key, value in data.items():
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
                elif isinstance(value, list):
                    value = _decode_list(value)
                elif isinstance(value, dict):
                    value = _decode_dict(value)
                rv[key] = value
            return rv

        return _decode_dict(data)

    def __init__(self, d=None):
        if not d:
            d = {}
        super(DictObject, self).__init__(d)

    def __dir__(self):
        return list(self.keys())

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        # XXX - don't think KeyError will ever be called here
        self[key] = value


class ColumnProxy(object):
    """ a class to simplify creating a data structure that mirrors
    a structure that can be fetched at run-time from a server.

    This class is used for structures like the list of valid
    extractor fields on NetShark or the list of valid columns on
    NetProfiler.  These are very long lists of names so we don't want
    to hard-code the list in steelscript but we would also like the
    list to be available at run-time so interactive tools like
    bpython or eclipse can do automatic completion.  At the same
    time, non-interactive scripts have no need to fetch and parse
    the list of field names so we only want the list to be fetched
    if needed.

    We achieve the goals listed above by using this proxy object.
    For non-interactive scripts, it simply implements __getattr__
    to echo back strings including those containing periods.
    So if columns is an instance of this class, then trivial uses are:

    >>> columns.foo
    foo
    >>> columns.x.y.z
    x.y.z

    For interactive scripts, the entry point for doing auto-completion
    (from something like a tab keypress in bpython) is __dir__.
    __dir__() calls a supplied function to get a list of valid names
    and builds a data structure that reflects the list of provided names.
    It calls a second callback so that this data structure can be stored
    in the parent object so future references do not need another fetch
    from the server.

    See the columns field in steelscript.netshark.NetShark objects for
    a typical example of how it is used.
    """

    def __init__(self, fn, callback):
        self._fn = fn
        self._callback = callback

    class Container(object):
        pass

    def __dir__(self):
        root = self.Container()
        for (name, value) in self._fn():
            o = root

            components = name.split('.')
            for component in components[:-1]:
                try:
                    o = getattr(o, component)
                except AttributeError:
                    n = self.Container()
                    setattr(o, component, n)
                    o = n

            setattr(o, components[-1], self.FakeColumn(name))

        self._callback(root)
        return dir(root)

    class FakeColumn(str):
        def __getattribute__(self, n):
            if n == 'count':
                return str('%s.%s' % (self, n))
            return str.__getattribute__(self, n)

        def __getattr__(self, n):
            return self.__class__('%s.%s' % (self, n))

    def __getattr__(self, n):
        return self.FakeColumn(n)


class RecursiveUpdateDict(dict):
    """ XXX this needs documentation """
    def __init__(self, *args, **kw):
        super(RecursiveUpdateDict, self).__init__(*args, **kw)

    def update(self, E=None, **F):
        if E is not None:
            if 'keys' in dir(E) and callable(getattr(E, 'keys')):
                for k in E:
                    if k in self:  # existing ...must recurse into both sides
                        self.r_update(k, E)
                    else:  # doesn't currently exist, just update
                        self[k] = E[k]
            else:
                for (k, v) in E:
                    self.r_update(k, {k: v})

        for k in F:
            self.r_update(k, {k: F[k]})

    def r_update(self, key, other_dict):
        if isinstance(self[key], dict) and isinstance(other_dict[key], dict):
            od = RecursiveUpdateDict(self[key])
            nd = other_dict[key]
            od.update(nd)
            self[key] = od
        else:
            self[key] = other_dict[key]


class Singleton(type):
    """Metaclass for singleton classes"""
    # inspired by
    # stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    _instances = {}

    def __call__(cls, *args, **kw):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kw)
        return cls._instances[cls]
