#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


"""
List all the key and column fields that the given shark appliance supports.
For full field details, use the -v flag.
"""

import optparse

from rvbd.shark.app import SharkApp
from rvbd.common.utils import Formatter


class FieldsApp(SharkApp):

    def add_options(self, parser):
        group = optparse.OptionGroup(parser, "Column output options")
        group.add_option('--sort-id', default=False, action='store_true',
                            help='sort by ID column instead of description')
        group.add_option('--truncate', default=False, action='store_true',
                            help='truncate description column rather than wrapping')
        group.add_option('-w', '--table-width', dest='table_width', default=120,
                            help="max width of table output, defaults to 120 characters")
        parser.add_option_group(group)

    def main(self):
        headers = ['ID', 'Description', 'Type']
        data = [(f.id, f.description, f.type) for f in self.shark.get_extractor_fields()]
        if self.options.sort_id:
            data.sort()
        Formatter.print_table(data, 
                              headers,
                              padding=2,
                              max_width=int(self.options.table_width),
                              long_column=1,
                              wrap_columns=(not self.options.truncate))


if __name__ == '__main__':
    FieldsApp().run()
