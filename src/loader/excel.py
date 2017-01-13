"""
xls (Microsoft Office 2003) Loader module
"""

import os
import logging
import pyexcel

from . import Loader, LoaderError

_logger = logging.getLogger('loader.excel')


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

    def load(self, translator):
        # Sheet names are listed here...
        sheet_names = [
            'Components',
            'Logic',
        ]
        # ... and the flat handler methods here.
        method_names = [
            'add_component',
            'add_logic',
        ]
        # Attention: sheet_names and method_names above are expected to have
        #            a 1-1 correspondence
        sheets = [
            pyexcel.get_sheet(
                file_name=self._file_path,
                sheet_name=sheet_name,
                name_columns_by_row=0) for sheet_name in sheet_names
        ]
        [[
            getattr(translator.flats, method)(
                **{key.lower(): val
                   for key, val in zip(sheet.colnames, row)})
            for row in sheet.rows()
        ] for sheet, method in zip(sheets, method_names)]
