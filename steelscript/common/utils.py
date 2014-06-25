# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import os
import sys
import glob
import shutil
import httplib
import pkg_resources

from itertools import izip


# http://goo.gl/zeJZl
def bytes2human(n, fmt=None):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    if fmt is None:
        fmt = "%(value)i%(symbol)s"
    symbols = ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i+1)*10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return fmt % locals()
    return fmt % dict(symbol=symbols[0], value=n)


# http://goo.gl/zeJZl
def human2bytes(s):
    """
    >>> human2bytes('1M')
    1048576
    >>> human2bytes('1G')
    1073741824
    """
    symbols = ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    s = s.replace(' ', '')
    offset = 0
    num = ''
    letter = 'B'
    for i, c in enumerate(s):
        if c == '.':
            offset = i
        elif not c.isdigit():
            letter = c.upper()
            break
        num += c

    if offset:
        num = str(int(float(num) * 1024))
        letter = symbols[symbols.index(letter) - 1]
    assert num.isdigit() and letter in symbols
    num = float(num)
    prefix = {symbols[0]: 1}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i + 1) * 10
    return int(num * prefix[letter])


def link_pkg_dir(pkgname, src_path, dest_dir, symlink=True,
                 replace=True, buf=None):
    """Create a link from a resource within an installed package.

    :param pkgname: name of installed package
    :param src_path: relative path within package to resource
    :param dest_dir: absolute path to location to link/copy
    :param symlink: create a symlink or copy files
    :param replace: if True, will unlink/delete before linking
    :param buf: IO buffer to send debug statements, if None uses sys.stdout
    """
    if buf is None:
        debug = sys.stdout.write
    else:
        debug = buf

    src_dir = pkg_resources.resource_filename(pkgname, src_path)

    if os.path.islink(dest_dir) and not os.path.exists(dest_dir):
        debug(' unlinking %s ...\n' % dest_dir)
        os.unlink(dest_dir)

    if os.path.exists(dest_dir):
        if not replace:
            return

        if os.path.islink(dest_dir):
            debug(' unlinking %s ...\n' % dest_dir)
            os.unlink(dest_dir)
        else:
            debug(' removing %s ...\n' % dest_dir)
            shutil.rmtree(dest_dir)

    if symlink:
        debug(' linking %s --> %s\n' % (src_dir, dest_dir))
        os.symlink(src_dir, dest_dir)
    else:
        debug(' copying %s --> %s\n' % (src_dir, dest_dir))
        shutil.copytree(src_dir, dest_dir)


def link_pkg_files(pkgname, src_pattern, dest_dir, symlink=True,
                   replace=True, buf=None):
    """Create links for files from a resource within an installed package.

    :param pkgname: name of installed package
    :param src_pattern: relative path within package to file resource,
        can be a glob pattern
    :param dest_dir: absolute path to location to link/copy, symlinks
        will be made inside this dir rather than linking to the dir itself
    :param symlink: create a symlink or copy files
    :param replace: if True, will unlink/delete before linking
    :param buf: IO buffer to send debug statements, if None uses sys.stdout
    """
    if buf is None:
        debug = sys.stdout.write
    else:
        debug = buf

    src_dir = pkg_resources.resource_filename(pkgname, src_pattern)
    src_files = glob.glob(src_dir)

    if os.path.islink(dest_dir):
        # avoid putting files within a symlinked path
        debug(' skipping linked directory %s ...\n' % dest_dir)
        return

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for f in src_files:
        fn = os.path.basename(f)
        dest_file = os.path.join(dest_dir, fn)

        if os.path.exists(dest_file) and not replace:
            debug(' skipping file %s ...\n' % dest_file)
            continue

        if os.path.islink(dest_file):
            debug(' unlinking %s ...\n' % dest_file)
            os.unlink(dest_file)
        elif os.path.exists(dest_file):
            debug(' removing %s ...\n' % dest_file)
            os.unlink(dest_file)

        if symlink:
            debug(' linking %s --> %s\n' % (f, dest_file))
            os.symlink(f, dest_file)
        else:
            debug(' copying %s --> %s\n' % (f, dest_file))
            shutil.copy(f, dest_file)


class Formatter(object):
    """ Helper class to format output into tables with headers

        get_csv and print_csv use simple formatting rules, for
        more complex usage, including dialects, the built-in
        `csv` module may be more suitable.
    """
    @classmethod
    def print_table(cls, columns, headers, paginate=None, padding=4,
                    max_width=None, long_column=1, wrap_columns=False):
        """ Print formatted table with optional pagination

            `columns`      - list of data rows
            `headers`      - list of strings for table header
            `paginate`     - number of rows to insert new header
            `padding`      - extra spaces between columns
            `max_width`    - number of characters to restrict output to
            `long_column`  - column number to either truncate or wrap to meet max_width
                             (defaults to second column)
            `wrap_columns` - indicate whether to wrap or truncate long_column
        """
        import textwrap

        widths = [max(len(str(x)) + padding for x in col) for col in izip(headers,
                                                                          *columns)]

        if max_width and sum(widths) > max_width:
            delta = sum(widths) - max_width
            if delta > widths[long_column]:
                # issue warning then turn off wrapping so data is still printed
                print ('WARNING: Formatting error: cannot truncate column %d '
                       'to meet max_width %d, printing all data instead ...'
                       % (long_column, max_width))
                max_width = None
            else:
                widths[long_column] -= delta

        header = ''.join(s.ljust(x) for s, x in zip(headers, widths))
        for i, row in enumerate(columns):
            if i == 0 or (paginate and i % paginate == 0):
                # print header at least once
                print ''
                print header
                print '-' * len(header)
            if max_width:
                row = list(row)
                column = row[long_column]
                width = widths[long_column] - padding - 2
                if not wrap_columns:
                    # truncate data with ellipsis if needed
                    row[long_column] = (column[:width] + '..') if len(column) > width else column
                    print ''.join(str(s).ljust(x) for s, x in zip(row, widths))
                else:
                    # take column and wrap it in place, creating new rows
                    wrapped = (r for r in textwrap.wrap(column, width=width))
                    row[long_column] = wrapped.next()
                    print ''.join(str(s).ljust(x) for s, x in zip(row, widths))
                    for line in wrapped:
                        newrow = [''] * len(widths)
                        newrow[long_column] = line
                        print ''.join(str(s).ljust(x) for s, x in zip(newrow,
                                                                      widths))
            else:
                print ''.join(str(s).ljust(x) for s, x in zip(row, widths))

    @classmethod
    def get_csv(cls, columns, headers, delim=','):
        """ Return list using `delim` as separator (defaults to comma-separated list)
        """
        output = [delim.join(s for s in headers)]
        for row in columns:
            output.append(delim.join(str(x) for x in row))
        return output

    @classmethod
    def print_csv(cls, columns, headers, delim=','):
        """ Print table to stdout using `delim` as separator
        """
        print '\n'.join(cls.get_csv(columns, headers, delim))


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
        '''Converts a dictionary into a DictObject instance, in the
           process converting all unicode strings to regular strings.'''

        if data is None:
            # if we aren't given a dict, just return an empty object
            return DictObject()

        def _decode_list(data):
            rv = []
            for item in data:
                if isinstance(item, unicode):
                    item = item.encode('utf-8')
                elif isinstance(item, list):
                    item = _decode_list(item)
                elif isinstance(item, dict):
                    item = _decode_dict(item)
                rv.append(item)
            return rv

        def _decode_dict(data):
            rv = DictObject()
            for key, value in data.iteritems():
                if isinstance(key, unicode):
                    key = key.encode('utf-8')
                if isinstance(value, unicode):
                    value = value.encode('utf-8')
                elif isinstance(value, list):
                    value = _decode_list(value)
                elif isinstance(value, dict):
                    value = _decode_dict(value)
                rv[key] = value
            return rv

        return _decode_dict(data)

    def __init__(self, d=None):
        if not d: d = {}
        super(DictObject, self).__init__(d)

    def __dir__(self):
        return self.keys()

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

    See the columns field in steelscript.netshark.NetShark objects for a typical
    example of how it is used.
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

            setattr(o, components[-1], value)

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
                    else: # doesn't currently exist, just update
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


class ChunkedMixin(object):
    def __init__(self, chunk_size, *args, **kwargs):
        self.chunk_size = chunk_size
        super(ChunkedMixin, self).__init__(self, *args, **kwargs)

    def request(self, method, url, body, headers):
        chunks = [body[s:self.chunk_size]
                  for s in range(0, len(body), self.chunk_size)]
        chunks.append('')

        def build(string, chunk):
            return string + '%x\r\n%s\r\n' % (len(chunk), chunk)
        new_body = reduce(build, chunks, '')

        headers['Transfer-Encoding'] = 'chunked'

        return super(ChunkedMixin, self).request(method, url, new_body, headers)

class ChunkedHTTPConnection(ChunkedMixin, httplib.HTTPConnection): pass
class ChunkedHTTPSConnection(ChunkedMixin, httplib.HTTPSConnection): pass
