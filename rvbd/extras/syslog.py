# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


""" This module contains classes that support the collection and parsing of syslog messages."""

import socket
import select
import threading
import sys
import time
import datetime
import string
import re

class Severity:
    """
    syslog severities enumeration
    """
    EMERGENCY = 0
    ALERT = 1
    CRITICAL = 2
    ERROR = 3
    WARNING = 4
    NOTICE = 5
    INFO = 6
    DEBUG = 7

class MessageFilter:
    """
    Enumeration of the message filters that the SyslogReceiver class supports
    """
    SNORT = ".* snort:.*"
    ALL = ".*"


class SyslogReceiver(threading.Thread):
    """
    Asynchronous Syslog Daemon

    This class listens on the specified port (514 by default) foo UDP syslog messages, and stores them in an array.
    """
    _listen_port = 514
    _message_filter = ".*"
    _bufsize = 8000
    _max_severity = Severity.DEBUG  # Accept all
    _facility_filter = -1
    _messages = []
    _messages_lock = threading.Lock()
    _alive = True

    def __init__(self, listen_port=514):
        self._listen_port = listen_port
        threading.Thread.__init__(self)

    def set_message_filter(self, filter):
        self._message_filter = filter
        
    def set_facility_filter(self, facility):
        self._facility_filter = facility

    def set_max_severity(self, severity):
        self._max_severity = severity
                        
    def run(self):
        #
        # Create the socket and bind it to the syslog port
        #
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("0.0.0.0", self._listen_port))
        except:
            print "Error binding to the port %d. Make sure the port is not in use.\n" % self._listen_port
            sys.exit(1)

        self.select_input = [sock]

        print "Listening on port %d" %(self._listen_port)
        print "Starting syslog collector"

        #
        # Main loop
        #
        while self._alive:
            try:
                #
                # Is there data from the socket?
                #
                inputready, outputready, exceptready = select.select(self.select_input,
                [],
                [],
                1)

                if len(inputready) == 0:
                    #
                    # No data yet
                    #
                    continue

                #
                # Yes, parse the message
                #
                data = sock.recvfrom(self._bufsize)[0]
                syslogstr = str(data)
        
                #
                # Extract Facility and Severity
                #
                fsepos = syslogstr.find('>')
                sfnum = string.atoi(syslogstr[1:fsepos])
                facility = (sfnum & 0x03f8) >> 3
                serverity = sfnum & 0x0007
        
                #
                # Apply the severity and facility filters
                #
                if serverity > self._max_severity:
                    continue
                        
                if self._facility_filter != -1:
                    if facility != self._facility_filter:
                        continue
                    
                #
                # Apply the message filter
                #
                syslog_msg = syslogstr[fsepos + 1:]
                if not(re.match(self._message_filter, syslog_msg)):
                    continue
                
                #
                # Message passes the filters. Parse its date.
                #
                msgcomp = syslog_msg.split()
                timestr = msgcomp[0] + " " + msgcomp[1] + " " + msgcomp[2]
                timestruct1900 = time.strptime(timestr, "%b %d %H:%M:%S")
                timestructnow = datetime.datetime(datetime.datetime.now().year, 
                                                  timestruct1900[1], 
                                                  timestruct1900[2],
                                                  timestruct1900[3],
                                                  timestruct1900[4],
                                                  timestruct1900[5])
                utctime = time.mktime(timestructnow.timetuple())
    
                #
                # Done. Add the message to the message list.
                #
                self._messages_lock.acquire()
                try:
                    self._messages.append((utctime, syslog_msg))
                finally:
                    self._messages_lock.release()
                    
            except socket.error:
                print ("Socket error")
                
        print("Stopping syslog collector")

    def get_messages(self):
        """
        Retrieve a copy of the available messages 

        The internal messages list is cleared as a consequence of a call to this method
        """        
        self._messages_lock.acquire()
        
        try:
            #
            # Make a copy of the message list and then clear it
            #
            messagelist = self._messages
            self._messages = []
        finally:
            self._messages_lock.release()
            
        return messagelist

    def die(self):
        self._alive = False

class SnortSyslogAlertParser:
    """
    Snort syslog message parser 

    Parses a syslog-ng udp message string containing a snort alert,
    extracting the severity, the facility, the hosts and the alert text.
    """
    
    endpoints = []
    alerttext = ""
    siginfo = ""
    includesports = True
        
    def __init__(self, syslog_msg):

        self.endpoints = []
        self.alerttext = ""
        self.siginfo = ""
        self.includesports = False
                    
        #
        # Split the message into its components
        #
        entries = re.split("] ?| ?{|} ?| ? -> ?|\n+", syslog_msg)
        
        if(len(entries) < 5):
            # We don't understand this alert
            return False

        #
        # Extract the alert text
        #
        self.alerttext = entries[1]
        
        #
        # Extract the signature info
        #
        exntries1 = re.split("snort: \[|\] *", syslog_msg)
        
        if len(exntries1) < 2:
            # We don't understand this alert
            return false
        
        self.siginfo = exntries1[1]

        #
        # Scan for ip addresses among the entries. We do this because an alert can
        # contain one or two (or more?) IP addresses.
        #
        for e in entries:
            endpcomp = re.split(":", e)

            if len(endpcomp) == 0 or len(endpcomp) > 2:
                # 0 or more than 2 column separated values: not an IP address
                continue

            if not(re.match("[0-9]+.[0-9]+.[0-9]+.[0-9]+", endpcomp[0])):
                # First value is not a valid IP address
                continue

            if len(endpcomp) == 2:
                if not(re.match("[0-9]+", endpcomp[1])):
                    # Not a valid port
                    continue

                #
                # This entry is in the form a.b.c.d:e
                #
                endpport = endpcomp[1];
                includesports = True
            else:
                #
                # This entry is in the form a.b.c.d, set 0 as the port
                #
                includesports = False
                endpport = 0;

            newendpoit = [endpcomp[0], endpport]
            self.endpoints.append(newendpoit)

    def getalerttext(self):
        return self.alerttext

    def getendpoints(self):
        return self.endpoints
    
    def getsignatureinfo(self):
        return self.siginfo


#
# Executes if the program is started normally, not if imported
#
if __name__ == '__main__':
    # Call the mainfunction that sets up threading.
    sls = SyslogReceiver()
    
    sls.set_message_filter(MessageFilter.SNORT)
    sls.set_max_severity(Severity.INFO)
    sls.set_facility_filter(4)
        
    sls.start()

    lmessages = []
    
    try:
        while True:
            lmessages = sls.get_messages() 
            if len(lmessages) == 0:
                time.sleep(1)
                continue
                    
            for msg in lmessages:
                sp = SnortSyslogAlertParser(msg[1])                
    except:
        sls.die()
        sls.join()
