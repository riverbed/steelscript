# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


import unittest
import logging
import setuptools
import sys
import csv
import traceback

import rvbd.common.app

logger = logging.getLogger(__name__)

class LogTestResult(unittest.TestResult):
    PASSED=0
    FAILED=1
    SKIPPED=2
    
    def __init__(self, stream=None, csvwriter=None):
        super(LogTestResult, self).__init__()
        self.stream = stream
        self.csvwriter = csvwriter
    
    def addTestResult(self, test, status, addmsg=None, tb=None):
        if   status == self.PASSED:  statusmsg = "PASS"
        elif status == self.SKIPPED: statusmsg = "SKIP"
        else:                        statusmsg = "FAIL"


        if addmsg:
            msg = "%s: %s" % (statusmsg, addmsg)
        else:
            msg = statusmsg
            
        logger.info("---- Test %s: %s" % (test.id(), msg))
        if tb:
            logger.debug("Traceback:\n%s" % ''.join(traceback.format_tb(tb)))
            
        if self.stream:
            self.stream.write("%s...%s" % (statusmsg, test.id()))
            if addmsg:
                self.stream.write(" (%s)" % addmsg)
            self.stream.write("\n")
            

        if self.csvwriter:
            self.csvwriter.writerow([test.id(), status, msg])
    
    def startTest(self, test):
        super(LogTestResult, self).startTest(test)
        logger.info("---- Test Starting: %s" % test)

    def addSuccess(self, test):
        super(LogTestResult, self).addSuccess(test)
        self.addTestResult(test, self.PASSED)
        
    def addError(self, test, err):
        super(LogTestResult, self).addError(test, err)
        self.addTestResult(test, self.FAILED, ("error %s " % (err[1])), err[2])

    def addFailure(self, test, err):
        super(LogTestResult, self).addFailure(test, err)
        self.addTestResult(test, self.FAILED, err[1], err[2])
    
    def addSkip(self, test, reason):
        super(LogTestResult, self).addSkip(test, reason)
        self.addTestResult(test, self.SKIPPED, "skipped")

    def addExpectedFailure(self, test, err):
        super(LogTestResult, self).addExpectedFailure(test, err)
        self.addTestResult(test, self.PASSED, "expected failure: %s" % err[1])

    def addUnexpectedSuccess(self, test):
        super(LogTestResult, self).addUnexpectedSuccess(test)
        self.addTestResult(test, self.FAILED, "unexpected pass")

class LogTestRunner:
    def __init__(self, stream=None, csv=None):
        self.stream = stream
        self.csv = csv
        
    def run(self, test):
        if self.csv:
            csvfile = open(self.csv, "wb")
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["test", "status", "msg"])
        else:
            csvfile = None
            csvwriter = None
        result = LogTestResult(self.stream, csvwriter)
        #starttime = time.time()
        starttime = 0
        test(result)

        if csvfile:
            csvfile.close()
            
        #endtime = time.time()
        endtime = 0
        failed, errored = map(len, (result.failures, result.errors))
        totaltime = endtime - starttime
        totalfailed = failed + errored
        totalpassed = result.testsRun - totalfailed
        successrate = 100.0 * float(totalpassed) / float(result.testsRun)
        logger.info("==== Test Results: Ran %d tests in %.1f secs, %d succeeded (%.1f%%)" %
                    (result.testsRun, totaltime, totalpassed, successrate))

        if self.stream:
            self.stream.write("Test Results: Ran %d tests in %.1f secs, %d succeeded (%.1f%%)\n"
                              % (result.testsRun, totaltime, totalpassed, successrate))

        return result.wasSuccessful()
        
class LogTestCommand(setuptools.Command):

    description = "Run tests with logging"

    user_options = [
        ('logfile=', 'l', 'Destination file for log messages'),
        ('dir=', 'd', 'Directory to search for tests'),
        ('test=', 't', 'Specific test to run (module, test case class, etc.)'),
        ('csv=', 'c', 'Write results to a CSV file'),
        ('httpdebug=', None, 'Set http lib debug level')
        ]
    
    def initialize_options(self):
        self.logfile = None
        self.dir = None
        self.test = None
        self.csv = None
        self.httpdebug = 0

    def finalize_options(self):
        if self.dir is not None and self.test is not None:
            raise DistutilsOptionError("Must specify only one of --dir and --test")
        if self.dir is None:
            self.dir = "."
        if self.httpdebug:
            self.httpdebug = int(self.httpdebug)

    def run(self):
        rvbd.common.app.Application.start_logging(logging.DEBUG, self.logfile,
                                                  httplib_debuglevel=self.httpdebug)

        self.stream = None
        if self.logfile is not None:
            self.stream = sys.stderr

        if self.stream:
            self.stream.write("Logfile: %s\n" % self.logfile)

        testloader = unittest.TestLoader()
        testloader.sortTestMethodsUsing = None
        
        if self.test:
            tests = testloader.loadTestsFromName(self.test)
        else:
            tests = testloader.discover(self.dir)

        tr = LogTestRunner(stream=self.stream, csv=self.csv)
        success = tr.run(tests)

        if success:
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests = loader.discover('.')

    runner = LogTestRunner(stream=sys.stdout)
    status = runner.run(tests)

    sys.exit(status)
    
