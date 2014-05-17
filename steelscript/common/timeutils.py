# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.




"""
This module contains a number of utilities for working with
dates and times, in conjunction with the python `datetime` module.

"""
from __future__ import absolute_import
from datetime import datetime, timedelta, tzinfo
from decimal import Decimal
import time
import calendar
import re

__all__ = [ 'ensure_timezone', 'force_to_utc', 'datetime_to_seconds', 
            'datetime_to_microseconds', 'datetime_to_nanoseconds',
            'usec_string_to_datetime', 'nsec_string_to_datetime',
            'timedelta_total_seconds', 'timedelta_str',
            'TimeParser', 'parse_timedelta', 'parse_range' ]


#
# tzinfo objects for utc and the local timezone,
# https://launchpad.net/dateutil
#

ZERO = timedelta(0)
EPOCHORDINAL = datetime.utcfromtimestamp(0).toordinal()

class tzutc(tzinfo):

    def utcoffset(self, dt):
        return ZERO
     
    def dst(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def __repr__(self):
        return "%s()" % self.__class__.__name__

    __reduce__ = object.__reduce__

class tzlocal(tzinfo):

    _std_offset = timedelta(seconds=-time.timezone)
    if time.daylight:
        _dst_offset = timedelta(seconds=-time.altzone)
    else:
        _dst_offset = _std_offset

    def utcoffset(self, dt):
        if self._isdst(dt):
            return self._dst_offset
        else:
            return self._std_offset

    def dst(self, dt):
        if self._isdst(dt):
            return self._dst_offset-self._std_offset
        else:
            return ZERO

    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        # We can't use mktime here. It is unstable when deciding if
        # the hour near to a change is DST or not.
        # 
        # timestamp = time.mktime((dt.year, dt.month, dt.day, dt.hour,
        #                         dt.minute, dt.second, dt.weekday(), 0, -1))
        # return time.localtime(timestamp).tm_isdst
        #
        # The code above yields the following result:
        #
        #>>> import tz, datetime
        #>>> t = tz.tzlocal()
        #>>> datetime.datetime(2003,2,15,23,tzinfo=t).tzname()
        #'BRDT'
        #>>> datetime.datetime(2003,2,16,0,tzinfo=t).tzname()
        #'BRST'
        #>>> datetime.datetime(2003,2,15,23,tzinfo=t).tzname()
        #'BRST'
        #>>> datetime.datetime(2003,2,15,22,tzinfo=t).tzname()
        #'BRDT'
        #>>> datetime.datetime(2003,2,15,23,tzinfo=t).tzname()
        #'BRDT'
        #
        # Here is a more stable implementation:
        #
        timestamp = ((dt.toordinal() - EPOCHORDINAL) * 86400
                     + dt.hour * 3600
                     + dt.minute * 60
                     + dt.second)
        return time.localtime(timestamp+time.timezone).tm_isdst

    def __eq__(self, other):
        if not isinstance(other, tzlocal):
            return False
        return (self._std_offset == other._std_offset and
                self._dst_offset == other._dst_offset)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "%s()" % self.__class__.__name__

    __reduce__ = object.__reduce__


def ensure_timezone(dt):
    """ Return a datetime object that corresponds to `dt`
    but that always has timezone info.  If `dt` already
    has timezone info, then it is simply returned.  If `dt`
    does not have timezone info, then the local time zone is
    assumed."""

    if dt.tzinfo is not None:
        return dt

    return dt.replace(tzinfo=tzlocal())

def force_to_utc(dt):
    """ Return a datetime object that corresponds to `dt`
    but in UTC rather than local time.
    If `dt` includes timezone info, then this routine simply
    converts from the given timezone to UTC.
    If `dt` does not include timezone info, then it is assumed
    to be in local time, which is then converted to UTC."""

    return ensure_timezone(dt).astimezone(tzutc())
    
def datetime_to_seconds(dt):
    """ Return the number of seconds since the Unix epoch
    for the datetime object `dt` """

    dt = ensure_timezone(dt)
    
    sec = int(calendar.timegm(dt.utctimetuple()))
    return sec

def datetime_to_microseconds(dt):
    """ Return the number of microseconds since the Unix epoch
    for the datetime object `dt` """

    dt = ensure_timezone(dt)
    
    sec = int(calendar.timegm(dt.utctimetuple()))
    return sec * 1000000 + dt.microsecond

def datetime_to_nanoseconds(dt):
    """ Return the number of nanoseconds since the Unix epoch
    for the datetime object `dt` """

    dt = ensure_timezone(dt)
    
    if not hasattr(dt, 'nanosecond'):
        return 1000 * datetime_to_microseconds(dt)

    return int(calendar.timegm(dt.utctimetuple()))*1000000000+dt.nanosecond

def sec_string_to_datetime(s):
    """ Convert the string `s` which represents a time in seconds
    since the Unix epoch to a datetime object """
    return datetime.fromtimestamp(s, tzutc())

def msec_string_to_datetime(s):
    """ Convert the string `s` which represents a time in milliseconds
    since the Unix epoch to a datetime object """
    sec = Decimal(s) / Decimal(1000)
    return datetime.fromtimestamp(sec, tzutc())

def usec_string_to_datetime(s):
    """ Convert the string `s` which represents a time in microseconds
    since the Unix epoch to a datetime object """
    sec = Decimal(s) / Decimal(1000000)
    return datetime.fromtimestamp(sec, tzutc())
    
def nsec_to_datetime(ns):
    """Convert the value `ns` which represents a time in nanoseconds
    since the Unix epoch (either as an integer or a string) to a
    datetime object"""
    if isinstance(ns, str):
        ns = int(ns)
    if ns == 0:
        return None

    # we want full nanosecond precision if we're using datetimeng but
    # float can't represent absolute timestamps with enough precision.
    # Decimal solves that problem but "regular" datetime objects can't
    # be constructed from instances of Decimal.  so, we create an
    # appropriate argument to fromtimestamp() by checking which
    # implementation of datetime we're using...
    if hasattr(datetime, 'nanosecond'):
        sec = Decimal(ns) / 1000000000
    else:
        sec = float(ns) / 1000000000

    return datetime.fromtimestamp(sec, tzutc())

def string_to_datetime(s):
    """Determine level of precision by number of digits and return
    a datetime object.

    Note: this method is only valid for datetimes between year 2001 and
    year 2286 since it assumes second level precision has 10 digits.
    """
    t = int(s)
    digits = len(str(t))
    if digits == 10:
        return sec_string_to_datetime(s)
    elif digits == 13:
        return msec_string_to_datetime(s)
    elif digits == 16:
        return usec_string_to_datetime(s)
    elif digits == 19:
        return nsec_string_to_datetime(s)
    else:
        raise TypeError('Unable to determine units of s: %s' % s)


# XXX/demmer remove this
nsec_string_to_datetime = nsec_to_datetime

def usec_string_to_timedelta(s):
    """ Convert the string `s` which represents a number of microseconds
    to a timedelta object """
    sec = float(s) / 1000000
    return timedelta(seconds=sec)

def timedelta_total_seconds(td):
    """ Handle backwards compatability for timedelta.total_seconds."""
    if hasattr(td, 'total_seconds'):
        return td.total_seconds()
    return float(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6


class TimeParser(object):
    """ Instances of this class parse strings representing dates and/or
    times into python `datetime.datetime` objects.
    This class is capable of parsing a variety of different formats.
    On the first call, the method `parse()` may take some time, as it
    tries a series of pre-defined formats one after another.  After
    successfully parsing a string, the parser object remembers the format
    that was used so subsequent calls with identically formatted strings
    are as efficient as the underlying method `datetime.strptime`.
    """
    def __init__(self):
        """ Construct a new TimeParser object """
        self._fmt = None

    @classmethod
    def _parse_no_hint(cls, s):
        """ parse string s as a date/time without any hint about the format.
        If it can be parsed, returns a tuple of the datetime object
        and the format object that was used.  If the string cannot be
        parsed, raises ValueError. """
        
        for fmt in cls._formats:
            try:
                dt = fmt.match(s)
                return dt, fmt
            except ValueError:
                pass

        raise ValueError("Could not parse datetime string: %s" % s)

    @classmethod
    def parse_one(cls, s):
        """ do a "one-shot" parsing of string s as a date/time.
        doesn't remember anything about the format that was used. """
        dt, ignored = cls._parse_no_hint(s)
        return dt

    def parse(self, s):
        """
        Parse the string `s` as a date and time.  Returns a
        `datetime.datetime` object on success or raises
        `ValueError` if the string cannot be parsed.
        """
        
        # begin with some normalization, strip whitespace and convert
        # dashes to slashes so that 05-10-2011 is equivalent to 05/10/2011
        s = s.strip().replace('-', '/')

        if self._fmt is not None:
            try:
                return self._fmt.match(s)
            except ValueError:
                pass

        dt, self._fmt = self._parse_no_hint(s)
        return dt

    # all the different time of day formats we can parse.
    # refer to the python time module documentation for details
    # on the format strings
    _time_formats = (
        '%H:%M:%S.%f',
        '%H:%M:%S',
        '%H:%M',
        '%I:%M:%S %p',
        '%I:%M:%S%p',
        '%I:%M %p',
        '%I:%M%p',
        '%I %p',
        '%I%p'
    )

    # all the different date formats we can parse.
    # note that dates are "normalized" a bit, see parse() below.
    _date_formats = (
        '%m/%d',
        '%B %d',
        '%b %d'
    )

    _date_year_formats = (
        '%Y/%m/%d',
        '%m/%d/%Y',
        '%m/%d/%y',
        '%B/%d/%Y',
        '%b/%d/%Y',
    )

    class _informat(object):
        def __init__(self, pattern, has_date, has_year):
            self.pattern = pattern
            self.has_date = has_date
            self.has_year = has_year
            if has_year: assert has_date

        def match(self, s):
            tm = datetime.strptime(s, self.pattern)

            if self.has_year:
                return tm
            
            now = datetime.now()
            if self.has_date:
                return tm.replace(year=now.year)

            return tm.replace(month=now.month, day=now.day, year=now.year)

    _formats = [ _informat(_tf, False, False) for _tf in _time_formats ] \
               + [ _informat('%s %s' % (_tf, _df), True, False)
                   for _tf in _time_formats for _df in _date_formats ] \
               + [ _informat('%s %s' % (_df, _tf), True, False)
                   for _tf in _time_formats for _df in _date_formats ] \
               + [ _informat('%s %s' % (_tf, _df), True, True)
                   for _tf in _time_formats for _df in _date_year_formats ] \
               + [ _informat('%s %s' % (_df, _tf), True, True)
                   for _tf in _time_formats for _df in _date_year_formats ]

_timedelta_units = {
    'us' : 0.000001, 'usec' : 0.000001, 'microsecond' : 0.000001, 'microseconds' : 0.000001,
    'ms' : 0.001, 'msec' : 0.001, 'millisecond' : 0.001, 'milliseconds' : 0.001,
    's' : 1, 'sec' : 1, 'second' : 1, 'seconds' : 1,
    'm' : 60, 'min' : 60, 'minute' : 60, 'minutes' : 60,
    'h' : 60*60, 'hr' : 60*60, 'hour' : 60*60, 'hours' : 60*60,
    'd' : 24*60*60, 'day' : 24*60*60, 'days': 24*60*60,
    'w' : 7*24*60*60, 'week' : 7*24*60*60, 'weeks': 7*24*60*60,
}

_timedelta_re = re.compile("([0-9]*\.*[0-9]*) *([a-zA-Z]*)")

def timedelta_str(td):
    def pluralize(val, base, plural):
        if val > 1:
            return "%d %s" % (val, plural)
        else:
            return "%d %s" % (val, base)

    if td.days > 0:
        if td.seconds != 0 or td.microseconds != 0:
            raise ValueError("Timedelta has too many components for pretty string: %s" % str(td))
        if td.days % 7 == 0:
            return pluralize(td.days / 7, "week", "weeks")
        else:
            return pluralize(td.days, "day", "days")
    elif td.seconds > 0:
        if td.microseconds != 0:
            raise ValueError("Timedelta has too many components for pretty string: %s" % str(td))
        if td.seconds % (60*60) == 0:
            return pluralize(td.seconds / (60*60), "hour", "hours")
        elif td.seconds % 60 == 0:
            return pluralize(td.seconds / 60, "minute", "minutes")
        else:
            return pluralize(td.seconds, "second", "seconds")
    else:
        if td.microseconds % 1000 == 0:
            return pluralize(td.microseconds / 1000, "millisecond", "milliseconds")
        else:
            return pluralize(td.microseconds, "microsecond", "microseconds")


def round_time(dt=None, round_to=60, round_up=False, trim=False):
    """Round a datetime object to any time laps in seconds
    `dt` : datetime.datetime object, default now.
    `round_to` : Closest number of seconds to round to, default 1 minute.
    `round_up`: Default rounds down to nearest `round_to` interval,
               True here will instead round up.
    `trim`: Trim to nearest round_to value rather than rounding.
    """
    # ref http://stackoverflow.com/a/10854034/2157429
    if dt is None:
        dt = datetime.now()
    dt = ensure_timezone(dt)

    if trim:
        rounded = (round_time(dt, round_to, False),
                   round_time(dt, round_to, True))
        return max(rounded) if max(rounded) <= dt else min(rounded)

    seconds = (dt - dt.min.replace(tzinfo=dt.tzinfo)).seconds
    if round_up:
        rounding = (seconds + round_to / 2) // round_to * round_to
    else:
        rounding = (seconds - round_to / 2) // round_to * round_to
    return dt + timedelta(0, rounding - seconds, -dt.microsecond)


def parse_timedelta(s):
    """ Parse the string `s` representing some duration of time
    (e.g., `"3 seconds"` or `"1 week"`) and return a `datetime.timedelta`
    object representing that length of time.
    If the string cannot be parsed, raises `ValueError`.
    """
    
    m = _timedelta_re.match(s)
    if not m:
        raise ValueError("Could not parse string as timedelta: %s" % s)

    if m.group(1) == "":
        val = 1
    else:
        val = float(m.group(1))
        
    if m.group(2) == "":
        units = 1
    else:
        try:
            units = _timedelta_units[m.group(2)]
        except KeyError:
            raise ValueError("Invalid timedelta units: %s" % m.group(2))

    return timedelta(seconds=units * float(val))
    

def parse_range(s):
    """ Parse the string `s` representing a range of times
    (e.g., `"12:00 PM to 1:00 PM"` or `"last 2 weeks"`).
    Upon success returns a pair of `datetime.datetime` objects
    representing the beginning and end of the time range.
    If the string cannot be parsed, raises `ValueError`.
    """

    s = s.strip()

    # first try something of the form "time1 to time2"
    i = s.split('to')
    if len(i) == 2:
        try:
            p = TimeParser()
            start = p.parse(i[0])
            end = p.parse(i[1])
            return start, end
        except ValueError:
            pass

    # try something of the form "last time"
    if s.startswith('last'):
        try:
            duration = parse_timedelta(s[4:].strip())
            end = datetime.now()
            start = end - duration
            return start, end
        except ValueError:
            pass

    # if it still doesn't work, try the pilot time filter syntax
    # which looks like "time1,time2"
    i = s.split(',')

    # XXX normally, Pilot formats filters with the
    # following syntax:
    # 11/20/2007 12:28:01.719742,11/20/2007 12:35:19.719742, GMT -8
    # We will need to handle the third piece if we want to avoid problems
    # with daylight savings
    if len(i) >= 2:
        try:
            p = TimeParser()
            start = p.parse(i[0])
            end = p.parse(i[1])
            return start, end
        except ValueError:
            pass

    raise ValueError('cannot parse time range "%s"' % s)
    

# XXX probably incorrect in some locales?
_fmt_widths = {
    'a': 3, 'A': 9, 'b': 3, 'B': 9, 'c': 24,
    'd': 2, 'f': 6, 'H': 2, 'I': 2, 'j': 3,
    'm': 2, 'M': 2, 'p': 2, 'S': 2, 'U': 2,
    'w': 1, 'W': 2, 'x': 8, 'X': 8, 'y': 2,
    'Y': 4, 'z': 5, 'Z': 3, '%': 1
    }

def max_width(fmt):
    """ Given a time formatting string (i.e., a string that can be
    used as the `fmt` option to `datetime.strftime`, compute the
    maximum length of a formatted date string """

    m = 0
    i = 0
    while i < len(fmt):
        if fmt[i] == '%':
            try:
                i += 1
                m += _fmt_widths[fmt[i]]
            except IndexError:
                raise ValueError('do not understand %%%s in format string' % fmt[i])
        else:
            m += 1

        i += 1

    return m
