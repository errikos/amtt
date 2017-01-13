"""
Contains the translator flat elements, as read from the input source.
"""

import logging

_logger = logging.getLogger('translator.flat')


class FlatComponent(object):
    """
    Class modelling a system Component, as read from the input (flat).
    """

    def __init__(self, type, name, parent, quantity):
        self._type = type
        self._name = name
        self._parent = parent
        self._quantity = quantity

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def quantity(self):
        return self._quantity


class FlatLogic(object):
    """
    Class modelling a Logic entry, as read from the input (flat).
    """

    def __init__(self, component, logic):
        self._component = component
        self._logic = logic

    @property
    def component(self):
        return self._component

    @property
    def logic(self):
        return self._logic
