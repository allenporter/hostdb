"""An ansible inventory module based on hostdb backed by hostdb.

This has some custom helpers for building etcd inventory.
"""

import dataclasses
import json
import os
import re
import logging
import pathlib

from ansible.errors import AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin

from . import hostdb, exceptions

_LOGGER = logging.getLogger(__name__)


DOCUMENTATION = r"""
  name: hostdb
  plugin_type: inventory
  short_description: Generates ansible inventory from hostdb state
  options:
    plugin:
      description: Name of the plugin
      required: true
      choices: ['hostdb']
    manifest:
      description: Manifest file that contains the hostdb state
      required: true
"""


class InventoryModule(BaseInventoryPlugin):
    """Inventory module for host db."""

    NAME = "hostdb"

    def verify_file(self, path):
        """Return true/false if this is possibly a valid file for this plugin."""
        self.display.vvv("Verifying %s is a valid hostdb inventory file" % path)
        if super().verify_file(path):
            if os.path.isdir(path):
                return True
            if any(path.endswith(x) for x in [".yaml", ".yml"]):
                return True
        self.display.vvv("Inventory file '%s' is not valid for hostdb" % path)
        return False

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path, cache)

        self._read_config_data(path)
        try:
            self._manifest = self.get_option("manifest")
        except Exception as e:
            raise AnsibleParserError(
                f"Unable to read 'manifest' option from inventory: {str(e)}"
            ) from e

        try:
            db = hostdb.HostDb.from_yaml(pathlib.Path(self._manifest))
        except exceptions.HostDbException as e:
            raise AnsibleParserError(f"Unable to read hostdb manifest {self._manifest}: {str(e)}") from e

        try:
            hostdb.validate(db)
        except exceptions.HostDbException as e:
            raise AnsibleParserError(f"Invalid hostdb manifest {self._manifest}: {str(e)}") from e

        env = db.manifest.env
        for group, group_config in db.service_groups.items():
            self.inventory.add_group(group)
            for srv_host, host in group_config.items():
                if env:
                    full_host = "%s.%s" % (srv_host, env)
                else:
                    full_host = srv_host
                self.inventory.add_host(host=full_host, group=group)
                self.inventory.set_variable(full_host, "manifest_host", host)

                machine = db.hosts[host]
                for k, v in dataclasses.asdict(machine).items():
                    self.inventory.set_variable(full_host, k, v)
