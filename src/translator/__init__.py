"""
The translator module.
"""

from .elements import Model
from .flat import FlatComponent, FlatLogic


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

    def add_component(self, type, name, parent, quantity, comment):
        self._components.append(FlatComponent(type, name, parent, quantity))

    def add_logic(self, component, logic, comment):
        self._logic.append(FlatLogic(component, logic))


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
