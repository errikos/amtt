"""
xls (Microsoft Office 2003) Loader module
"""

import logging
import os

import pyexcel

from amtt.errors import LoaderError
from . import Loader

_logger = logging.getLogger(__name__)


def handler(args):
    filename = args.excel_in
    name, ext = os.path.splitext(filename)
    if ext.lower() not in ('.xls', '.xlsx'):
        raise LoaderError("XlsLoader input must be an XLS or XLSX file path")
    return ExcelLoader(args.excel_in)


class ExcelLoader(Loader):
    """
    Loader to load the model from XLS/XLSX files.
    """

    def __init__(self, file_path):
        self._file_path = file_path

    @staticmethod
    def empty(row):
        t = [c for c in row if c]
        return len(t) == 0

    def load(self, container):
        # For each sheet in sheet definitions
        for sheet_type, sheet_name in self.sheet_definitions_iter():
            # -- read sheet
            rsheet = pyexcel.get_sheet(
                file_name=self._file_path,
                sheet_name=sheet_name,
                name_columns_by_row=False)
            # -- call validation routine
            colnames = [x.lower() for x in rsheet.colnames]
            self.validate_schema(colnames, sheet_type)
            # -- read and store non-empty sheet rows
            for row in filter(lambda r: not self.empty(r), rsheet.rows()):
                # -- rowdict contains column:value pairs
                row_dict = {
                    key.lower().replace(' ', '_').strip(): Loader.strip(val)
                    for key, val in zip(rsheet.colnames, row)
                }
                # -- add rowdict to container
                container.add_row(sheet_type, **row_dict)
