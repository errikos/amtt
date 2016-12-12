"""
csv Loader module
"""

import logging
from . import Loader

_logger = logging.getLogger('loader.csv')


def handler(args):
    return CsvLoader(args.dir_in)


class CsvLoader(Loader):
    """
    Loader to load the model from CSV files.
    """

    def __init__(self, dir_in):
        self.dir_in = dir_in

    def load(self, translator):
        # TODO: Implement
        pass
