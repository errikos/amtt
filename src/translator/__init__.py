"""
The translator module.
"""

from .elements import Model
from .flat import FlatComponent, FlatLogic, FlatProperty


class TranslatorError(Exception):
    """
    Base class for Translator Exceptions.
    """


class _FlatContainer(object):
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


class Translator(object):
    """
    The translator class.
    """

    def __init__(self, loader, target):
        """
        The Translator constructor.

        Args:
            loader (Loader): A loader instance, used to provide the input.
            target (string): The target software to export to.
        """
        self._loader = loader
        self._target = target
        self._flat_container = _FlatContainer()

    def translate(self):
        self._loader.load(self)
        # Get the exporter object
        from exporter import ExporterFactory
        exporter = ExporterFactory.get_exporter(self._target)
        # Export the model
        exporter.export(self)

    @property
    def flats(self):
        """
        Property giving access to the flat objects container.
        """
        return self._flat_container
