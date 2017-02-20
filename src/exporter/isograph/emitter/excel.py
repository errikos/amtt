"""
Microsoft Office Excel emitter module.
"""

from . import IsographEmitter, RbdBlock, RbdConnection, RbdNode
from . import SCHEMA
from collections import OrderedDict

import pyexcel_xls as xls
import logging

_logger = logging.getLogger('exporter.isograph.emitter')


class ExcelEmitter(IsographEmitter):
    """
    Microsoft Office Excel emitter for Isograph.
    """

    sheet_attributes = ['_blocks', '_repeat_blocks', '_nodes', '_connections']

    def __init__(self, file_path):
        self._file_path = file_path
        self._blocks = OrderedDict([('__HEADER__', RbdBlock.header())])
        self._repeat_blocks = OrderedDict([('__HEADER__', RbdBlock.header())])
        self._nodes = OrderedDict([('__HEADER__', RbdNode.header())])
        self._connections = OrderedDict(
            [('__HEADER__', RbdConnection.header())])

    def add_block(self, block):
        self._blocks[block.Id] = block

    def add_repeat_block(self, repeat_block):
        self._repeat_blocks[repeat_block.Id] = repeat_block

    def add_node(self, node):
        self._nodes[node.Id] = node

    def add_connection(self, connection):
        self._connections[connection.Id] = connection

    def commit(self):
        data = OrderedDict(
            [(sheet, [[getattr(row, k) for k in SCHEMA[sheet]]
                      for row in getattr(self, attr).values()])
             for sheet, attr in zip(SCHEMA.keys(), self.sheet_attributes)])
        xls.save_data(self._file_path, data)

    def get_index_type_by_id(self, id):
        if id in self._nodes:
            return list(self._nodes).index(id) - 1, 'Rbd node'
        elif id in self._blocks:
            return list(self._blocks).index(id) - 1, 'Rbd block'
        elif id in self._repeat_blocks:
            return list(self._repeat_blocks).index(id) - 1, 'Rbd repeat block'

    @property
    def file_path(self):
        return self._file_path
