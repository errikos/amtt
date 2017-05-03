"""
Microsoft Office Excel files emitter for Isograph.
"""

import logging
from collections import OrderedDict

import pyexcel_xls as xls

from amtt.exporter.isograph.rows import *
from amtt.exporter.isograph.rows import SCHEMA
from amtt.exporter.isograph.emitter import IsographEmitter

_logger = logging.getLogger(__name__)


class ExcelEmitter(IsographEmitter):
    """
    Microsoft Office Excel emitter for Isograph.
    """

    def __init__(self, output_dir):
        # Call to super-class initializer
        super().__init__(output_dir)
        # First row is the header, which is needed to automate
        # the column mappings when importing to Isograph.
        self._blocks.append(RbdBlockRow.header())
        self._repeat_blocks.append(RbdRepeatBlockRow.header())
        self._nodes.append(RbdNodeRow.header())
        self._connections.append(RbdConnectionRow.header())

    def commit(self):
        # List ExcelEmitter attributes.
        sheet_attributes = [
            '_blocks', '_repeat_blocks', '_nodes', '_connections'
        ]
        data = OrderedDict(
            [(sheet, [[getattr(row, k) for k in SCHEMA[sheet]]
                      for row in getattr(self, attr)])
             for sheet, attr in zip(SCHEMA.keys(), sheet_attributes)])
        xls.save_data(self.output_path, data=data)
