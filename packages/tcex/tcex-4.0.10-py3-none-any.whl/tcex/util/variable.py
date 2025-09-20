"""TcEx Framework Module"""

# standard library
import re

from .model.playbook_variable_model import PlaybookVariableModel


class BinaryVariable(bytes):
    """Bytes object with internal variable type field. Used when reading playbook variables"""

    _variable_type = 'Binary'


class StringVariable(str):
    """String object with internal variable type field. Used when reading playbook variables"""

    _variable_type = 'String'


class Variable:
    """TcEx Utilities Variables Class"""

    def contains_playbook_variable(self, key: str) -> bool:
        """Return True if provided key contains a properly formatted playbook variable."""
        return isinstance(key, str) and bool(re.search(self.variable_playbook_pattern, key))

    def contains_tc_variable(self, key: str):
        """Return True if provided key contains a properly formatted TC variable."""
        return isinstance(key, str) and bool(re.search(self.variable_tc_pattern, key))

    def get_playbook_variable_model(self, variable: str | None) -> PlaybookVariableModel | None:
        """Return data model of playbook variable (e.g., #App:1234:output!String)."""
        if variable is None:
            return None

        data = None
        variable = variable.strip()
        if re.match(self.variable_playbook_match, variable):
            var = re.search(self.variable_playbook_parse, variable)
            if var is not None:
                data = PlaybookVariableModel(**var.groupdict())
        return data

    def get_playbook_variable_type(self, variable: str) -> str:
        """Get variable type"""
        model = self.get_playbook_variable_model(variable)
        return 'String' if model is None else model.type

    def is_playbook_variable(self, key: str) -> bool:
        """Return True if provided key is a properly formatted playbook variable."""
        return isinstance(key, str) and bool(re.match(self.variable_playbook_match, key))

    def is_tc_variable(self, key: str) -> bool:
        """Return True if provided key is a properly formatted tc variable."""
        return isinstance(key, str) and bool(re.match(self.variable_tc_match, key))

    @property
    def variable_expansion_pattern(self) -> re.Pattern:
        """Regex pattern to match and parse a playbook or ThreatConnect variable.

        Playbook Variable : #App:334:example.service_input!String
                          : #Global:0:gbl.timestamp.iso!String
                          : #Trigger:1:testing.body!String
        TC Variable       : &{TC:TEXT:4dc9202e-6945-4364-aa40-4b47655046d2}
        """
        return re.compile(
            # Origin:
            # PB-Variable: "#"
            # TC-Variable: "&"
            r'(?P<origin>#|&)'
            r'(?:\{)?'  # drop "{"
            # Provider:
            # PB-Variable: provider - literal "App|Trigger"
            # TC-Variable: provider - literal "TC|Vault"
            r'(?P<provider>App|Global|TC|Trigger|Vault):'
            # ID:
            # PB-Variable: Job ID (e.g., 334)
            # TC-Variable: One of (FILE|KEYCHAIN|TEXT)
            r'(?P<id>[\w]+):'
            # Lookup:
            # PB-Variable: variable id (e.g., API Token)
            # TC-Variable: variable id (e.g., 4dc9202e-6945-4364-aa40-4b47655046d2)
            r'(?P<lookup>[A-Za-z0-9_\.\-\[\]]+)'
            r'(?:\})?'  # drop "}"
            # Type
            # PB-Variable: variable type (e.g., String|StringArray)
            # TC-Variable: N/A
            # r'(?:!(?P<type>[A-Za-z0-9_-]+))?'
            r'(?:!(?P<type>StringArray|BinaryArray|KeyValueArray'
            r'|TCEntityArray|TCEnhancedEntityArray'
            r'|String|Binary|KeyValue|TCEntity|TCEnhancedEntity'
            r'|(?:(?!String)(?!Binary)(?!KeyValue)'
            r'(?!TCEntity)(?!TCEnhancedEntity)'
            r'[A-Za-z0-9_-]+)))?'  # variable type (custom)
        )

    @property
    def variable_playbook_array_types(self) -> list[str]:
        """Return list of standard playbook array variable types."""
        return [
            'BinaryArray',
            'KeyValueArray',
            'StringArray',
            'TCEntityArray',
            'TCEnhancedEntityArray',
        ]

    @property
    def variable_playbook_match(self) -> re.Pattern:
        """Return compiled re pattern for exact match of variable."""
        return re.compile(rf'^{self.variable_playbook_pattern}$')

    def variable_playbook_method_name(self, variable: str) -> str | None:
        """Convert variable name to a valid method name.

        #App:9876:string.operation!String -> string_operation_string
        """
        method_name = None
        if variable is not None:
            variable = variable.strip()
            if re.match(self.variable_playbook_match, variable):
                var = re.search(self.variable_playbook_parse, variable)
                if var is not None:
                    variable_name = var.group(3).replace('.', '_').lower()
                    variable_type = var.group(4).lower()
                    method_name = f'{variable_name}_{variable_type}'
        return method_name

    @property
    def variable_playbook_parse(self) -> re.Pattern:
        """Return compiled re pattern."""
        return re.compile(self.variable_playbook_pattern)

    @property
    def variable_playbook_pattern(self) -> str:
        """Regex pattern to match and parse a playbook variable.

        Parse this string: #App:334:example.service_input!String
                         : #Global:0:gbl.timestamp.iso!String
                         : #Trigger:1:testing.body!String
        """
        return (
            # App Type: literal "App|Trigger"
            r'#(?P<app_type>App|Global|Trigger)'
            # Job ID: the Id of the running job (e.g, 7979).
            r':(?P<job_id>[\d]+)'
            # Key: the variable key (e.g., api_token)
            r':(?P<key>[A-Za-z0-9_\.\-\[\]]+)'
            # Type: one of the following types
            #     (Binary|BinaryArray|KeyValue|KeyValueArray|
            #      String|StringArray|TCEntity|TCEntityArray|
            #      or <custom>)
            r'!(?P<type>StringArray|BinaryArray|KeyValueArray'
            r'|TCEntityArray|TCEnhancedEntityArray'
            r'|String|Binary|KeyValue|TCEntity|TCEnhancedEntity'
            r'|(?:(?!String)(?!Binary)(?!KeyValue)'
            r'(?!TCEntity)(?!TCEnhancedEntity)'
            r'[A-Za-z0-9_-]+))'  # variable type (custom)
        )

    @property
    def variable_playbook_single_types(self) -> list[str]:
        """Return list of standard playbook single variable types."""
        return [
            'Binary',
            'KeyValue',
            'String',
            'TCEntity',
            'TCEnhancedEntity',
        ]

    @property
    def variable_playbook_types(self) -> list[str]:
        """Return list of standard playbook variable types."""
        return self.variable_playbook_single_types + self.variable_playbook_array_types

    @property
    def variable_tc_match(self) -> re.Pattern:
        """Return regex pattern for tc variable EXACT match."""
        return re.compile(rf'^{self.variable_tc_pattern}$')

    @property
    def variable_tc_parse(self) -> re.Pattern:
        """Return regex pattern for tc variable search."""
        return re.compile(self.variable_tc_pattern)

    @property
    def variable_tc_pattern(self) -> str:
        """Return regex pattern for tc variable.

        Parse this string -> &{TC:TEXT:4dc9202e-6945-4364-aa40-4b47655046d2}
        """
        return (
            # Origin "&"
            r'(?:&)'
            r'(?:\{)'
            # Provider: literal "TC|Vault"
            r'(?P<provider>TC|Vault):'
            # Type: one of (FILE|KEYCHAIN|TEXT)
            r'(?P<type>FILE|KEYCHAIN|TEXT):'
            # Key: variable id (e.g., 4dc9202e-6945-4364-aa40-4b47655046d2)
            r'(?P<key>[A-Za-z0-9_\.\-\[\]]+)'
            r'(?:\})'
        )
