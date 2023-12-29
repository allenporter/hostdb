## Hostdb Ansible Inventory Plugin

See `examples/manifest.yaml` for the manifest example.

You need to install `hostdb` using pip:
```
$ pip install hostdb
```

Then make the hostdb module discoverable by ansible. Next a playbook, create a file `inventory_plugins/hostdb.py` with the contents:
```
from hostdb.inventory import DOCUMENTATION, InventoryModule
```

Then tell ansible about the hostdb inventory plugin in `ansible.cfg`:
```
[inventory]
enable_plugins = hostdb
```

Then in the inventory file `hosts/inventory.yaml` reference the cluster manifest:
```
---
plugin: hostdb
manifest: examples/manifest.yaml
```

You can test the plugin with `ansible-inventory --list -i hosts/inventory.yaml` and see
the terraform output variables you have defined as part of the ansibile inventory:
```
$ ANSIBLE_CONFIG=examples/ansible/ansible.cfg ansible-inventory --list | head
{
    "_meta": {
        "hostvars": {
            "rtr01": {
                "desc": "Router",
                "hardware_labels": [],
                "host": "friend",
                "ip": "192.168.1.1",
                "mac": "00:11:22:33:44:55",
                "manifest_host": "friend",
...
```

You can then use the service prefixes as inventory groups e.g. `rtr` or `sto` in the above examples.