# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.


class APIVersion:
    """Simple class to wrap information
    about the client-side supported API versions"""

    def __init__(self, v):
        if isinstance(v, basestring):
            L = v.split(".")
            self.major = int(L[0])
            self.minor = int(L[1])
        elif isinstance(v, APIVersion):
            self.major = v.major
            self.minor = v.minor
        else:
            raise ValueError("Invalid type: %s" % type(v))

    def __str__(self):
        return "%s.%s" % (self.major, self.minor)

    def __cmp__(self, other):
        if self.major < other.major:
            return -1

        if self.major > other.major:
            return 1

        if self.minor < other.minor:
            return -1

        if self.minor > other.minor:
            return 1

        return 0

if __name__ == "__main__":
    a = APIVersion("1.0")
    a2 = APIVersion("1.0")
    a3 = APIVersion(a)
    b = APIVersion("1.1")
    c = APIVersion("2.1")

    print "a, a2, a3, b, c", a, a2, a3, b, c
    print "a < b", a < b
    print "a > b", a > b
    print "a > c", a > c
    print "a == a2", a == a2
    print "a > a2", a > a2
    print "a >= a2", a >= a2
