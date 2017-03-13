"""
Microsoft Office Excel files emitter for Isograph.
"""

import logging
import os
from datetime import datetime as dt

import pyexcel_xls as xls

_logger = logging.getLogger(__name__)


class ExcelEmitter(object):
    """
    Microsoft Office Excel emitter for Isograph.
    """

    def __init__(self, output_dir):
        nobasedir = output_dir is None
        basedir = output_dir if not nobasedir else ''
        output_path = 'model_{}.xls'.format(
            dt.now().strftime('%Y%m%d_%H%M%S_%f'))
        self._output_path = os.path.join(basedir, output_path)
        _logger.info('Output path is: ' + os.path.abspath(self.output_path))

    @property
    def output_path(self):
        return self._output_path

    def add_element(self):
        # TODO
        pass
