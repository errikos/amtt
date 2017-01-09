"""
The loader module.

This module consists of all loaders available to the front-end.
The currently available loaders are:
    - CsvLoader
        Loads the model from CSV files.

In order to define new loaders, the following steps are required:
    1. Create your loader class by subclassing the Loader class,
       as described below.
    2. If required, add a subparser in the parse_arguments function found in
       main.py, so that you can support loader invocation from the command line.
       Check the argparse module for details:
       https://docs.python.org/3/library/argparse.html
    3. If (2) was required, then also create a handler function for the command
       line options of your loader. This function shall accept the parsed
       arguments object as its only parameter and return an instance of your
       loader, based on the former. Assign your handler to your sub-parser
       by invoking the set_defaults method on your sub-parser (see current code
       as reference).
"""

import translator


class LoaderError(translator.TranslatorError):
    """
    Base class for Loader Exceptions.
    Derive from this class when defining exceptions for your Loader classes.
    """


class Loader(object):
    """
    The Loader base class. Every loader must be a subclass of this class.

    A valid Loader must implement the following methods:
        - load(translator: Translator) -> None
            Given a Translator object, this method loads the data model by
            making use of the Translator class methods (check documentation).

    If a Loader fails to implement any of the above methods, then an
    AttributeError is raised at runtime, upon method invocation.

    In most cases, a Loader may be just a simple importer of data, as during
    the translation process model validation gets carried out, so any missed
    errors will be reported at that time.

    However, it is crucial that the Loader carries out data validation before
    instantiating objects or putting data in the Keep.
    """


# Contains all available loaders.
__all__ = ['csv', 'excel']
