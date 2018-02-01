# Copyright (c) 2018 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
This module contains functions for parsing and analyzing file data.
"""

import mimetypes

from steelscript.common.exceptions import RvbdException

# MIME type to use if mimetypes can't detect the real file mime type
DEFAULT_MIME_TYPE = "application/octet-stream"


def get_mime_type(file_name, strict=True):
    """
    Detect the MIME Type of a open file object by inspecting the first
    MAGIC_LEN bytes of the file data.
    :param file_name: file basename
    :param strict: From the mimetypes docs - The optional strict argument is a
           flag specifying whether the list of known MIME types is limited to
           only the official types registered with IANA.
    :return: The files MIME type if it could be detected. DEFAULT_MIME_TYPE is
             returned if the file type could not be determined.
    """
    if len(file_name.split('.')) >= 2:
        mime_type, encode = mimetypes.guess_type(file_name, strict=strict)
        if mime_type is None:
            mime_type = DEFAULT_MIME_TYPE
        return mime_type
    else:
        raise RvbdException("Mime type detection requires a file name to have "
                            "an extension. Please rename {0} to have an "
                            "appropriate file extension."
                            "".format(file_name))
