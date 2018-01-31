# Copyright (c) 2018 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
This module contains functions for parsing and analyzing file data.
"""

import magic

# How many bytes of a file to use for file type
# detection
MAGIC_LEN = 1024
# MIME type to use if magic can't detect the real file mime type
DEFAULT_MIME_TYPE = "application/octet-stream"


def get_mime_type(file_object):
    """
    Detect the MIME Type of a open file object by inspecting the first
    MAGIC_LEN bytes of the file data.
    :param file_object: An open python file object
    :return: The files MIME type if it could be detected. DEFAULT_MIME_TYPE is
             returned if the file type could not be determined.
    """
    file_object.seek(0)
    try:
        magic_code = magic.from_buffer(file_object.read(MAGIC_LEN), mime=True)
    except Exception as e:
        magic_code = DEFAULT_MIME_TYPE
    finally:
        file_object.seek(0)
    return magic_code