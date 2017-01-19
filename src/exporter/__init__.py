"""
The exporter module.

This module consists of all exporters available to the back-end.
The currently available exporters are:
    - IsographExporter
        Exports the model to Isograph importable format.
"""


class Exporter(object):
    """
    The Exporter base class. Every exporter must be a subclass of this class.

    A valid Exporter must implement the following methods:
        pass

    If an Exporter fails to implement any of the above methods, then an
    AttributeError is raised at runtime, upon method invocation.
    """


__all__ = ['isograph']
