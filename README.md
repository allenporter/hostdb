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

From `ansible.cfg` this is an example with a default prod inventory:
```
[defaults]
inventory_plugins = /path/to/python/site-packages
inventory = hosts/prod/inventory.yaml
```

You can install hostdb with `pip install hostdb` and find out the path to site-packages
that it is installed under with with `pip show hostdb`.

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

You can then use the service prefixes as inventory groups e.g. `cfg` or `mon` in the above examples.

## Development

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```
