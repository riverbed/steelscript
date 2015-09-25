# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

import time


def do_poll(func, *args, **kwargs):
    """
    Creates a generator, calling a generic function with *args and **kwargs
    on each request, raising StopIteration if max_poll_retries is hit, and
    sleeping long enough such that each call is at least min_poll_interval
    apart.

    Extra args to do_poll (e.g., *args and **kwargs) will be passed as
    parameters to func.

    The iterable returned is usable in built-in python methods such as any(),
    all(), and sum().  Coupled with comprehensions, this provides a simple
    way to periodically poll a method and check output.  e.g.

        def wait_for_reboot(sh):
            return any(do_poll(is_up, sh=sh, max_poll_retries=20))

        # Verify dict key
        all(x['rate'] > 1000 for x in do_poll(show_download_stats))

    :param func:  Function object to be called on each iteration
    :param max_poll_retries:  Max times to call func.  Default 10.
    :param min_poll_interval:  Min seconds between calls.  Default 3.

    :return:  An iterable generator that calls func with args and kwargs.
    """
    # Note: In Python3 we would make these keyword-only arguments.
    max_poll_retries = kwargs.pop('max_poll_retries', 10)
    min_poll_interval = kwargs.pop('min_poll_interval', 3)

    retries = 0
    last_time = 0
    while retries < max_poll_retries:
        now_time = time.time()
        if last_time and now_time < last_time + min_poll_interval:
            time.sleep(min_poll_interval + last_time - now_time)
        last_time = time.time()
        yield func(*args, **kwargs)
        retries += 1
