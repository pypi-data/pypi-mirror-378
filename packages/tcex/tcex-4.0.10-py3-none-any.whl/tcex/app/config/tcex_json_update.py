"""TcEx Framework Module"""

# standard library
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tcex_json import TcexJson  # CIRCULAR-IMPORT


class TcexJsonUpdate:
    """Config object for tcex.json configuration file (updater)"""

    def __init__(self, tj: 'TcexJson'):
        """Initialize instance properties."""
        self.tj = tj

    def multiple(self, template: str | None = None):
        """Update the contents of the tcex.json file."""

        # update app_name
        self.update_package_app_name()

        # update deprecated fields
        self.update_deprecated_fields()

        # update package excludes
        self.update_package_excludes()

        # update template
        if template is not None:
            self.tj.model.template_name = template

        # write updated profile
        self.tj.write()

    def update_deprecated_fields(self):
        """Update the lib_versions array in the tcex.json file."""
        if hasattr(self.tj.model, 'lib_versions'):
            self.tj.model.lib_versions = None

    def update_package_app_name(self):
        """Update the package app_name in the tcex.json file."""
        if (
            self.tj.model.package.app_name is None
            or self.tj.model.package.app_name in self.tj.ij.app_prefixes.values()
        ):
            # lower case name and replace prefix if already exists
            _app_name = Path.cwd().name.lower().replace(self.tj.ij.app_prefix.lower(), '')

            # replace spaces and dashes with underscores
            _app_name = _app_name.replace(' ', '_').replace('-', '_').lower()

            # title case app name
            _app_name = '_'.join([a.title() for a in _app_name.split('_')])

            # prepend appropriate App prefix (e.g., TCPB_-_)
            _app_name = f'{self.tj.ij.app_prefix}{_app_name}'

            # update App name
            self.tj.model.package.app_name = _app_name

    def update_package_excludes(self):
        """Update the excludes values in the tcex.json file."""
        for i in [
            '.gitignore',
            '.pre-commit-config.yaml',
            'app_spec.yaml',
            'local-*',
            'pyproject.toml',
        ]:
            if i not in self.tj.model.package.excludes:
                # TODO: [low] pydantic doesn't seem to allow removing items from list???
                self.tj.model.package.excludes.append(i)
