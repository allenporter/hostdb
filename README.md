# hostdb

This is an ansible plugin library that provides custom functionality to use terraform
as inventory in ansible playbooks. This also helps with terraform machine management
to define machines using a proper naming scheme. The original intended use case was
for proxmox VMs, though can be used with other terraform providers.

## Details

This library provides an ansibile inventory plugin powered by the terraform database. Hosts
are provisioned and updated in terraform, then can be used to power ansible inventory.

This library also contains modules useful for allocating new hostnames, and generally validating
that the host database is setup correctly.

## Machine naming

Machines are allocated following [A Proper Server Naming Scheme](https://mnx.io/blog/a-proper-server-naming-scheme/) that helps us treat our machines like cattle, but still find them. The basics are:

  - You have a domain name that all hosts are assigned to e.g. `example.com`
  - Every host assigned a name from a wordlist, however we don't have to care about it in practice. e.g.  `blast.example.com`
  - A site has a geograph e.g. `lax.example.com`
  - Every machine has one or more purposes (e.g. a service that it runs) and has a CNAME for each. Serial numbers are
    added to identify the service. e.g. `mon01.lax.example.com`

Hostnames are allocated using a wordlist `hostdb/resources/wordlist` which are reasonably
interesting names recommended from the naming scheme above.

This is just a quick summary, but see the above article for more details.

# Database format

This inventory module expects to have the following output variables in `outputs.tf`:

```
output "hosts" {
  description = "All allocated hostnames (including retired)"
  value = local.all_hosts
}

output "node_ids" {
  description = "A map of hosts to proxmox VM node ids"
  value = module.vms.node_id
}

output "services" {
  description = "Assignments for all services"
  value = var.services
}
```

The values above are examples from a real terraform module, but they would obviously be
different based on your provider.

An example of a `hosts` output looks something like the following:
```
"blast": {
    "ip": "192.168.1.80",
},
"domino": {
    "ip": "192.168.1.81",
},
"exodus": {
    "ip": "192.168.1.82",
},
```

All parameters are included in the ansible inventory as host variables.

The `services` output assigns machines to DNS names which are the same
prefixes used as the ansible inventory group.
```
"cfg01": "domino",
"mon01": "blast",
"mon02": "exodus",
```

I recommend using these with a terraform DNS provider to automatically
manage DNS for you.

## Ansible inventory

This assumes you have a repository setup with multiple terraform environments
for `dev` and `prod`. Each environment has an inventory config file e.g. `hosts/prod/inventory.yaml`

You need to install `hostdb` using pip:
```
$ pip install hostdb
```

Then make the hostdb module discoverable by ansible. Create a file `~/.ansible/plugins/inventory/hostdb.py` with the contents:
```
from hostdb.inventory import DOCUMENTATION, InventoryModule
```

Then tell ansible about the hostdb inventory plugin in `ansible.cfg`:
```
[inventory]
enable_plugins = hostdb
```

These are examples of the prod and dev inventory config files. From `hosts/prod/inventory.yaml`:
```
---
plugin: hostdb.inventory
env: prod
```

From `hosts/dev/inventory.yaml`:
```
---
plugin: hostdb.inventory
env: dev
```

You can test the plugin with `ansible-inventory --list -i hosts/dev/inventory.yaml` and see
the terraform output variables you have defined as part of the ansibile inventory:
```
$ ansible-inventory --list -i hosts/dev/inventory.yaml | head
{
    "_meta": {
        "hostvars": {
            "cfg01.dev": {
                "ansible_python_interpreter": "/usr/bin/python3",
                "control_plane": "true",
                "cpus": "4",
                "disable_offload_iface": "eth0",
...
```

You can then use the service prefixes as inventory groups e.g. `cfg` or `mon` in the above examples.

## Provisioning

When provisioning a new host, you need to pick a new host name then add it to terraform
and deploy the machine using your method of choice (e.g. proxmox terraform provider).
The `allocate_hostname` tool can help you pick an available name from the wordlist that
has not already been allocated. Run the command and it shows you 5 choices to pick from
so you don't get stuck with a name you don't like. The rest of the names are thrown back
into the pool.

This assumes the terraform paths are `hosts/{dev,prod}/`

```shell
$ allocate_hostname
natural
almanac
panther
monkey
urban
```

## Validation

You can verify your inventory and hostdb are working by validating the db. Point it at your
terraform directory to confirm the structure is as expected:

```shell
$ validate_hostdb hosts/prod
Success
```

## Development

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
$ py.test
```
