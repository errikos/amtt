"""Python module containing the translator core entities."""

import logging
import re

from amtt.errors import TranslatorError

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
        if self._name.lower() in ('active', 'standby'):
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


class FailureModel(object):
    """Class modelling a failure model."""

    def __init__(self, name, distribution, parameter_spec, standby_state,
                 remarks):
        """Initialize FailureModel.

        Args:
            name: the failure model ID.
            distribution: the failure model distribution.
                Currently supported values:
                    - exponential
                    - weibull
                    - bi-weibull
                    - tri-weibull
            parameter_spec: comma separated parameter list for the specified
                distribution. Expected in the following format:
                    - exponential:
                        mttf
                    - weibull:
                        eta1,beta1,gamma1
                    - bi-weibull:
                        eta1,beta1,gamma1:eta2,beta2,gamma2
                    - tri-weibull:
                        eta1,beta1,gamma1:eta2,beta2,gamma2:eta3,beta3,gamma3
        """
        self._name = name
        self._distribution = {
            'exponential': 'Exponential',
            'weibull': 'Weibull',
            'bi-weibull': 'Bi-Weibull',
            'tri-weibull': 'Tri-Weibull',
        }[distribution.lower()]
        self._parse_parameters(parameter_spec)
        self._standby_state = standby_state
        self._remarks = remarks

    def _parse_parameters(self, parameters):

        def die():
            errmsg = ('Parameter specification for FM: {fm} does not match '
                      'expected format for {dist}')
            errmsg = errmsg.format(fm=self.name, dist=self.distribution)
            _logger.error(errmsg)
            raise TranslatorError(errmsg)

        if self.distribution.lower() == 'exponential':
            # Handle exponential parameter specification
            if not re.match(r'[0-9]+', parameters):
                die()
            self._parameters = [int(parameters)]
        elif self.distribution.lower() == 'weibull':
            # Handle weibull parameter specification
            if not re.match(r'[0-9]+,[0-9]+,[0-9]+', parameters):
                die()
            self._parameters = [parameters.split(',')]
        elif self.distribution.lower() == 'bi-weibull':
            # Handle bi-weibull parameter specification
            if not re.match(r'[0-9]+,[0-9]+,[0-9]+:'
                            r'[0-9]+,[0-9]+,[0-9]+', parameters):
                die()
            self._parameters = [x.split(',') for x in parameters.split(':')]
        elif self.distribution.lower() == 'tri-weibull':
            # Handle tri-weibull parameter specification
            if not re.match(r'[0-9]+,[0-9]+,[0-9]+:'
                            r'[0-9]+,[0-9]+,[0-9]+:'
                            r'[0-9]+,[0-9]+,[0-9]+', parameters):
                die()
            self._parameters = [x.split(',') for x in parameters.split(':')]

    @property
    def name(self):
        """str: the failure model name."""
        return self._name

    @property
    def distribution(self):
        """str: the failure model distribution."""
        return self._distribution

    @property
    def parameters(self):
        """list: the failure model parameter list."""
        return self._parameters

    @property
    def standby_state(self):
        """str: the failure model standby state."""
        return self._standby_state

    @property
    def remarks(self):
        """str: the failure model remarks."""
        return self._remarks


class Manpower(object):
    """Class modelling a manpower declaration."""

    def __init__(self, mptype, availability, cost):
        """Initialize Manpower."""
        self._mptype = mptype
        try:
            self._availability = int(availability)
        except ValueError:
            errstr = ('Manpower type "{}" - availability should be an integer'
                      .format(mptype))
            _logger.error(errstr)
            raise TranslatorError(errstr)
        try:
            self._cost = float(cost)
        except ValueError:
            errstr = ('Manpower type "{}" - cost should be a float'
                      .format(mptype))
            _logger.error(errstr)
            raise TranslatorError(errstr)

    @property
    def manpower_type(self):
        """str: the manpower type."""
        return self._mptype

    @property
    def availability(self):
        """int: the available units of the manpower."""
        return self._availability

    @property
    def cost(self):
        """float: the manpower cost."""
        return self._cost


class Spare(object):
    """Class modelling a spare declaration."""

    def __init__(self, devtype, availability, cost):
        """Initialize Spare."""
        self._devtype = devtype
        try:
            self._availability = int(availability)
        except ValueError as e:
            errstr = ('Spare type "{}" - availability should be an integer'
                      .format(devtype))
            _logger.error(errstr)
            raise TranslatorError(errstr)
        try:
            self._cost = float(cost)
        except ValueError as e:
            errstr = ('Spare type "{}" - cost should be a float'
                      .format(devtype))
            _logger.error(errstr)
            raise TranslatorError(errstr)

    @property
    def device_type(self):
        """str: the spare (device) type."""
        return self._devtype

    @property
    def availability(self):
        """int: the available units of the spare."""
        return self._availability

    @property
    def cost(self):
        """float: the spare cost."""
        return self._cost


__all__ = [
    'SystemElement',
    'ElementLogic',
    'FailureModel',
    'Manpower',
    'Spare',
]
