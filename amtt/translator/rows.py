"""
Contains the translator flat elements, as read from the input source.

Each row is modelled as a class, in order to allow easier manipulation,
if such functionality is required later on.

For the time being, row modelling classes act only as value containers.
"""
import logging
from amtt.loader import InputSheet, SCHEMAS

_logger = logging.getLogger(__name__)


class ComponentRow(object):
    """
    Class modelling a system Component, as read from the input (flat).
    """

    def __init__(self, **kwargs):
        for arg in SCHEMAS[InputSheet.components]:
            setattr(self, arg, kwargs[arg])


class LogicRow(object):
    """
    Class modelling a Logic entry, as read from the input (flat).
    """

    def __init__(self, **kwargs):
        for arg in SCHEMAS[InputSheet.logic]:
            setattr(self, arg, kwargs[arg])


class RowsContainer(object):
    """
    Container for objects as read from the input.
    """

    def __init__(self):
        self._components = []
        self._logic = []

    def add_row(self, sheet_type, **kwargs):
        """
        Adds a new row of type sheet_type to the container.
        Delegates insertion to one of the methods below.
        """
        {   # Python-like switch :)
            InputSheet.components: self._add_component,
            InputSheet.logic: self._add_logic,
        }[sheet_type](**kwargs)

    def _add_component(self, **kwargs):
        """Adds a new component row."""
        self._components.append(ComponentRow(**kwargs))

    def _add_logic(self, **kwargs):
        """Adds a new logic row."""
        self._logic.append(LogicRow(**kwargs))

    @property
    def contains_templates(self):
        """Returns True if the container contains template components."""
        try:
            # At least one template component
            next(filter(lambda x: x.parent == '*', self.component_list))
            return True
        except StopIteration:
            # Not a single template component
            return False

    @property
    def component_list(self):
        return self._components

    @property
    def logic_list(self):
        return self._logic
