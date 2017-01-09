"""
xls (Microsoft Office 2003) Loader module
"""

import os
import logging
import pyexcel_xls as xls

from . import Loader, LoaderError

_logger = logging.getLogger('loader.xls')


def handler(args):
    filename = args.xls_in
    name, ext = os.path.splitext(filename)
    if ext != '.xls':
        raise LoaderError("XlsLoader input must be an XLS file path")
    return XlsLoader(args.xls_in)


class XlsLoader(Loader):
    """
    Loader to load the model from XLS files.
    """

    def __init__(self, file_path):
        self._file_path = file_path

    def load(self, translator):
        xls_doc = xls.get_data(self._file_path)
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
