"""
Contains the translator core elements.
"""

import logging

_logger = logging.getLogger('translator.elements')


class Structure(object):
    """

    """

    def __init__(self):
        pass


class Model(object):
    """

    """

    def __init__(self):
        self._structure = Structure()

    @property
    def structure(self):
        return self._structure
