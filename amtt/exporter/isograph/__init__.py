"""
Exporter module for Isograph Availability Workbench.
"""
import logging

from amtt.exporter import Exporter

from amtt.exporter.isograph.excel import ExcelEmitter
from amtt.exporter.isograph.rbd import Rbd

_logger = logging.getLogger(__name__)


class IsographExporter(Exporter):
    """
    Exporter to export the model to Isograph.
    """

    def __init__(self, translator):
        self._translator = translator
        self._emitter = ExcelEmitter(translator.output_basedir)

    def export(self):
        # TODO: create block diagram from input
        rbd = Rbd()
        rbd.from_ir_container(self._translator.ir_container)
        # TODO: dump block diagram to output
        rbd.serialize(self._emitter)
