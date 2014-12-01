# This will trigger an ImportError other than what we would get if
# this module did not exist at all.

import some_random_junk_that_doesnt_exist  # noqa flake8
