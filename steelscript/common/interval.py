# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import copy

__all__ = ['Interval', 'IntervalList']


class Interval(object):
    """
    Creates an object from an interval with start and end. Start and end are
    objects that can be compared using operators such as '<=', '>=' and '=='.
    Examples:
        >>> int1, int2 = Interval(1, 4), Interval(2, 5)
        >>> int1 - int2
        Interval(1, 2)
        >>> int1, int2 = Interval(1, 2), Interval(0, 4)
        >>> int1 in int2
        True
        >>> int1, int2 = Interval(1, 3), Interval(1, 3)
        >>> int1 == int2
        True
        >>> dt1 = datetime.datetime(2016, 5, 18, 13)
        >>> dt2 = datetime.datetime(2016, 5, 18, 14)
        >>> dt3 = datetime.datetime(2016, 5, 18, 10)
        >>> dt4 = datetime.datetime(2016, 5, 18, 15)
        >>> int1 = Interval(dt1, dt2)
        >>> int2 = Interval(dt3, dt4)
        >>> int1 in int2
        True
    """

    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end

    def __str__(self):
        return '%s, %s' % (self.start, self.end)

    def __repr__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, self.start, self.end)

    def __contains__(self, item):
        """One interval is contained by another if the range from start to end
        of the first interval is within the range of start to end of the
        second interval.

        :params item: an Interval object
        :returns: True or False
        """
        return item.start >= self.start and item.end <= self.end

    def __sub__(self, other=None):
        """Subtracting an Interval object or an IntervalList object.
        If subtracting an Interval object, the method returns an interval
        object with the part of interval from left operand that does not
        belong to the subtracted interval object.
        If subtracting an IntervalList object, the method returns the an
        IntervalList object, with each interval contained in the left
        operand and not contained in any of the interval objects in right
        operand.
        Example:
            >>>int1, int2 = Interval(1, 2), Interval(4, 5)
            >>>int3 = Interval(0, 7)
            >>>int3 - IntervalList([int1, int2])
            IntervalList([Interval(0, 1), Interval(2, 4), Interval(5, 7)])

        :param other: an Interval/IntervalList object or None
        :return: IntervalList object
        """

        if other is None:
            return IntervalList([self])

        if self in other:
            return IntervalList([])

        if isinstance(other, IntervalList):
            remain = IntervalList([self])
            for interval in other:
                remain -= interval
            return remain

        else:  # isinstance(other, Interval):
            if other in self:
                ints = [(self.start, other.start), (other.end, self.end)]
                return IntervalList([self.__class__(t[0], t[1])
                                     for t in ints if t[0] != t[1]])
            elif not self.overlap(other):
                return IntervalList([self])
            elif self.start <= other.start:
                return IntervalList([self.__class__(start=self.start,
                                                    end=other.start)])
            else:  # self.end >= other.end:
                return IntervalList([self.__class__(start=other.end,
                                                    end=self.end)])

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

    def __add__(self, other):
        """Merges two Interval objects.

        Example:
            >>>int1 = Interval(1, 4)
            >>>int2 = Interval(2, 5)
            >>>int1 + int2
            Interval(1, 5)

        :param other: Interval object
        :return: IntervalList object
        """
        if not self.overlap(other):
            return IntervalList([self, other])
        merged = self.__class__(min(self.start, other.start),
                                max(self.end, other.end))
        return IntervalList([merged])

    def overlap(self, other):
        return self.end >= other.start and self.start <= other.end

    @property
    def size(self):
        return self.end - self.start

    def intersection(self, interval_list):
        """Return intersection interval list.

        Example:
            >>>int1 = Interval(1,5)
            >>>il = IntervalList([Interval(0,2), Interval(4,6)])
            >>>int1.intersection(il) == IntervalList(Interval[1,2],
            >>>                                      Interval[4,5])

        :param interval_list: IntervalList object
        :return: IntervalList object
        """
        return self - (self - interval_list)


class IntervalList(object):
    """Creates an object from a list of Interval objects."""
    def __init__(self, intervals):
        intervals = sorted(intervals, key=lambda x: (x.start, x.end))

        # Merge overlapping intervals
        stack = []
        for itv in intervals:
            if not stack:
                stack.append(itv)
            else:
                if stack[-1].overlap(itv):
                    itv = (stack.pop() + itv)[0]
                stack.append(itv)
        self.intervals = stack

    def __repr__(self):
        intervals = ', '.join([repr(interval) for interval in self])
        return 'IntervalList([' + intervals + '])'

    def __str__(self):
        intervals = ', '.join('(' + str(interval) + ')' for interval in self)
        return '[' + intervals + ']'

    def __getitem__(self, index):
        return self.intervals[index]

    def __len__(self):
        return len(self.intervals)

    def __contains__(self, other):
        """One interval is contained in a IntervalList object if the interval
        object is contained by one of intervals within the IntervalList
        object.

        Example:
            >>>int1 = Interval(1, 2)
            >>>ints = IntervalList([Interval(0, 3), Interval(4, 5)])
            >>>int1 in ints
            True

        :param other: an Interval object.
        :return: True or False.
        """
        for interval in self.intervals:
            if other in interval:
                return True
        return False

    def __sub__(self, other):
        """Subtracting one Interval object or an IntervalList object.
        Get an IntervalList object as an aggregated results from each
        interval object subtracting the right operand object.

        Example:
            >>>int1, int2 = Interval(0, 3), Interval(4, 5)
            >>>int3 = Interval(1, 2)
            >>>ints1 = IntervalList([int1, int2])
            >>>ints1 - int3
            IntervalList([Interval(0, 1), Interval(2, 3), Interval(4, 5)])

        :param other: an Interval object or an IntervalList object
        :return: an IntervalList object
        """
        l = []
        for interval in self:
            remain = interval - other
            l.extend(remain.intervals)
        return IntervalList(l)

    def __eq__(self, other):
        """Check if two IntervalList objects are equivalent.

        Example:
            >>>ints1 = IntervalList([1, 3], [5, 6])
            >>>ints2 = IntervalList([1, 3], [5, 6])
            >>>ints1 == ints2
            True

        :param other: IntervalList object.
        :return: True or False.
        """
        return len(self) == len(other) and \
            all([self[i] == other[i] for i in range(len(self))])

    def __add__(self, other):
        """Merge one Interval object into self.

        Example:
             >>>int1 = Interval(2, 3)
             >>>ints = IntervalList([Interval(1, 2), Interval(3,4)])
             >>>ints + int1
             IntervalList([Interval(1, 4)])

        :param other: An Interval object.
        :return: An IntervalList object.
        """
        intervals = copy.copy(self.intervals)
        intervals.append(other)
        return IntervalList(intervals)

    def append(self, other):
        self.intervals.append(other)
