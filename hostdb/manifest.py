"""Manifest definitions for the hostdb package.

This file contains all of the dataclass definitions for the hostdb package.
"""

from dataclasses import dataclass, field

# "sto01" becomes ("sto", "01")
SERVICE_MATCH = r"([a-z|_|-]+)(\d+)"


@dataclass
class Network:
    """Network configuration."""

    subnet: str
    gateway: str
    nameserver: list[str] = field(default_factory=list)


@dataclass
class Machine:
    """Machine configuration."""

    host: str
    desc: str | None = None
    ip: str | None = None
    mac: str | None = None
    services: list[str] | None = field(default_factory=list)
    hardware_labels: list[str] | None = field(default_factory=list)


@dataclass
class Manifest:
    """Manifest configuration."""

    domain: str | None = None
    site: str | None = None
    name: str | None = None
    service_types: list[str] = field(default_factory=list)
    hardware_labels: list[str] = field(default_factory=list)
    machines: list[Machine] = field(default_factory=list)
    network: list[Network] = field(default_factory=list)
