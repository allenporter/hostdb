"""Library for reading the terraform database."""

import json
import random
import re
from importlib.resources import files
from typing import Any

import python_terraform


class HostDbException(Exception):
    """Error raised working with the host database."""


class HostDbConfigError(HostDbException):
    """Exception raised for errors in configuration"""


class HostDb:
    """Library for managing terraform inventory."""

    def __init__(self, cfg: dict[str, Any]):
        """Initialize HostDb."""
        if "values" not in cfg:
            raise HostDbException(f"Invalid hostdb configuration missing 'values': {cfg}")
        outputs = cfg["values"]["outputs"]
        all_hosts = outputs["hosts"]["value"]
        node_ids = outputs["node_ids"]["value"]
        services = outputs["services"]["value"]

        for (hostname, node_id) in node_ids.items():
            if hostname not in all_hosts:
                continue
            all_hosts[hostname]["node_id"] = node_id
        self._hosts = all_hosts

        self._services = services
        self._service_groups = {}
        for (service, host) in services.items():
            match = re.match("([a-z|_|-]+)\\d+", service)
            if not match:
                continue
            func = match.group(1)
            if func not in self._service_groups:
                self._service_groups[func] = {}
            self._service_groups[func][service] = host

    @classmethod
    def FromTerraform(cls, hostdb_dir: str) -> "HostDb":
        """Initialize HostDB from a terraform directory."""
        t = python_terraform.Terraform(working_dir=hostdb_dir)
        return_code, stdout, stderr = t.show("-json")
        if return_code != 0:
            raise HostDbException("Could not run terraform: %s", stderr)
        cfg = json.loads(stdout)
        return HostDb(cfg)

    @property
    def hosts(self):
        return self._hosts

    @property
    def hostnames(self):
        return self._hosts.keys()

    @property
    def services(self):
        return self._services

    @property
    def service_groups(self):
        return self._service_groups


def validate_raw(hosts: dict[str, Any], services: dict[str, str]):
    ips = {}
    macs = {}
    for (host, config) in hosts.items():
        if "ip" in config:
            ip = config["ip"]
            if ip in ips:
                raise HostDbConfigError(
                    "Duplicate IP for '%s' and '%s': %s" % (ips[ip], host, ip)
                )
            ips[ip] = host
        if "mac" in config:
            mac = config["mac"]
            if mac in macs:
                raise HostDbConfigError(
                    "Duplicate MAC for '%s' and '%s': %s" % (macs[mac], host, mac)
                )
            macs[mac] = host

    for (service, host) in services.items():
        if host not in hosts:
            raise HostDbConfigError(
                "Service '%s' host '%s' not found in hosts" % (service, host)
            )


def validate(db: HostDb) -> None:
    """Validate the specified host database."""
    validate_raw(db.hosts, db.services)


def build_hostname_set() -> dict[str, str]:
    """Return the hostname set from the wordlist."""
    words: dict[str, str] = {}
    text = files("hostdb.resources").joinpath("wordlist").read_text(encoding="utf-8")
    for line in text.split("\n"):
        if line.startswith("#"):
            continue
        for w in line.split(" "):
            w = w.strip()
            if not w:
                continue
            words[w] = ""
    return words


def allocate_hostnames(
    dbs: list[HostDb], count: int, rand=random.Random()
) -> list[str]:
    """Produce the specified number of new hostnames that are not already allocated."""
    # Attempts to preserve order to facilitate testing with fixed random
    hostname_set = build_hostname_set()
    for db in dbs:
        for host in db.hostnames:
            if host in hostname_set:
                del hostname_set[host]
    hostname_pool = list(hostname_set.keys())
    random.shuffle(hostname_pool)
    return hostname_pool[0:count]
