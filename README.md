# hostdb

This is a library for managing homelab hosts using infrastructure as code
principles. The primary motivation is to help manage bare metal machines and
other network infrastructure in an inventory below the kubernetes cluster.

## Details

This library started as a hybrid using terraform for machine management and
exposting the terrafrom state as a dynamic ansible inventory plugin. The initial
use case was for managing VMs in proxmox as well as their DNS records, however
given trouble around the proxmox API with breaking changes and lack of a stable
terraform provider, there is a desire for something simpler and less intertwined
to specific brittle APIs.

The idea now is that the inventory can exist as its own primitive then be used
with other components for provisioning (e.g. could still be used as an
ansible inventory plugin).

This library also contains modules useful for allocating new hostnames, and generally validating
that the host database is setup correctly.

## Machine naming

Machines are allocated following [A Proper Server Naming Scheme](https://mnx.io/blog/a-proper-server-naming-scheme/) that helps us treat our machines like cattle, but still find them. The basics are:

  - You have a domain name that all hosts are assigned to e.g. `example.com`
  - A site has a geography within the domain e.g. `lax.example.com`
  - Every host assigned a name from a wordlist e.g.  `blast.example.com`. However
    we don't have to care about the hosts name in practice.
  - Every machine has one or more purposes (e.g. a service that it runs) and has
    a CNAME for each. Serial numbers are added to identify the service.
    e.g. `kapi01.lax.example.com`

Hostnames are allocated using a wordlist `hostdb/resources/wordlist` which are reasonably
interesting names recommended from the naming scheme above.

This is just a quick summary, but see the above article for more details.

# Manifest format

Infrastructure is defined through a manifest in yaml:
```
---
site:
  domain: lax.example.com
  name: Los Angeles
  env: prod

machines:
- host: friend
  desc: Router
  ip: 192.168.1.1
  mac: 00:11:22:33:44:55
  services:
  - rtr01
- host: lagoon
  desc: Kubernetes API server
  ip: 192.168.1.10
  mac: 00:11:22:33:44:56
  services:
  - kapi01
# Retired machines
- host: latin
```

All parameters are included in the ansible inventory as host variables.

The `services` output assigns machines to DNS names which are the same
prefixes used as the ansible inventory group.
```
"rtr01": "friend",
"kapi01": "lagoon",
```

These can be used with a DNS provider.

## Ansible inventory

See examples/ansible/README.md for an example of how to use a manifest to drive
an ansible inventory with an inventory plugin.


## Provisioning

When provisioning a new host, you need to pick a new host name then add it to the
manifest and deploy the machine using your method of choice (e.g. some IaC provider).
The `allocate` command can help you pick an available name from the wordlist that
has not already been allocated. Run the command and it shows you 5 choices to pick from
so you don't get stuck with a name you don't like. The rest of the names are thrown back
into the pool.

```shell
$ hostdb allocate --path tests/testdata/config.yaml
ninja
reptile
warning
subject
llama
```

## Validation

You can verify your machine manifest is valid:

```shell
$ hostdb validate --path tests/testdata/config.yaml
Success
```

## Development

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
$ py.test
```
