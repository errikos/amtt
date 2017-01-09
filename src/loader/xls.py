"""
xls (Microsoft Office 2003) Loader module
"""

import logging
import pyexcel_xls as xls

from . import Loader

_logger = logging.getLogger('loader.xls')


def handler(args):
    return XlsLoader(args.dir_in)


class XlsLoader(Loader):
    """
    Loader to load the model from XLS files.
    """

    def __init__(self, file_path):
        self._file_path = file_path

    def load(self, translator):
        # TODO: Implement
        pass
