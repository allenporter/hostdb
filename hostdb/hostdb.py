"""Library for reading the terraform database."""

import re
import pathlib
import yaml

from mashumaro.codecs.yaml import yaml_decode

from .manifest import Manifest, Machine, SERVICE_MATCH
from .validation import validate_manifest
from .exceptions import HostDbException


class HostDb:
    """Library for managing terraform inventory."""

    def __init__(self, manifest: Manifest) -> None:
        """Initialize HostDb."""
        self._manifest = manifest

        all_hosts = {machine.host: machine for machine in manifest.machines}
        services = {
            service: machine.host
            for machine in manifest.machines
            for service in machine.services
        }
        self._hosts = all_hosts

        self._services = services
        self._service_groups = {}
        for service, host in services.items():
            match = re.match(SERVICE_MATCH, service)
            if not match:
                continue
            func = match.group(1)
            if func not in self._service_groups:
                self._service_groups[func] = {}
            self._service_groups[func][service] = host

    @classmethod
    def from_yaml(cls, config: pathlib.Path) -> "HostDb":
        """Initialize HostDB from a yaml string."""
        try:
            manifest = yaml_decode(config.read_text(), Manifest)
        except FileNotFoundError as err:
            raise HostDbException(f"Could not read {config}: {err}") from err
        except yaml.parser.ParserError as err:
            raise HostDbException(f"Could not parse {config}: {err}") from err
        except ValueError as err:
            raise HostDbException(f"Could not parse {config}: {err}") from err
        return HostDb(manifest)

    @property
    def manifest(self) -> list[Manifest]:
        return self._manifest

    @property
    def hosts(self) -> dict[str, Machine]:
        return self._hosts

    @property
    def hostnames(self) -> list[str]:
        return self._hosts.keys()

    @property
    def services(self) -> list[str]:
        return self._services

    @property
    def service_groups(self) -> dict[str, dict[str, str]]:
        return self._service_groups


def validate(db: HostDb) -> None:
    """Validate the specified host database."""
    validate_manifest(db.manifest)
