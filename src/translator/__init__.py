"""
The translator module.
"""


class TranslatorError(Exception):
    """
    Base class for Translator Exceptions.
    """


class Translator(object):
    """

    """

    def __init__(self, loader, target):
        """
        The Translator constructor.

        Args:
            loader (Loader): A loader-old instance, used to provide the input.
            target (string): The target software to export to.
        """
        self._loader = loader
        self._target = target
