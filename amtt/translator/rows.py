"""Contains the translator flat elements, as read from the input source.

Each row is modelled as a class, in order to allow easier manipulation,
if such functionality is required later on.

For the time being, row modelling classes act only as value containers.
"""
import logging
from amtt.loader import InputSheet, SCHEMAS

_logger = logging.getLogger(__name__)


class ComponentRow(object):
    """Class modelling a system Component, as read from the input (flat)."""

    def __init__(self, **kwargs):
        """Initialize ComponentRow."""
        for arg in SCHEMAS[InputSheet.components]:
            setattr(self, arg, kwargs[arg])


class LogicRow(object):
    """Class modelling a Logic entry, as read from the input (flat)."""

    def __init__(self, **kwargs):
        """Initialize LogicRow."""
        for arg in SCHEMAS[InputSheet.logic]:
            setattr(self, arg, kwargs[arg])


class RowsContainer(object):
    """Container for objects as read from the input."""

    def __init__(self):
        """Initialize RowsContainer."""
        self._components = []
        self._logic = []

    def add_row(self, sheet_type, **kwargs):
        """Add a new row of type sheet_type to the container.

        Delegate insertion to one of the methods below.
        """
        {   # Python-like switch :)
            InputSheet.components: self._add_component,
            InputSheet.logic: self._add_logic,
        }[sheet_type](**kwargs)

    def _add_component(self, **kwargs):
        """Add a new component row."""
        self._components.append(ComponentRow(**kwargs))

    def _add_logic(self, **kwargs):
        """Add a new logic row."""
        self._logic.append(LogicRow(**kwargs))

    @property
    def contains_templates(self):
        """Return True if the container contains template components."""
        try:
            # At least one template component
            next(filter(lambda x: x.parent == '*', self.component_list))
            return True
        except StopIteration:
            # Not a single template component
            return False

    @property
    def component_list(self):
        """list: the components list."""
        return self._components

    @property
    def logic_list(self):
        """list: the "logics" list."""
        return self._logic
