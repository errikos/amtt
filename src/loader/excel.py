"""
xls (Microsoft Office 2003) Loader module
"""

import os
import logging
import pyexcel_xls as xls
import pyexcel_xlsx as xlsx

from . import Loader, LoaderError

_logger = logging.getLogger('loader.excel')


def handler(args):
    filename = args.excel_in
    name, ext = os.path.splitext(filename)
    if ext.lower() == '.xls':
        module = xls
    elif ext.lower() == '.xlsx':
        module = xlsx
    else:
        raise LoaderError("XlsLoader input must be an XLS or XLSX file path")
    return ExcelLoader(args.excel_in, module)


class ExcelLoader(Loader):
    """
    Loader to load the model from XLS/XLSX files.
    """

    def __init__(self, file_path, module):
        self._file_path = file_path
        self._module = module

    def load(self, translator):
        xls_doc = self._module.get_data(self._file_path)
        # Load system components
        components = iter(xls_doc['Components'])
        next(components)  # skip header
        [translator.add_component(comp) for comp in components]
        # Load system logic
        logic = iter(xls_doc['Logic'])
        next(logic)  # skip header
        [translator.add_logic(logic) for logic in logic]
        # Load system properties
        properties = iter(xls_doc['Properties'])
        next(properties)
        [translator.add_property(prop) for prop in properties]
