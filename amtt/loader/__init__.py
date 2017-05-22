"""The loader module.

This module consists of all loaders available to the front-end.
The currently available loaders are:
    - CsvLoader
        Loads the model from CSV files.

In order to define new loaders, the following steps are required:
    1. Create your loader class by subclassing the Loader class,
       as described below.
    2. If required, add a subparser in the parse_arguments function found in
       main.py, so that you can support loader invocation from the command
       line. Check the argparse module for details:
       https://docs.python.org/3/library/argparse.html
    3. If (2) was required, then also create a handler function for the command
       line options of your loader. This function shall accept the parsed
       arguments object as its only parameter and return an instance of your
       loader, based on the former. Assign your handler to your sub-parser
       by invoking the set_defaults method on your sub-parser (see current code
       as reference).
"""
import enum
import logging

from itertools import count
from amtt.errors import LoaderError

_logger = logging.getLogger(__name__)


# Used to assign IDs to InputSheet enum members
_isheet_id = iter(count(start=1))


class InputSheet(enum.Enum):
    components = next(_isheet_id)
    logic = next(_isheet_id)
    failure_models = next(_isheet_id)
    component_failures = next(_isheet_id)
    manpower = next(_isheet_id)
    spares = next(_isheet_id)


"""
The following definitions are used for schema validation
(see validate_schema method below).

SCHEMAS is a dict containing members of the InputSheet enum as keys
and sets containing the valid columns for that table as values.
"""
SCHEMAS = {
    InputSheet.components: {
        'type',    # The component type (valid: compound,group,basic).
        'name',    # The component name (ID).
        'parent',  # The component parent (enclosing block).
        'code',    # Component code (ID - usually shorter than name).
        'instances',  # Number of components to define.
    },
    InputSheet.logic: {
        'type',       # The failure type (valid: inherited,failurenode).
        'component',  # Component to assign the logic to (-> Components.Name).
        'logic',      # Logic to assign (valid: AND,OR,ACTIVE(X,Y)).
    },
    InputSheet.failure_models: {
        'name',   # The failure model name (ID).
        'distribution',  # The failure model distribution.
        'parameters',    # The failure model distribution parameters.
        'standbystate',  # The failure model standby state.
        'remarks',  # Remarks on the failure model.
    },
    InputSheet.component_failures: {
        'component',  # The component to assign to (-> Components.Name).
        'failuremodel',  # The failure model to assign (-> FailureModels.Name).
        'phase',  # The simulation phase to assign for.
    },
    InputSheet.manpower: {
        'manpowertype',  # Type of manpower (labor).
        'noavailable',   # Manpower availability.
        'cost',  # Cost of manpower.
    },
    InputSheet.spares: {
        'devicetype',   # Type of device (spare).
        'noavailable',  # Spare availability.
        'cost',  # Cost of spare.
    }
}


class Loader(object):
    """The Loader base class. Every loader must be a subclass of this class.

    A valid Loader must implement the following methods:
        - load(translator: Translator) -> None
            Given a Translator object, this method loads the data model by
            making use of the Translator class methods (check documentation).

    If a Loader fails to implement any of the above methods, then an
    AttributeError is raised at runtime, upon method invocation.

    In most cases, a Loader may be just a simple importer of data, as during
    the translation process model validation gets carried out, so any missed
    errors will be reported at that time.

    However, it is crucial that the Loader carries out data validation before
    instantiating objects or putting data in the Keep.
    """

    # Dictionary defining the input sheet/table/file namee (interpretation
    # depends on the input type, we stick with "sheet" in the definition).
    _sheet_definitions = {
        InputSheet.components: 'Components',
        InputSheet.logic: 'Logic',
        InputSheet.failure_models: 'FailureModels',
        InputSheet.component_failures: 'ComponentFailures',
        InputSheet.manpower: 'Manpower',
        InputSheet.spares: 'Spares',
    }

    @staticmethod
    def strip(val):
        return val.strip() if type(val) == str else val

    @staticmethod
    def validate_schema(schema, schema_type):
        """Perform basic schema validation.

        Raises a LoaderError if any of the columns defined in SCHEMAS
        for schema_type is missing from from schema.

        If schema has more columns than its specification in SCHEMAS,
        then a warning is issued, but no Exception is raised.

        You may override this method in your Loader class if needed,
        e.g. in order to conduct more sophisticated validation.
        """
        schema_def = SCHEMAS[schema_type]
        schema = set(schema)
        if schema_def - schema:  # Columns missing from input schema => ERROR
            _logger.error('Input schema for %s is missing some columns: %s',
                          schema_type.name, schema_def - schema)
            raise LoaderError(
                'Schema validation for {} failed'.format(schema_type.name))
        elif schema - schema_def:  # Input schema has extra columns => WARNING
            _logger.warning('Input schema for %s has extra columns: %s',
                            schema_type.name, schema - schema_def)

    @staticmethod
    def sheet_definitions_iter():
        for definition in Loader._sheet_definitions.items():
            yield definition


# Contains all available loaders.
__all__ = ['csv', 'excel']
