# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import unittest

from steelscript.common import Interval, IntervalList


class IntervalTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_contain(self):
        int1 = Interval(1, 3)
        int2 = Interval(2, 3)
        self.assertTrue(int2 in int1)

    def test_overlap(self):
        int1 = Interval(1, 5)
        int2 = Interval(0, 2)
        int3 = Interval(3, 4)
        int4 = Interval(4, 6)
        self.assertTrue(int1.overlap(int2))
        self.assertTrue(int2.overlap(int1))
        self.assertTrue(int3.overlap(int1))
        self.assertTrue(int1.overlap(int3))
        self.assertTrue(int4.overlap(int1))
        self.assertTrue(int1.overlap(int4))

    def test_sub(self):

        int1 = Interval(1, 5)
        int2 = Interval(3, 4)
        ints1 = IntervalList([Interval(1, 3), Interval(4, 5)])
        self.assertEqual(int2 - int1, None)
        self.assertEqual(int1 - int2, ints1)

        int1 = Interval(1, 3)
        int2 = Interval(4, 6)
        int3 = Interval(2, 5)
        ints1 = IntervalList([int1, int2])
        ints2 = IntervalList([Interval(1, 2), Interval(5, 6)])
        self.assertTrue(ints1 - int3 == ints2)

        int1 = Interval(1, 3)
        int2 = Interval(3, 5)
        self.assertEqual(int1 - int2, Interval(1, 3))

        int1 = Interval(1, 3)
        int2 = Interval(5, 8)
        ints1 = IntervalList([int1, int2])
        int3 = Interval(0, 2)
        ints2 = IntervalList([Interval(0, 1)])
        self.assertEqual(int3 - ints1, ints2)

    def test_add(self):
        int1, int2, int3 = Interval(0, 3), Interval(1, 5), Interval(0, 5)
        self.assertEqual(int1 + int2, int3)

        int4 = Interval(-1, 0)
        self.assertEqual(int2 + int4, IntervalList([int2, int4]))

        ints = IntervalList([int4, int2])
        int5 = Interval(6, 7)
        self.assertEqual(ints + int5, IntervalList([int2, int4, int5]))

        int5 = Interval(0, 1)
        self.assertEqual(ints + int5, IntervalList([Interval(-1, 5)]))

        int5 = Interval(3, 7)
        self.assertEqual(ints + int5, IntervalList([int4, Interval(1, 7)]))

if __name__ == '__main__':
    unittest.main()
