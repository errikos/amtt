"""
Contains the translator flat elements, as read from the input source.
"""

import logging
from exporter.isograph.rbd import Logic

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

    def __init__(self, type, component, logic):
        self._type = type
        self._component = component
        self._logic = Logic[logic]

    @property
    def type(self):
        return self._type

    @property
    def component(self):
        return self._component

    @property
    def logic(self):
        return self._logic


class FlatProperty(object):
    """
    Class modelling a Property entry, as read from the input (flat).
    """

    def __init__(self, component, property_id, type, value, unit):
        self._component = component
        self._property_id = property_id
        self._type = type
        self._value = value
        self._unit = unit

    @property
    def component(self):
        return self._component

    @property
    def property_id(self):
        return self._property_id

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value

    @property
    def unit(self):
        return self.unit


class FlatContainer(object):
    """
    Container for objects as read from the input.
    """

    def __init__(self):
        self._components = []
        self._logic = []
        self._properties = []

    def add_component(self, type, name, parent, quantity, comment):
        self._components.append(FlatComponent(type, name, parent, quantity))

    def add_logic(self, type, component, logic, comment):
        self._logic.append(FlatLogic(type, component, logic))

    def add_property(self, component, propertyid, type, value, unit, comment):
        self._properties.append(
            FlatProperty(component, propertyid, type, value, unit))

    @property
    def component_list(self):
        return self._components

    @property
    def logic_list(self):
        return self._logic

    @property
    def property_list(self):
        return self._properties
