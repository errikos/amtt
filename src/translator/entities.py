"""
Python module containing the translator core entities.
"""

import logging
import re

_logger = logging.getLogger(__name__)


class SystemElement(object):
    """
    Class modelling a system element.
    """

    def __init__(self, type, name, code, instances):
        self._type = type
        self._name = name
        self._code = code
        self._instances = instances
        self._logic = None
        self._parent = None

    def __str__(self):
        return '{}: {}'.format(self.type, self.name)

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def code(self):
        return self._code

    @property
    def instances(self):
        return self._instances

    @property
    def logic(self):
        return self._logic

    @logic.setter
    def logic(self, logic):
        self._logic = logic

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent


class ElementLogic(object):
    """
    Class modelling an element logic.
    """

    def __init__(self, raw_string):
        # Parse raw string
        tokens = re.split(r'[(,)]', raw_string)
        self._name = tokens[0]
        self._voting = tokens[1] if len(tokens) > 1 else None
        self._total = tokens[2] if len(tokens) > 2 else None

    def __eq__(self, other):
        """Overload for comparing two Logic objects"""
        return self.name == other.name \
            and self.voting == other.voting \
            and self.total == other.total

    def __str__(self):
        s = 'Logic: ' + self._name
        if self._name == 'ACTIVE':
            s += ', {} out of {}'.format(self._voting, self._total)
        return s

    @property
    def name(self):
        return self._name

    @property
    def voting(self):
        return self._voting

    @property
    def total(self):
        return self._total
