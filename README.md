# hostdb

A library or module machine management using Terraform, Ansible. The primary use case
of this is with the terraform proxmox provider, though it could work with any other
terraform based provider that provisions machines.

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

## Development

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```
