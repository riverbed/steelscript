# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.





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
        prefix[s] = 1 << (i + 1) * 10
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


class Formatter(object):
    """ Helper class to format output into tables with headers

        get_csv and print_csv use simple formatting rules, for
        more complex usage, including dialects, the built-in
        `csv` module may be more suitable.
    """
    @classmethod
    def print_table(cls, data, headers, paginate=None, padding=4,
                    max_width=None, long_column=1, wrap_columns=False):
        """ Print formatted table with optional pagination

            `data`         - list of data rows
            `headers`      - list of strings for table header
            `paginate`     - number of rows to insert new header
            `padding`      - extra spaces between columns
            `max_width`    - number of characters to restrict output to
            `long_column`  - column number to either truncate or wrap to meet
                             max_width (defaults to second column)
            `wrap_columns` - indicate whether to wrap or truncate long_column
        """
        import textwrap

        widths = [max(len(str(x)) + padding for x in col)
                  for col in zip(headers, *data)]

        if max_width and sum(widths) > max_width:
            delta = sum(widths) - max_width
            if delta > widths[long_column]:
                # issue warning then turn off wrapping so data is still printed
                print(('WARNING: Formatting error: cannot truncate column %d '
                       'to meet max_width %d, printing all data instead ...'
                       % (long_column, max_width)))
                max_width = None
            else:
                widths[long_column] -= delta

        header = ''.join(s.ljust(x) for s, x in zip(headers, widths))
        for i, row in enumerate(data):
            if i == 0 or (paginate and i % paginate == 0):
                # print header at least once
                print('')
                print(header)
                print('-' * len(header))
            if max_width:
                row = list(row)
                column = row[long_column]
                width = widths[long_column] - padding - 2
                if not wrap_columns:
                    # truncate data with ellipsis if needed
                    row[long_column] = ((column[:width] + '..')
                                        if len(column) > width else column)
                    print(''.join(str(s).ljust(x)
                                  for s, x in zip(row, widths)))
                else:
                    # take column and wrap it in place, creating new rows
                    wrapped = (r for r in textwrap.wrap(column, width=width))
                    try:
                        row[long_column] = next(wrapped)
                    except StopIteration:
                        # The column is empty string
                        pass
                    print(''.join(str(s).ljust(x)
                                  for s, x in zip(row, widths)))
                    for line in wrapped:
                        newrow = [''] * len(widths)
                        newrow[long_column] = line
                        print(''.join(str(s).ljust(x)
                                      for s, x in zip(newrow, widths)))
            else:
                print(''.join(str(s).ljust(x)
                              for s, x in zip(row, widths)))

    @classmethod
    def get_csv(cls, data, headers, delim=','):
        """Return list of lists using `delim` as separator."""

        output = [delim.join(headers)]

        for row in data:
            output.append(delim.join(str(x) for x in row))

        return output

    @classmethod
    def print_csv(cls, data, headers, delim=','):
        """ Print table to stdout using `delim` as separator
        """
        print('\n'.join(cls.get_csv(data, headers, delim)))
