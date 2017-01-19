"""
The translator module.
"""

from .flat import FlatContainer
from exporter.isograph import IsographExporter
from errors import ExporterError


class Translator(object):
    """
    The translator class.
    """

    def __init__(self, loader, target):
        """
        The Translator constructor.

        Args:
            loader (Loader): A loader instance, used to provide the input.
            target (string): The target software to export to.
        """
        self._loader = loader
        self._target = target
        self._flat_container = FlatContainer()

    def parse_model(self):
        # Here we construct the in-memory model from the flat objects
        pass

    def translate(self):
        self._loader.load(self)
        # Get the exporter object
        exporter = ExporterFactory.get_exporter(self)
        # Export the model
        exporter.export()

    @property
    def flats(self):
        """
        Property giving access to the flat objects container.
        """
        return self._flat_container

    @property
    def target(self):
        return self._target


class ExporterFactory(object):
    @staticmethod
    def get_exporter(caller):
        if caller.target.lower() == 'isograph':
            return IsographExporter(caller)
        else:
            raise ExporterError('Unknown target: {}'.format(caller.target))
