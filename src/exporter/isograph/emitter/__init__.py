"""
Emitter module for Isograph.
"""

import logging
from itertools import chain
from collections import OrderedDict

_logger = logging.getLogger(__name__)

SCHEMA = OrderedDict([
    ('RbdBlocks', ['Id', 'Page', 'XPosition', 'YPosition']),
    ('RbdRepeatBlocks', ['Id', 'Page', 'XPosition', 'YPosition']),
    ('RbdNodes', ['Id', 'Page', 'Vote', 'XPosition', 'YPosition']),
    ('RbdConnections', [
        'Id', 'Page', 'Type', 'InputObjectIndex', 'InputObjectType',
        'OutputObjectIndex', 'OutputObjectType'
    ]),
])


class RbdBlock(object):
    def __init__(self, **kwargs):
        for key in SCHEMA['RbdBlocks']:
            setattr(self, key, kwargs.get(key))

    def __str__(self):
        return ','.join(
            (len(SCHEMA['RbdBlocks']) *
             ['{}:{}'])).format(*chain.from_iterable(vars(self).items()))

    @staticmethod
    def header():
        return RbdBlock(**{k: k for k in SCHEMA['RbdBlocks']})


class RbdNode(object):
    def __init__(self, **kwargs):
        for key in SCHEMA['RbdNodes']:
            setattr(self, key, kwargs.get(key))

    def __str__(self):
        return ','.join(
            (len(SCHEMA['RbdNodes']) *
             ['{}:{}'])).format(*chain.from_iterable(vars(self).items()))

    @staticmethod
    def header():
        return RbdNode(**{k: k for k in SCHEMA['RbdNodes']})


class RbdConnection(object):
    def __init__(self, **kwargs):
        for key in SCHEMA['RbdConnections']:
            setattr(self, key, kwargs.get(key))

    def __str__(self):
        return ','.join(
            (len(SCHEMA['RbdConnections']) *
             ['{}:{}'])).format(*chain.from_iterable(vars(self).items()))

    @staticmethod
    def header():
        return RbdConnection(**{k: k for k in SCHEMA['RbdConnections']})


class IsographEmitter(object):
    """
    Base class for Isograph emitter objects.
    """
