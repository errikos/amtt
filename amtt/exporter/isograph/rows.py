"""Contains the Isograph flat elements.

The contents of the module model the "serialized" elements that are to be
written to the ouput files for Isograph. They define and impose the schema
of the output.
"""

import logging
from collections import OrderedDict

_logger = logging.getLogger(__name__)

# Reliability Block Diagram rows ##############################################


class RbdBlockRow(object):
    """Class modelling an RBD block entry."""

    schema = ['Id', 'Page', 'XPosition', 'YPosition', 'Description']

    def __init__(self, **kwargs):
        """Initialize RbdBlockRow."""
        for key in RbdBlockRow.schema:
            setattr(self, key, kwargs.get(key))

    @staticmethod
    def header():
        """Return a header entry for RbdBlockRow.

        Used for outputs: Excel
        Not used for outputs: XML
        """
        return RbdBlockRow(**{k: k for k in RbdBlockRow.schema})


class RbdRepeatBlockRow(object):
    """Class modelling a mirrored RBD block entry."""

    schema = ['Id', 'Page', 'ReferenceBlock', 'XPosition', 'YPosition']

    def __init__(self, **kwargs):
        """Initialize RbdRepeatBlockRow."""
        for key in RbdRepeatBlockRow.schema:
            setattr(self, key, kwargs.get(key))

    @staticmethod
    def header():
        """Return a header entry for RbdRepeatBlockRow.

        Used for outputs: Excel
        Not used for outputs: XML
        """
        return RbdRepeatBlockRow(**{k: k for k in RbdRepeatBlockRow.schema})


class RbdNodeRow(object):
    """Class modelling an RBD node entry."""

    schema = ['Id', 'Page', 'Vote', 'XPosition', 'YPosition']

    def __init__(self, **kwargs):
        """Initialize RbdNodeRow."""
        for key in RbdNodeRow.schema:
            setattr(self, key, kwargs.get(key))

    @staticmethod
    def header():
        """Return a header entry for RbdRepeatBlockRow.

        Used for outputs: Excel
        Not used for outputs: XML
        """
        return RbdNodeRow(**{k: k for k in RbdNodeRow.schema})


class RbdConnectionRow(object):
    """Class modelling an RBD connection entry."""

    schema = [
        'Id', 'Page', 'Type', 'InputObjectIndex', 'InputObjectType',
        'OutputObjectIndex', 'OutputObjectType'
    ]

    def __init__(self, **kwargs):
        """Initialize RbdConnectionRow."""
        for key in RbdConnectionRow.schema:
            setattr(self, key, kwargs.get(key))

    @staticmethod
    def header():
        """Return a header entry for RbdRepeatBlockRow.

        Used for outputs: Excel
        Not used for outputs: XML
        """
        return RbdConnectionRow(**{k: k for k in RbdConnectionRow.schema})


###############################################################################

SCHEMA = OrderedDict([
    ('RbdBlocks', RbdBlockRow.schema),
    ('RbdRepeatBlocks', RbdRepeatBlockRow.schema),
    ('RbdNodes', RbdNodeRow.schema),
    ('RbdConnections', RbdConnectionRow.schema),
])

__all__ = [
    'RbdBlockRow', 'RbdRepeatBlockRow', 'RbdNodeRow', 'RbdConnectionRow'
]
