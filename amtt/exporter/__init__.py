"""
The exporter module.

This module consists of all exporters available to the back-end.
The currently available exporters are:
    - IsographExporter
        Exports the model to Isograph importable format.
"""

from datetime import datetime as dt


class Exporter(object):
    """The Exporter base class. Every exporter must derive from this class.

    A valid Exporter must implement the following methods:
        pass

    If an Exporter fails to implement any of the above methods, then an
    AttributeError is raised at runtime, upon method invocation.

    """

    timestamp = dt.now().strftime('%Y%m%d_%H%M%S_%f')


__all__ = ['isograph']
