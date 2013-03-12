# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


import os
import subprocess
import logging
import rvbd.shark.view

wireshark_candidates = ["C:/Program Files/Wireshark/wireshark.exe",
                        "/usr/bin/wireshark", 
                        "/usr/local/bin/wireshark",
                        "/Applications/Wireshark.app/Contents/Resources/bin/wireshark"]

def _get_wireshark_path():
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)
    for f in wireshark_candidates:
        if is_exe(f):
            return f
                       


def sendToWireshark(uri, filters=None):
    """ 
    Launch wireshark and send packets to it. 

    URI syntax is documented in shark.view.SharkView. Optional list of filters is applied to packets before pulling the from shark.
    """
    if filters is None:
        filters = []

    ws = _get_wireshark_path()
    if not ws:
        logging.warning("sendToWireshark: could not find wireshark executable")
        return
    p2sview = rvbd.shark.view.PipeToSocket(uri, filters)


    p2sview.apply()

    # The args are the same as those used by Pilot Console to launch wireshark.
    pipe=subprocess.Popen([ws, 
                           "-o", "console.log.level:127", "-k", 
                           "-o", "capture.auto_scroll: FALSE", "-i", 
                           "-", "-X", "stdin_descr:%s" % uri],
                          bufsize=-1, stdin=subprocess.PIPE).stdin
    p2sview.get_data(pipe)
    p2sview.close()

def sendToFile(uri, outfile, filters=None):
    """ 
    Send packets to the specified outfile file

    URI syntax is documented in shark.view.SharkView. Optional list of filters is applied to packets before pulling the from shark.
    """
    if filters is None:
        filters = []

    p2sview = rvbd.shark.view.PipeToSocket(uri, filters)
    p2sview.apply()

    fd = open(outfile, 'w')
    p2sview.get_data(fd)
    fd.close()
