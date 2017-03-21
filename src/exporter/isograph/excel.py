"""
Microsoft Office Excel files emitter for Isograph.
"""

import logging
import os
import pyexcel_xls as xls
from datetime import datetime as dt
from collections import OrderedDict

from exporter.isograph.rows import *
from exporter.isograph.rows import SCHEMA

_logger = logging.getLogger(__name__)


class ExcelEmitter(object):
    """
    Microsoft Office Excel emitter for Isograph.
    """

    sheet_attributes = ['_blocks', '_repeat_blocks', '_nodes', '_connections']

    def __init__(self, output_dir):
        # Setup output path
        nobasedir = output_dir is None
        basedir = output_dir if not nobasedir else ''
        output_path = 'model_{}.xls'.format(
            dt.now().strftime('%Y%m%d_%H%M%S_%f'))
        self._output_path = os.path.join(basedir, output_path)
        _logger.info('Output path is: ' + os.path.abspath(self.output_path))
        # Initialize output row containers.
        # First row is the header, which is needed to automate
        # the column mappings when importing to Isograph.
        self._blocks = [RbdBlockRow.header()]
        self._repeat_blocks = [RbdRepeatBlockRow.header()]
        self._nodes = [RbdNodeRow.header()]
        self._connections = [RbdConnectionRow.header()]
        # Initialize output identifier containers.
        self._ids = {}
        # self._block_ids = {}
        # self._repeat_block_ids = {}
        # self._node_ids = {}
        # Initialize output identifier counters.
        self._next_block_id = 0
        self._next_repeat_block_id = 0
        self._next_node_id = 0

    def add_block(self, **kwargs):
        self._blocks.append(RbdBlockRow(**kwargs))
        self._ids[kwargs['Id']] = self._next_block_id
        self._next_block_id += 1

    def add_repeat_block(self, **kwargs):
        # TODO
        pass

    def add_node(self, **kwargs):
        self._nodes.append(RbdNodeRow(**kwargs))
        self._ids[kwargs['Id']] = self._next_node_id
        self._next_node_id += 1

    def add_connection(self, identifier, page, src_id, src_type, dst_id,
                       dst_type):
        # TODO
        src_index = self._ids[src_id]
        dst_index = self._ids[dst_id]
        connection = RbdConnectionRow(
            Id=identifier,
            Page=page,
            Type='Diagonal',
            InputObjectIndex=src_index,
            InputObjectType=src_type,
            OutputObjectIndex=dst_index,
            OutputObjectType=dst_type)
        self._connections.append(connection)

    def commit(self):
        data = OrderedDict(
            [(sheet, [[getattr(row, k) for k in SCHEMA[sheet]]
                      for row in getattr(self, attr)])
             for sheet, attr in zip(SCHEMA.keys(), self.sheet_attributes)])
        xls.save_data(self.output_path, data=data)

    @property
    def output_path(self):
        return self._output_path
