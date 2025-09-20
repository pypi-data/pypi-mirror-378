"""TcEx Framework Module"""

# standard library
import logging
from functools import cached_property

from ...app.key_value_store.key_value_store import KeyValueStore
from ...util.model.playbook_variable_model import PlaybookVariableModel
from ...util.util import Util
from .playbook_create import PlaybookCreate
from .playbook_delete import PlaybookDelete
from .playbook_output import PlaybookOutput
from .playbook_read import PlaybookRead

# get logger
_logger = logging.getLogger(__name__.split('.', maxsplit=1)[0])


class Playbook:
    """Playbook methods for accessing key value store.

    Args:
        key_value_store: A KV store instance.
        context: The KV Store context/session_id. For PB Apps the context is provided on
            startup, but for service Apps each request gets a different context.
        output_variables: The requested output variables. For PB Apps outputs are provided on
            startup, but for service Apps each request gets different outputs.
    """

    def __init__(
        self,
        key_value_store: KeyValueStore,
        context: str | None = None,
        output_variables: list | None = None,
    ):
        """Initialize the class properties."""
        self.context = context
        self.key_value_store = key_value_store
        self.output_variables = output_variables or []

        # properties
        self.log = _logger
        self.util = Util()

    def check_key_requested(self, key: str) -> bool:
        """Return True if output key was requested by downstream app.

        Provide key should be in format "app.output".
        """
        variables = []
        for variable in self.output_variables:
            var = self.util.get_playbook_variable_model(variable)
            if isinstance(var, PlaybookVariableModel):
                variables.append(var.key)

        return key in variables

    def check_variable_requested(self, variable: str) -> bool:
        """Return True if output variable was requested by downstream app.

        Provide variable should be in format of "#App:1234:app.output!String".
        """
        return variable in self.create.output_variables

    def get_variable_type(self, variable: str) -> str:
        """Get the Type from the variable string or default to String type.

        The default type is "String" for those cases when the input variable is
        contains not "DB variable" and is just a String.

        Example Variable:

        #App:1234:output!StringArray returns **StringArray**

        Example String:

        "My Data" returns **String**
        """
        return self.util.get_playbook_variable_type(variable)

    @cached_property
    def create(self) -> PlaybookCreate:
        """Return instance of PlaybookCreate"""
        if self.context is None:
            ex_msg = 'Playbook context is required for PlaybookCreate.'
            raise RuntimeError(ex_msg)

        return PlaybookCreate(self.context, self.key_value_store, self.output_variables)

    @cached_property
    def delete(self) -> PlaybookDelete:
        """Return instance of PlaybookDelete"""
        if self.context is None:
            ex_msg = 'Playbook context is required for PlaybookDelete.'
            raise RuntimeError(ex_msg)

        return PlaybookDelete(self.context, self.key_value_store)

    def is_variable(self, key: str) -> bool:
        """Return True if provided key is a properly formatted playbook variable."""
        return self.util.is_playbook_variable(key)

    @cached_property
    def output(self) -> PlaybookOutput:
        """Return instance of PlaybookOutput"""
        return PlaybookOutput(self)

    @cached_property
    def read(self) -> PlaybookRead:
        """Return instance of PlaybookRead"""
        if self.context is None:
            ex_msg = 'Playbook context is required for PlaybookRead.'
            raise RuntimeError(ex_msg)

        return PlaybookRead(self.context, self.key_value_store)
