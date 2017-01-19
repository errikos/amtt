"""
Exporter module for Isograph Availability Workbench.
"""

import logging
from exporter import Exporter
from .rbd import Rbd

_logger = logging.getLogger('exporter.isograph')


class IsographExporter(Exporter):
    """
    Exporter to export the model to Isograph.
    """

    def __init__(self, translator):
        self._translator = translator

    def export(self):
        # create block diagram from input
        block_diagram = self._create_reliability_block_diagram()
        # dump block diagram to output

    def _create_reliability_block_diagram(self):
        """
        Create the RBD from the input (flat) objects.
        """
        block_diagram = Rbd(self._translator.flats)
        return block_diagram
