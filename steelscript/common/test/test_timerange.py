# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import unittest

from collections import OrderedDict

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from steelscript.common.timeutils import parse_range, parse_timedelta


class TimeRangeTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def close_to_now(self, dt):
        self.assertTrue(dt - datetime.now() < timedelta(milliseconds=1))

    def within_unit(self, dt, unit):
        return datetime.now() - dt <= parse_timedelta(unit)

    def on_boundary(self, dt, unit):
        start_units = OrderedDict()
        start_units['year'] = 1
        start_units['month'] = 1
        start_units['day'] = 1
        start_units['hour'] = 0
        start_units['minute'] = 0
        start_units['second'] = 0
        start_units['microsecond'] = 0

        index = start_units.keys().index(unit)
        for unit in start_units.keys()[index + 1:]:
            self.assertTrue(getattr(dt, unit) == start_units[unit])

    def test_range_seconds(self):
        start, end = parse_range('last 3 seconds')
        self.assertTrue(end - start, timedelta(0, 3))
        self.close_to_now(end)

        start, end = parse_range('previous 3 seconds')
        self.assertTrue(end - start, timedelta(0, 3))
        self.within_unit(start, 'second')

        start, end = parse_range('this second')
        self.within_unit(start, 'second')

    def test_range_minutes(self):
        start, end = parse_range('last 3 minutes')
        self.assertTrue(end - start, timedelta(0, 3*60))

        start, end = parse_range('previous 3 minutes')
        self.assertTrue(end - start, timedelta(0, 3*60))
        self.on_boundary(end, 'minute')
        self.within_unit(end, 'minute')

        start, end = parse_range('this minute')
        self.on_boundary(start, 'minute')
        self.close_to_now(end)
        self.within_unit(start, 'minute')

    def test_range_hours(self):
        start, end = parse_range('last 3 hours')
        self.assertTrue(end - start, timedelta(0, 60*60))

        start, end = parse_range('previous 3 hours')
        self.assertTrue(end - start, timedelta(0, 60*60))
        self.on_boundary(end, 'hour')
        self.within_unit(end, 'hour')

        start, end = parse_range('this hour')
        self.on_boundary(start, 'hour')
        self.close_to_now(end)
        self.within_unit(start, 'hour')

    def test_range_days(self):
        start, end = parse_range('last 3 days')
        self.assertTrue(end - start, parse_timedelta('3 days'))

        start, end = parse_range('yesterday')
        self.assertTrue(end - start, parse_timedelta('1 day'))
        self.on_boundary(end, 'day')
        self.within_unit(end, 'day')

        start, end = parse_range('today')
        self.on_boundary(start, 'day')
        self.close_to_now(end)
        self.within_unit(start, 'day')

    def test_range_weeks(self):
        start, end = parse_range('last 3 weeks')
        self.assertTrue(end - start, parse_timedelta('3 weeks'))

        start, end = parse_range('previous 3 weeks')
        self.assertTrue(end - start, parse_timedelta('3 weeks'))
        self.on_boundary(end, 'day')
        self.within_unit(end, 'week')
        self.assertTrue(end.weekday() == 6)

        start, end = parse_range('this week')
        self.on_boundary(start, 'day')
        self.close_to_now(end)
        self.within_unit(start, 'week')
        self.assertTrue(start.weekday() == 6)

        start, end = parse_range('previous week', begin_monday=True)
        self.assertTrue(start.weekday() == 0)

        start, end = parse_range('this week', begin_monday=True)
        self.assertTrue(start.weekday() == 0)

    def test_range_months(self):

        start, end = parse_range('last 3 months')
        self.assertTrue(end - start, parse_timedelta('3 months'))

        start, end = parse_range('previous 3 months')
        self.assertEquals(start, end - relativedelta(months=3))
        self.on_boundary(end, 'month')
        self.within_unit(end, 'month')

        start, end = parse_range('this month')
        self.on_boundary(start, 'month')
        self.close_to_now(end)
        self.within_unit(start, 'month')

    def test_range_quarters(self):
        start, end = parse_range('last 3 q')
        self.assertTrue(end - start, parse_timedelta('3 q'))

        start, end = parse_range('previous 3 q')
        self.assertEquals(start, end - relativedelta(months=9))
        self.on_boundary(end, 'month')
        self.within_unit(end, 'quarter')
        self.assertTrue(end.month in [1, 4, 7, 10])

        start, end = parse_range('this q')
        self.on_boundary(start, 'month')
        self.close_to_now(end)
        self.within_unit(start, 'quarter')
        self.assertTrue(start.month in [1, 4, 7, 10])

    def test_range_years(self):

        start, end = parse_range('last 3 years')
        self.assertTrue(end - start, parse_timedelta('3 years'))

        start, end = parse_range('previous 3 years')
        self.assertEquals(start, end - relativedelta(years=3))
        self.on_boundary(end, 'year')
        self.within_unit(end, 'year')

        start, end = parse_range('this year')
        self.on_boundary(start, 'year')
        self.close_to_now(end)
        self.within_unit(start, 'year')
