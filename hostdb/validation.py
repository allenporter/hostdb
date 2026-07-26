"""Validation of hostdb manifests."""

import re

from .exceptions import HostDbConfigError
from .manifest import SERVICE_MATCH, Manifest


def validate_manifest(manifest: Manifest) -> None:
    hosts = {}
    ips = {}
    macs = {}
    services = {}

    service_types = set(manifest.service_types)
    if len(service_types) != len(manifest.service_types):
        raise HostDbConfigError(f"Duplicate service types: {manifest.service_types}")

    hardware_labels = set(manifest.hardware_labels)
    if len(hardware_labels) != len(manifest.hardware_labels):
        raise HostDbConfigError(
            f"Duplicate hardware labels: {manifest.hardware_labels}"
        )

    for machine in manifest.machines:
        if host := machine.host:
            if host in hosts:
                raise HostDbConfigError(
                    f"Duplicate host '{host}' for '{hosts[host]}' and '{machine}'"
                )
            hosts[host] = machine
        if ip := machine.ip:
            if ip in ips:
                raise HostDbConfigError(
                    f"Duplicate IP for '{ips[ip]}' and '{machine.host}': {ip}"
                )
            ips[ip] = machine.host
        if mac := machine.mac:
            if mac in macs:
                raise HostDbConfigError(
                    f"Duplicate MAC for '{macs[mac]}' and '{machine.host}': {mac}"
                )
            macs[mac] = machine.host
        for service in machine.services:
            if service in services:
                raise HostDbConfigError(
                    f"Duplicate service '{service}' for '{services[service]}' and '{machine.host}'"
                )
            services[service] = machine.host

            match = re.match(SERVICE_MATCH, service)
            if not match:
                continue
            func = match.group(1)
            if func not in service_types:
                raise HostDbConfigError(
                    f"Service type '{func}' for '{machine.host}' not defined in service_types: {manifest.service_types}"
                )
        for label in machine.hardware_labels:
            if label not in hardware_labels:
                raise HostDbConfigError(
                    f"Hardware label '{label}' for '{machine.host}' not defined in hardware_labels: {manifest.hardware_labels}"
                )
