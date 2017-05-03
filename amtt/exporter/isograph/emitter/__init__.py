"""
Emitter module/class for Isograph.
"""

import os
import abc
import logging
from datetime import datetime as dt

from amtt.exporter.isograph.rows import *

_logger = logging.getLogger(__name__)


class IsographEmitter(object):
    """
    Base emitter class for Isograph.
    """

    def __init__(self, output_dir):
        # Setup output path
        nobasedir = output_dir is None
        basedir = output_dir if not nobasedir else ''
        output_path = 'model_{}'.format(dt.now().strftime('%Y%m%d_%H%M%S_%f'))
        self._output_path = os.path.join(basedir, output_path)
        _logger.info('Output path is: ' + os.path.abspath(self.output_path))
        # Initialize output row containers.
        self._blocks = []
        self._repeat_blocks = []
        self._nodes = []
        self._connections = []
        # Initialize output identifier containers.
        self._ids = {}
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
        src_index = self._ids[src_id]
        dst_index = self._ids[dst_id]
        connection = RbdConnectionRow(
            Id=identifier,
            Page=page,
            Type='Horizontal/vertical',
            InputObjectIndex=src_index,
            InputObjectType=src_type,
            OutputObjectIndex=dst_index,
            OutputObjectType=dst_type)
        self._connections.append(connection)

    @property
    def output_path(self):
        return self._output_path

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError('IsographEmitter should be sub-classed')
