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
        # Load system components
        components_path = os.path.join(self.dir_in, 'components.csv')
        with open(components_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                row[3] = int(row[3])  # convert quantity to int
                translator.add_component(row)
        # Load system logic
        logic_path = os.path.join(self.dir_in, 'logic.csv')
        with open(logic_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                translator.add_logic(row)
        # Load system properties
        properties_path = os.path.join(self.dir_in, 'properties.csv')
        with open(properties_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                translator.add_property(row)
