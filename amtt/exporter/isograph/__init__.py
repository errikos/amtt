"""Exporter module for Isograph Availability Workbench."""
import logging
import networkx as nx
from itertools import count

from amtt.translator.ir import component_basename
from amtt.exporter import Exporter
from amtt.exporter.isograph.emitter.xml import XmlEmitter
from amtt.exporter.isograph.rbd import Rbd
from amtt.exporter.isograph._functions import *

_logger = logging.getLogger(__name__)


class IsographExporter(Exporter):
    """Exporter to export the model to Isograph."""

    def __init__(self, translator):
        """Initialize IsographExporter."""
        self._translator = translator
        self._emitter = XmlEmitter(translator.output_basedir)

    @staticmethod
    def normalize_block_names(ir_container):
        """Normalize the component (block) names.

        Isograph imposes a 40 character limit for the component names.
        In case the model uses template components, there is a big chance that
        the names will grow very big in length. Therefore, we store the
        base name in the description field and assign a unique integer (ID)
        as the components name.
        """
        g = ir_container.component_graph
        if ir_container.uses_templates:
            _logger.info('Template usage detected:')
            _logger.info(' * Normalizing component names for Isograph')
            # Create relabeling mapping.
            # Each component name will be replaced with a number (ID).
            relabel_mapping = {n: c for n, c in zip(g.nodes_iter(), count(1))}
            del relabel_mapping['ROOT']  # We don't want to relabel ROOT
            # Relabel and rename components graph
            # -- copy=False means "relabel in-place"
            nx.relabel_nodes(g, relabel_mapping, copy=False)
            for u, v in nx.bfs_edges(g, 'ROOT'):
                # -- get a hold of the associated object
                vo = g.node[v]['obj']
                # -- set base name as description
                vo.description = component_basename(vo.name)
                # -- set ID number as name
                vo.name = v
            # Note: No need to relabel or rename failures graph

    def export(self):
        """Export the model to Isograph importable format."""
        # Normalize block names, if necessary
        self.normalize_block_names(self._translator.ir_container)
        # Export RBD (blocks, nodes, connections, block rules)
        self._export_rbd()
        # Export failure model definitions
        self._export_failure_models()
        # Export manpower
        self._export_manpower()
        # Export spares
        self._export_spares()
        # Write output file
        self._emitter.commit()

    def _export_rbd(self):
        # Create block diagram from input
        rbd = Rbd()
        rbd.from_ir_container(self._translator.ir_container)
        # Dump reliability block diagram to output
        rbd.serialize(self._emitter)

    def _export_failure_models(self):
        fmodel_export(self._translator.ir_container, self._emitter)

    def _export_manpower(self):
        manpower_export(self._translator.ir_container, self._emitter)

    def _export_spares(self):
        spares_export(self._translator.ir_container, self._emitter)
