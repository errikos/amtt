"""The translator module."""

import logging

from amtt.errors import ExporterError

from amtt.exporter.isograph import IsographExporter
from .ir import IRContainer
from .rows import RowsContainer

_logger = logging.getLogger(__name__)


class Translator(object):
    """The translator class."""

    def __init__(self, loader, target, output_basedir):
        """Initialize the translator.

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
        """Construct the in-memory model.

        Does the following:
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
        """Export the in-memory graphs to PNG image files."""
        self._ir_container.export_graphs(self._output_basedir)

    def translate(self):
        """Carry out the translation process."""
        # Get the exporter object
        exporter = ExporterFactory.get_exporter(self)
        # Export the model
        exporter.export()

    @property
    def target(self):
        """str: the target back-end."""
        return self._target

    @property
    def output_basedir(self):
        """str: the output directory."""
        return self._output_basedir

    @property
    def ir_container(self):
        """IRContainer: the IR container object of the translator."""
        return self._ir_container


class ExporterFactory(object):
    """Factory for back-end exporters."""

    @staticmethod
    def get_exporter(caller):
        """Construct and return the appropriate exporter."""
        if caller.target.lower() == 'isograph':
            return IsographExporter(caller)
        else:
            raise ExporterError('Unknown target: {}'.format(caller.target))
