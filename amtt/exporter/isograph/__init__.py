"""
Exporter module for Isograph Availability Workbench.
"""
import logging
import networkx as nx
from itertools import count

from amtt.translator.ir import component_basename
from amtt.exporter import Exporter
from amtt.exporter.isograph.emitter.xml import XmlEmitter
from amtt.exporter.isograph.rbd import Rbd
from amtt.exporter.isograph.rows import *

_logger = logging.getLogger(__name__)


class IsographExporter(Exporter):
    """
    Exporter to export the model to Isograph.
    """

    def __init__(self, translator):
        self._translator = translator
        self._emitter = XmlEmitter(translator.output_basedir)

    @staticmethod
    def normalize_block_names(ir_container):
        g = ir_container.component_graph
        if ir_container.uses_templates:
            relabel_mapping = {n: c for n, c in zip(g.nodes_iter(), count(1))}
            del relabel_mapping['ROOT']  # We don't want to relabel ROOT
            nx.relabel_nodes(g, relabel_mapping, copy=False)
            for u, v in nx.bfs_edges(g, 'ROOT'):
                vo = g.node[v]['obj']  # Get a hold of the associated object
                # Set base name as description
                vo.description = component_basename(vo.name)
                # Set ID number as name
                vo.name = v

    def export(self):
        # Normalize block names, if necessary
        self.normalize_block_names(self._translator.ir_container)
        # Create block diagram from input
        rbd = Rbd()
        rbd.from_ir_container(self._translator.ir_container)
        # Dump block diagram to output
        rbd.serialize(self._emitter)
