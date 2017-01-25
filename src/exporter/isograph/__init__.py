"""
Exporter module for Isograph Availability Workbench.
"""

from exporter import Exporter
from .rbd import Rbd
from .emitter.excel import ExcelEmitter

from datetime import datetime as dt
import logging

_logger = logging.getLogger('exporter.isograph')


class IsographExporter(Exporter):
    """
    Exporter to export the model to Isograph.
    """

    def __init__(self, translator, output_path=None):
        if output_path is None:
            output_path = 'model_{}.xls'.format(
                dt.now().strftime('%Y%m%d_%H%M%S_%f'))
            print('Output path is: ' + output_path)
        self._translator = translator
        self._emitter = ExcelEmitter(output_path)

    def export(self):
        # create block diagram from input
        block_diagram = self._create_reliability_block_diagram()
        # dump block diagram to output

    def _create_reliability_block_diagram(self):
        """
        Create the RBD from the input (flat) objects.
        """
        block_diagram = Rbd(self._translator.flats, self._emitter)
        return block_diagram
