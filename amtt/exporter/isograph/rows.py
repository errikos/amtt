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

    schema = [
        'Id',    # Block ID (must be unique)
        'Page',  # Εnclosing block, a.k.a. page (-> RbdBlocks.Id)
        'StandbyMode',   # Block standby mode
        'FailureModel',  # Assigned failure model
        'XPosition',    # Block X coordinate in the diagram
        'YPosition',    # Block Y coordinate in the diagram
        'Description',  # Block description
    ]

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

    schema = [
        'Id',    # Repeat block ID (must be unique)
        'Page',  # Εnclosing block, a.k.a. page (-> RbdBlocks.Id)
        'ReferenceBlock',  # The mirrored block (-> RbdBlocks.Id)
        'XPosition',  # Repeat block X coordinate in the diagram
        'YPosition',  # Repeat block Y coordinate in the diagram
    ]

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

    schema = [
        'Id',    # Node ID (must be unique)
        'Page',  # Εnclosing block, a.k.a. page (-> RbdBlocks.Id)
        'Vote',  # Node voting number
        'XPosition',  # Node X coordinate in the diagram
        'YPosition',  # Node Y coordinate in the diagram
    ]

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
        'Id',    # Connection ID (must be unique).
        'Page',  # Εnclosing block, a.k.a. page (-> RbdBlocks.Id)
        'Type',  # Type of connection (horizontal/vertical)
        'InputObjectIndex',   # Index of input object
        'InputObjectType',    # Type of input object (node,block,rpt block)
        'OutputObjectIndex',  # Index of output object
        'OutputObjectType',   # Type of output object (node,block,rpt block)
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


class FailureModelRow(object):
    """Class modelling a FailureModel entry."""

    schema = [
        'Id',  # Failure model ID
        'FmDistribution',  # Failure model distribution
        'FmMttf',  # Failure model MTTF - exponential dist. only
        'FmBeta1',  # Failure model Beta1 - Weibull family dist. only
        'FmBeta2',  # Failure model Beta2 - Bi-Weibull family dist. only
        'FmBeta3',  # Failure model Beta3 - Tri-Weibull family dist. only
        'FmEta1',  # Failure model Eta1 - Weibull family dist. only
        'FmEta2',  # Failure model Eta2 - Bi-Weibull family dist. only
        'FmEta3',  # Failure model Eta3 - Tri-Weibull family dist. only
        'FmGamma1',  # Failure model Gamma1 - Weibull family dist. only
        'FmGamma2',  # Failure model Gamma2 - Weibull family dist. only
        'FmGamma3',  # Failure model Gamma3 - Weibull family dist. only
    ]

    def __init__(self, **kwargs):
        """Initialize FailureModelRow."""
        for key in FailureModelRow.schema:
            setattr(self, key, kwargs.get(key))


###############################################################################

SCHEMA = OrderedDict([
    ('RbdBlocks', RbdBlockRow.schema),
    ('RbdRepeatBlocks', RbdRepeatBlockRow.schema),
    ('RbdNodes', RbdNodeRow.schema),
    ('RbdConnections', RbdConnectionRow.schema),
    ('FailureModels', FailureModelRow.schema),
])

__all__ = [
    'RbdBlockRow',
    'RbdRepeatBlockRow',
    'RbdNodeRow',
    'RbdConnectionRow',
    'FailureModelRow',
]
