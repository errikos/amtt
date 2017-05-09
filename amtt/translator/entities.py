"""Python module containing the translator core entities."""

import logging
import re

_logger = logging.getLogger(__name__)


class SystemElement(object):
    """Class modelling a system element."""

    def __init__(self, type, name, parent, code, instances, description=None):
        """Initialize SystemElement."""
        self._type = type
        self._name = name
        self._code = code
        self._instances = instances
        self._parent = parent
        self._description = description
        self._logic = None  # Only applicable to compound elements.
        self._failure_model = None  # Only applicable to basic elements.

    def __str__(self):
        """Return the string representation of the object."""
        return '{}_{}'.format(self.type, self.name)

    def is_type(self, type_str):
        """Return True if self has the type indicated by type_str."""
        return self.type.lower() == type_str.lower()

    @property
    def id(self):
        """str: unique ID for the system element."""
        return '{}_{}'.format(self.type, self.name)

    @property
    def type(self):
        """str: the component type of the system element."""
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def name(self):
        """str: the name of the system element."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def code(self):
        """str: the system element code."""
        return self._code

    @property
    def instances(self):
        """int: the number of instances for the system element."""
        return self._instances

    @property
    def logic(self):
        """ElementLogic: the associated element logic class."""
        return self._logic

    @logic.setter
    def logic(self, logic):
        self._logic = logic

    @property
    def parent(self):
        """parent: the system element parent."""
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def description(self):
        """str: the system element description."""
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def failure_model(self):
        """str: the assigned failure model or None if not a basic element."""
        return self._failure_model

    @failure_model.setter
    def failure_model(self, failure_model):
        self._failure_model = failure_model


class ElementLogic(object):
    """Class modelling an element logic."""

    def __init__(self, raw_string):
        """Initialize ElementLogic."""
        tokens = re.split(r'[(,)]', raw_string)  # Parse raw string
        self._name = tokens[0]
        self._voting = tokens[1] if len(tokens) > 1 else None
        self._total = tokens[2] if len(tokens) > 2 else None

    def __eq__(self, logic_str):
        """Overload for comparing with a string."""
        return self.name.lower() == logic_str.lower()

    def __str__(self):
        """Return the string representation of the object."""
        s = 'Logic: ' + self._name
        if self._name == 'ACTIVE':
            s += ', {} out of {}'.format(self._voting, self._total)
        return s

    @property
    def name(self):
        """str: the logic name, more like ID, e.g. AND, OR, etc."""
        return self._name

    @property
    def voting(self):
        """int: the voting number (--> X out of Y)."""
        return self._voting

    @property
    def total(self):
        """int: the total to vote against (X out of Y <--)."""
        return self._total
