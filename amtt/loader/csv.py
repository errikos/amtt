"""Loader module for loading from CSV files."""

import os
import logging
import csv
from . import Loader

_logger = logging.getLogger(__name__)


def handler(args):
    """Handle csv option in argparse."""
    return CsvLoader(args.dir_in)


class CsvLoader(Loader):
    """Loader to load the model from CSV files."""

    def __init__(self, dir_in):
        """Initialize CsvLoader."""
        self.dir_in = dir_in

    def load(self, container):
        """Load the rows from the CSV files into the container."""
        # For each sheet is sheet definitions (here: file)
        for sheet_type, sheet_name in self.sheet_definitions_iter():
            filename = sheet_name + '.csv'
            with open(os.path.join(self.dir_in, filename)) as f:
                reader = csv.DictReader(f)
                # convert csv field (column) names to lowercase
                reader.fieldnames = [
                    field.lower().replace(' ', '_')
                    for field in reader.fieldnames
                ]
                [container.add_row(sheet_type, **row) for row in reader if row]
