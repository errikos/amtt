"""
The translator module.
"""

import logging

from exporter.isograph import IsographExporter
from errors import ExporterError
from .rows import RowsContainer
from .ir import IRContainer

_logger = logging.getLogger(__name__)


class Translator(object):
    """
    The translator class.
    """

    def __init__(self, loader, target, output_basedir):
        """
        The Translator constructor.

        Args:
            loader (Loader): A loader instance, used to provide the input.
            target (string): The target software to export to.
        """
        self._loader = loader
        self._target = target
        self._output_basedir = output_basedir
        # Initialize the IR Container
        self._ir_container = IRContainer()

    def parse_model(self):
        """
        Constructs the in-memory model. Does the following:
          - Reads the model into the flat container.
          - Creates the in-memory graphs that represent the input model.
        """
        # Read the model into the flat container
        rows_container = RowsContainer()
        self._loader.load(rows_container)  # Obtain rows from the loader
        # Create IR structures
        self._ir_container.load_from_rows(rows_container)
        del rows_container

    def export_png(self):
        """Exports the in-memory graphs to PNG image files"""
        self._ir_container.export_graphs(self._output_basedir)

    def translate(self):
        # Get the exporter object
        exporter = ExporterFactory.get_exporter(self)
        # Export the model
        exporter.export()

    @property
    def target(self):
        return self._target

    @property
    def output_basedir(self):
        return self._output_basedir

    @property
    def ir_container(self):
        return self._ir_container


class ExporterFactory(object):
    @staticmethod
    def get_exporter(caller):
        if caller.target.lower() == 'isograph':
            return IsographExporter(caller)
        else:
            raise ExporterError('Unknown target: {}'.format(caller.target))
