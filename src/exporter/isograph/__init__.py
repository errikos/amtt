"""

"""

import logging
from exporter import Exporter

_logger = logging.getLogger('exporter.isograph')


class IsographExporter(Exporter):
    """
    Exporter to export the model to Isograph.
    """

    def __init__(self, translator):
        self._translator = translator

    def export(self):
        for component in self._translator.flats._components:
            print(component.name)
