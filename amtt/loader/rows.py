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


class FailureModelRow(object):
    """Class modelling a FailureModel entry, as read from the input (flat)."""

    def __init__(self, **kwargs):
        """Initialize FailureModelRow."""
        for arg in SCHEMAS[InputSheet.failure_models]:
            setattr(self, arg, kwargs[arg])


class ComponentFailureRow(object):
    """Class modelling a ComponentFailure entry, as read from the input."""

    def __init__(self, **kwargs):
        """Initialize ComponentFailureRow."""
        for arg in SCHEMAS[InputSheet.component_failures]:
            setattr(self, arg, kwargs[arg])


class ManpowerRow(object):
    """Class modelling a Manpower entry, as read from the input."""

    def __init__(self, **kwargs):
        """Initialize ManpowerRow."""
        for arg in SCHEMAS[InputSheet.manpower]:
            setattr(self, arg, kwargs[arg])


class SpareRow(object):
    """Class modelling a Spare entry, as read from the input."""

    def __init__(self, **kwargs):
        """Initialize SpareRow."""
        for arg in SCHEMAS[InputSheet.spares]:
            setattr(self, arg, kwargs[arg])


class RowsContainer(object):
    """Container for objects as read from the input."""

    def __init__(self):
        """Initialize RowsContainer."""
        self._components = []
        self._logic = []
        self._failure_models = []
        self._component_failures = []
        self._manpowers = []
        self._spares = []

    def add_row(self, sheet_type, **kwargs):
        """Add a new row of type sheet_type to the container.

        Delegate insertion to one of the methods below.
        """
        {   # Python-like switch :)
            InputSheet.components: self._add_component,
            InputSheet.logic: self._add_logic,
            InputSheet.failure_models: self._add_failure_model,
            InputSheet.component_failures: self._add_component_failure,
            InputSheet.manpower: self._add_manpower,
            InputSheet.spares: self._add_spare,
        }[sheet_type](**kwargs)

    def _add_component(self, **kwargs):
        """Add a new component row."""
        self._components.append(ComponentRow(**kwargs))

    def _add_logic(self, **kwargs):
        """Add a new logic row."""
        self._logic.append(LogicRow(**kwargs))

    def _add_failure_model(self, **kwargs):
        """Add a new failure model row."""
        self._failure_models.append(FailureModelRow(**kwargs))

    def _add_component_failure(self, **kwargs):
        """Add a new component failure row."""
        self._component_failures.append(ComponentFailureRow(**kwargs))

    def _add_manpower(self, **kwargs):
        """Add a new manpower row."""
        self._manpowers.append(ManpowerRow(**kwargs))

    def _add_spare(self, **kwargs):
        """Add a new spares row."""
        self._spares.append(SpareRow(**kwargs))

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

    @property
    def failure_models_list(self):
        """list: the failure models list."""
        return self._failure_models

    @property
    def component_failures_list(self):
        """list: the component failures list."""
        return self._component_failures

    @property
    def manpower_list(self):
        """list: the manpower list."""
        return self._manpowers

    @property
    def spares_list(self):
        """list: the spares list."""
        return self._spares
