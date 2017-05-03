"""
Exporter module for Isograph Availability Workbench.
"""
import logging

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

    def export(self):
        # Create block diagram from input
        rbd = Rbd()
        rbd.from_ir_container(self._translator.ir_container)
        # Dump block diagram to output
        rbd.serialize(self._emitter)
