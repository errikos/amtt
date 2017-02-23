"""
Contains the translator flat elements, as read from the input source.
"""

import logging
from exporter.isograph.rbd import Logic

_logger = logging.getLogger(__name__)


class FlatComponent(object):
    """
    Class modelling a system Component, as read from the input (flat).
    """

    def __init__(self, **kwargs):
        for arg in ('type', 'name', 'parent', 'code', 'instances'):
            setattr(self, arg, kwargs[arg])


class FlatLogic(object):
    """
    Class modelling a Logic entry, as read from the input (flat).
    """

    def __init__(self, **kwargs):
        for arg in ('type', 'component', 'logic'):
            setattr(self, arg, kwargs[arg])


class FlatContainer(object):
    """
    Container for objects as read from the input.
    """

    def __init__(self):
        self._components = []
        self._logic = []
        self._properties = []

    def add_component(self, **kwargs):
        self._components.append(FlatComponent(**kwargs))

    def add_logic(self, **kwargs):
        self._logic.append(FlatLogic(**kwargs))

    @property
    def component_list(self):
        return self._components

    @property
    def logic_list(self):
        return self._logic
