"""Module containing the Exception definitions."""


class TranslatorError(Exception):
    """Base class for Translator Exceptions."""


class LoaderError(TranslatorError):
    """Base class for Loader Exceptions.

    Derive from this class when defining exceptions for your Loader classes.
    """


class ExporterError(TranslatorError):
    """Base class for Exporter Exceptions.

    Derive from this class when defining exceptions for your Exporter classes.
    """
