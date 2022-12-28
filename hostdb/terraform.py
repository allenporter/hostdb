"""An ansible inventory module based on hostdb."""

import json
import os
import re

import python_terraform
from ansible.errors import AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin

DOCUMENTATION = r"""
  name: terraform
  plugin_type: inventory
  short_description: Generates ansible inventory from terraform state
  options:
    plugin:
      description: Name of the plugin
      required: true
      choices: ['terraform']
    env:
      description: Environment used for separation and naming
      required: true
"""


class InventoryModule(BaseInventoryPlugin):

    NAME = "terraform"

    def verify_file(self, path):
        """return true/false if this is possibly a valid file for this plugin to consume"""
        if super(InventoryModule, self).verify_file(path):
            path_dir = os.path.dirname(path)
            main_tf = "%s/main.tf" % (path_dir)
            if not os.path.exists(main_tf):
                return False
        return True

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        try:
            # Store the options from the YAML file
            self._env = self.get_option("env")
        except Exception as e:
            raise AnsibleParserError("All correct options required: {}".format(e))

        inv_path = os.path.dirname(path)
        t = python_terraform.Terraform(working_dir=inv_path)
        return_code, stdout, stderr = t.show("-json")
        if return_code != 0:
            raise Exception("Could not run terraform: %s", stderr)
        cfg = json.loads(stdout)
        outputs = cfg["values"]["outputs"]
        all_hosts = outputs["hosts"]["value"]
        node_ids = outputs["node_ids"]["value"]
        services = outputs["services"]["value"]

        for (hostname, config) in all_hosts.items():
            # TODO(allen): Swap out "node_ip" with "ip" everywhere so this
            # block can be removed.
            if "ip" in config:
                config["node_ip"] = config["ip"]
            # Join this into the main dict since its a separate output field
            if hostname in node_ids:
                config["node_id"] = node_ids[hostname]

        # Infer groups based on hostname prefix (e.g. "vmm01" => "vmm")
        service_groups = {}
        for (service, host) in services.items():
            match = re.match(r"([a-z|_|-]+)\d+", service)
            if not match:
                continue
            func = match.group(1)
            if func not in service_groups:
                service_groups[func] = {}
            service_groups[func][service] = host

        etcd_cluster_string = self.compute_etcd_cluster_string(all_hosts)

        for (group, group_config) in service_groups.items():
            self.inventory.add_group(group)
            for srv_host in group_config.keys():
                full_host = "%s.%s" % (srv_host, self._env)
                self.inventory.add_host(host=full_host, group=group)
                hostname = services[srv_host]
                if hostname not in all_hosts:
                    raise Exception(f"Could not find host {hostname} in inventory")
                host_config = all_hosts[hostname]
                for (k, v) in host_config.items():
                    self.inventory.set_variable(full_host, k, v)
                if etcd_cluster_string:
                    self.inventory.set_variable(
                        full_host, "etcd_cluster", etcd_cluster_string
                    )

    def compute_etcd_cluster_string(self, hosts):
        etcd_cluster = {}
        for (hostname, config) in hosts.items():
            # compute the etcd cluster string
            if "etcd_name" not in config:
                continue
            if "etcd_ip" not in config:
                raise AnsibleParserError(
                    "Inventory missing etcd_ip for host {}: {}".format(hostname, config)
                )
            if "etcd_port" not in config:
                raise AnsibleParserError(
                    "Inventory missing etcd_port for host {}: {}".format(
                        hostname, config
                    )
                )
            etcd_cluster[config["etcd_name"]] = "http://{}:{}".format(
                config["etcd_ip"], config["etcd_port"]
            )
        return ",".join(["{}={}".format(k, v) for k, v in etcd_cluster.items()])
