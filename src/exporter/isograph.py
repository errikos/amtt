"""
isograph Exporter module
"""

import logging
from . import Exporter

_logger = logging.getLogger('exporter.isograph')


class IsographExporter(Exporter):
    """
    Exporter to export the model to Isograph.
    """

    def __init__(self):
        pass

    def export(self, translator):
        print('Exporting for Isograph...')
