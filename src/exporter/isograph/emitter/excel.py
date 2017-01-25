"""
Microsoft Office Excel emitter module.
"""

from . import Emitter
from collections import OrderedDict

import pyexcel_xls as xls
import logging

_logger = logging.getLogger('exporter.isograph.emitter')

_schema = OrderedDict([
    ('RbdBlocks', ['Id', 'Page', 'XPosition', 'YPosition']),
    ('RbdRepeatBlocks', ['Id', 'Page', 'XPosition', 'YPosition']),
    ('RbdNodes', ['Id', 'Page', 'Vote', 'XPosition', 'YPosition']),
    ('RbdConnections', [
        'Id', 'Page', 'InputObjectIndex', 'InputObjectType',
        'OutputObjectIndex', 'OutputObjectType'
    ]),
])


class RbdBlock(object):
    def __init__(self, **kwargs):
        for key in _schema['RbdBlocks']:
            setattr(self, key, kwargs.get(key))

    @staticmethod
    def header():
        return RbdBlock(**{k: k for k in _schema['RbdBlocks']})


class RbdNode(object):
    def __init__(self, **kwargs):
        for key in _schema['RbdNodes']:
            setattr(self, key, kwargs.get(key))

    @staticmethod
    def header():
        return RbdNode(**{k: k for k in _schema['RbdNodes']})


class RbdConnection(object):
    def __init__(self, **kwargs):
        for key in _schema['RbdConnections']:
            setattr(self, key, kwargs.get(key))

    @staticmethod
    def header():
        return RbdConnection(**{k: k for k in _schema['RbdConnections']})


class ExcelEmitter(Emitter):
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
            [(sheet, [[getattr(row, k) for k in _schema[sheet]]
                      for row in getattr(self, attr).values()])
             for sheet, attr in zip(_schema.keys(), self.sheet_attributes)])
        xls.save_data(self._file_path, data)

    @property
    def file_path(self):
        return self._file_path
