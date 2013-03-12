# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


'''
This script collects syslog alerts from Snort, parses them and for each of them it creates a locked clip
on the specified shark appliance

@author: ldegioanni
'''

import sys
import time
import datetime

from rvbd.shark import Shark, Time
from rvbd.shark import filter
from rvbd.extras import syslog

#########################################################################
# Global script settings
#########################################################################

# Syslog serverity filter
max_syslog_severity = syslog.Severity.INFO

# Syslog facility filter. -1 means "accept all facilities"
syslog_facility = 4

# IP address of the shark appliance to connect to
shark_address = "dorothy7.lab.nbttech.com"

# Credential to use on the shark
shark_username = "admin"
shark_pass = "admin"

# The clip will be created on the following jobs
job_name = "New Job 1"

# The length of the clip, in seconds. 30 means that the clip will contain 15 seconds before and 15 seconds after the alert.
clip_extension_s = 30

# The type of packets that each clip will contain
class ClipFilterType:
    NO_FILTER = 0       # All the packets captured by the Shark during the time covered by the clip
    ATTACKER = 1        # Packets sent or received by the attacker
    VICTIM = 2          # Packets sent or received by the victim
    CONVERSATION = 3    # Packets between the attacker and the victim, on any port
    FLOWS = 4           # Packets between the attacker and the victim, on the ports specified by the alert

clip_filter = ClipFilterType.ATTACKER

#########################################################################
# Script body
#########################################################################

uri = "https://%s:%s@%s:61898" % (shark_username, shark_pass, shark_address)

#
# Connect to the Shark
#
sk = Shark(shark_address, username=shark_username, password=shark_pass)

print "succesfully connected to Shark " + shark_address

#
# Locate the jobs that will need to be used
#
job_to_use = sk.get_capture_job_by_name(job_name)
     
#
# Configure the syslog sink with the proper filters and start it
#
sls = syslog.SyslogReceiver()

sls.set_message_filter(syslog.MessageFilter.SNORT)
sls.set_max_severity(max_syslog_severity)
sls.set_facility_filter(syslog_facility)
    
sls.start()

lmessages = []

#
# Wait for the alerts to come and create a clip for all of them
#
try:
    while True:
        #
        # Get the messages from the syslog server
        #
        lmessages = sls.get_messages() 
        if len(lmessages) == 0:
            time.sleep(1)
            continue
                
        for msg in lmessages:
            #
            # Extract the message details
            #
            alert_time = msg[0]
            sp = syslog.SnortSyslogAlertParser(msg[1])
                            
            #
            # Create the filters for this clip 
            #
            filters = []
            
            # 1. The time filter for +-clip_extension_s/2 around the event
            filters.append(filter.TimeFilter(alert_time - clip_extension_s / 2, alert_time + clip_extension_s / 2))
            
            # 2. The endpoint (or endpoints) filter 
            endpoints = sp.getendpoints()
            
            if clip_filter != ClipFilterType.NO_FILTER:
                # make sure the alert has two endpoints
                if len(endpoints) == 2:
                    if clip_filter == ClipFilterType.ATTACKER:
                        filters.append(filter.CubeFilter("ip::ip.str=\"%s\"" % endpoints[0][0]))
                    elif clip_filter == ClipFilterType.VICTIM:
                        filters.append(filter.CubeFilter("ip::ip.str=\"%s\"" % endpoints[1][0]))
                    elif clip_filter == ClipFilterType.CONVERSATION:
                        filters.append(filter.CubeFilter("(ip::ip.str=\"%s\") & (ip::ip.str=\"%s\")" % (endpoints[0][0], endpoints[1][0])))
                    elif clip_filter == ClipFilterType.FLOWS:
                        # Some alerts (e.g. the ICMP ones) come without a port. In that case we fallback into the conversation case
                        if(endpoints[0][1] == 0):
                            filters.append(filter.CubeFilter("(ip::ip.str=\"%s\") & (ip::ip.str=\"%s\")" % (endpoints[0][0], endpoints[1][0])))
                        else:
                            filters.append(filter.CubeFilter("((ip::source_ip.str=\"%s\" & ip::transport.source_port=\"%s\") & (ip::destination_ip.str=\"%s\" & ip::transport.destination_port=\"%s\")) | ((ip::source_ip.str=\"%s\" & ip::transport.source_port=\"%s\") | (ip::destination_ip.str=\"%s\" & ip::transport.destination_port=\"%s\"))" \
                                                                  % (endpoints[0][0], endpoints[0][1], endpoints[1][0], endpoints[1][1], endpoints[1][0], endpoints[1][1], endpoints[0][0], endpoints[0][1])))

            #
            # Create the clip
            #
            infotext = "[" + sp.getsignatureinfo() + "]-" + sp.getalerttext()
            print "%s - %s" %(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), infotext) 
            
            sk.create_clip_from_jobhandle(job_to_use.handle, filters, "SNORT" + infotext)
                
except:
    sls.die()
    sls.join()
    raise
