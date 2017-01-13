"""
csv Loader module
"""

import os
import logging
import csv
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
        # csv file names are listed here...
        file_names = [
            'components.csv',
            'logic.csv',
        ]
        # ... and the flat handler methods here.
        method_names = [
            'add_component',
            'add_logic',
        ]
        # Attention: file_names and method_names above are expected to have
        #            a 1-1 correspondence
        for file_name, method_name in zip(file_names, method_names):
            with open(os.path.join(self.dir_in, file_name)) as f:
                reader = csv.DictReader(f)
                # convert csv field (column) names to lowercase
                reader.fieldnames = [
                    field.lower() for field in reader.fieldnames
                ]
                # add the flat components to the translator structures
                [
                    getattr(translator.flats, method_name)(**row)
                    for row in reader
                ]

