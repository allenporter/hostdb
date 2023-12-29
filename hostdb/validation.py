"""Validation of hostdb manifests."""

import re


from .exceptions import HostDbConfigError
from .manifest import Manifest, SERVICE_MATCH


def validate_manifest(manifest: Manifest) -> None:
    hosts = {}
    ips = {}
    macs = {}
    services = {}

    service_types = set(manifest.service_types)
    if len(service_types) != len(manifest.service_types):
        raise HostDbConfigError("Duplicate service types: %s" % manifest.service_types)

    hardware_labels = set(manifest.hardware_labels)
    if len(hardware_labels) != len(manifest.hardware_labels):
        raise HostDbConfigError(
            "Duplicate hardware labels: %s" % manifest.hardware_labels
        )

    for machine in manifest.machines:
        if host := machine.host:
            if host in hosts:
                raise HostDbConfigError(
                    "Duplicate host '%s' for '%s' and '%s'"
                    % (host, hosts[host], machine)
                )
            hosts[host] = machine
        if ip := machine.ip:
            if ip in ips:
                raise HostDbConfigError(
                    "Duplicate IP for '%s' and '%s': %s" % (ips[ip], machine.host, ip)
                )
            ips[ip] = machine.host
        if mac := machine.mac:
            if mac in macs:
                raise HostDbConfigError(
                    "Duplicate MAC for '%s' and '%s': %s"
                    % (macs[mac], machine.host, mac)
                )
            macs[mac] = machine.host
        for service in machine.services:
            if service in services:
                raise HostDbConfigError(
                    "Duplicate service '%s' for '%s' and '%s'"
                    % (service, services[service], machine.host)
                )
            services[service] = machine.host

            match = re.match(SERVICE_MATCH, service)
            if not match:
                continue
            func = match.group(1)
            if func not in service_types:
                raise HostDbConfigError(
                    "Service type '%s' for '%s' not defined in service_types: %s"
                    % (func, machine.host, manifest.service_types)
                )
        for label in machine.hardware_labels:
            if label not in hardware_labels:
                raise HostDbConfigError(
                    "Hardware label '%s' for '%s' not defined in hardware_labels: %s"
                    % (label, machine.host, manifest.hardware_labels)
                )
