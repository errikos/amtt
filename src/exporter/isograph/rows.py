"""
Contains the Isograph flat elements, to be written to the output excel file.
"""

import logging

_logger = logging.getLogger(__name__)

# Reliability Block Diagram rows ##############################################


class RbdBlockRow(object):

    schema = ['Id', 'Page', 'XPosition', 'YPosition']

    def __init__(self, **kwargs):
        for key in RbdBlockRow.schema:
            setattr(self, key, kwargs.get(key))

    @staticmethod
    def header():
        return RbdBlockRow(**{k: k for k in RbdBlockRow.schema})


class RbdRepeatBlockRow(object):

    schema = ['Id', 'Page', 'XPosition', 'YPosition']

    def __init__(self, **kwargs):
        for key in RbdRepeatBlockRow.schema:
            setattr(self, key, kwargs.get(key))

    @staticmethod
    def header():
        return RbdRepeatBlockRow(**{k: k for k in RbdRepeatBlockRow.schema})


class RbdNodeRow(object):

    schema = ['Id', 'Page', 'Vote', 'XPosition', 'YPosition']

    def __init__(self, **kwargs):
        for key in RbdNodeRow.schema:
            setattr(self, key, kwargs.get(key))

    @staticmethod
    def header():
        return RbdNodeRow(**{k: k for k in RbdNodeRow.schema})


class RbdConnectionRow(object):

    schema = [
        'Id', 'Page', 'Type', 'InputObjectIndex', 'InputObjectType',
        'OutputObjectIndex', 'OutputObjectType'
    ]

    def __init__(self, **kwargs):
        for key in RbdConnectionRow.schema:
            setattr(self, key, kwargs.get(key))

    @staticmethod
    def header():
        return RbdConnectionRow(**{k: k for k in RbdConnectionRow.schema})


###############################################################################
