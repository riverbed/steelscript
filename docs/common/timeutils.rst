:py:mod:`steelscript.common.timeutils`
======================================

.. automodule:: steelscript.common.timeutils

Timezone Handling
-----------------

.. autofunction:: ensure_timezone
.. autofunction:: force_to_utc

Conversions
-----------

Devices often represesent time as seconds (or microseconds or
nanoseconds) since the Unix epoch (January 1, 1970).  The following
functions are useful for converting to and from native Python
``datetime.datetime`` objects:

.. autofunction:: datetime_to_seconds
.. autofunction:: datetime_to_microseconds
.. autofunction:: datetime_to_nanoseconds
.. autofunction:: usec_string_to_datetime
.. autofunction:: nsec_to_datetime
.. autofunction:: usec_string_to_timedelta
.. autofunction:: timedelta_total_seconds

Parsing dates and times
-----------------------

.. autoclass:: TimeParser

Parsing time ranges
-------------------

.. autofunction:: parse_timedelta
.. autofunction:: parse_range
