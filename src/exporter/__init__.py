"""
The exporter module.

This module consists of all exporters available to the back-end.
The currently available exporters are:
    - IsographExporter
        Exports the model to Isograph importable format.
"""

import translator


class ExporterError(translator.TranslatorError):
    """
    Base class for Exporter Exceptions.
    Derive from this class when defining exceptions for your Exporter classes.
    """


class Exporter(object):
    """
    The Exporter base class. Every exporter must be a subclass of this class.

    A valid Exporter must implement the following methods:
        pass

    If an Exporter fails to implement any of the above methods, then an
    AttributeError is raised at runtime, upon method invocation.
    """


class ExporterFactory(object):

    @staticmethod
    def get_exporter(caller):
        if caller.target.lower() == 'isograph':
            from .isograph import IsographExporter
            return IsographExporter(caller)
        else:
            raise ExporterError('Unknown target: {}'.format(caller.target))


__all__ = ['isograph']
