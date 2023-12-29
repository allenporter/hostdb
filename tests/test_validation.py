"""Test for the hostname validation logic."""

import pytest

from hostdb.validation import validate_manifest
from hostdb.exceptions import HostDbConfigError
from hostdb.manifest import Manifest, Machine


def test_success() -> None:
    """Test validation logic for a service pointing to a missing host."""
    manifest = Manifest(
        machines=[
            Machine(
                host="host1",
                ip="127.0.0.1",
                mac="00:aa:bb:cc:dd:ee",
                services=["web01"],
            ),
            Machine(
                host="host2",
                ip="127.0.0.2",
                mac="bb:aa:bb:cc:dd:ee",
                services=["web02"],
            ),
            Machine(
                host="host3",
                ip="127.0.0.3",
                mac="ee:aa:bb:cc:dd:ee",
                services=["web03"],
            ),
        ],
        service_types=["web", "sto"],
    )
    validate_manifest(manifest)


def test_duplicate_ip() -> None:
    """Test validation logic for services with duplicate ip addresses."""
    manifest = Manifest(
        machines=[
            Machine(
                host="host1",
                ip="127.0.0.1",
                mac="00:aa:bb:cc:dd:ee",
                services=["web01"],
            ),
            Machine(
                host="host2",
                ip="127.0.0.1",
                mac="bb:aa:bb:cc:dd:ee",
                services=["web02"],
            ),
            Machine(
                host="host3",
                ip="127.0.0.3",
                mac="ee:aa:bb:cc:dd:ee",
                services=["web03"],
            ),
        ],
        service_types=["web", "sto"],
    )
    with pytest.raises(HostDbConfigError, match=r"Duplicate IP"):
        validate_manifest(manifest)


def test_duplicate_mac() -> None:
    manifest = Manifest(
        machines=[
            Machine(
                host="host1",
                ip="127.0.0.1",
                mac="00:aa:bb:cc:dd:ee",
                services=["web01"],
            ),
            Machine(
                host="host2",
                ip="127.0.0.2",
                mac="ee:aa:bb:cc:dd:ee",
                services=["web02"],
            ),
            Machine(
                host="host3",
                ip="127.0.0.3",
                mac="ee:aa:bb:cc:dd:ee",
                services=["web03"],
            ),
        ],
        service_types=["web", "sto"],
    )
    with pytest.raises(HostDbConfigError, match=r"Duplicate MAC"):
        validate_manifest(manifest)


def test_duplicate_service() -> None:
    """Test validation logic for hosts using the same service."""
    manifest = Manifest(
        machines=[
            Machine(
                host="host1",
                ip="127.0.0.1",
                mac="00:aa:bb:cc:dd:ee",
                services=["web03"],
            ),
            Machine(
                host="host2",
                ip="127.0.0.2",
                mac="bb:aa:bb:cc:dd:ee",
                services=["web02"],
            ),
            Machine(
                host="host3",
                ip="127.0.0.3",
                mac="ee:aa:bb:cc:dd:ee",
                services=["web03"],
            ),
        ],
        service_types=["web", "sto"],
    )
    with pytest.raises(HostDbConfigError, match=r"Duplicate service"):
        validate_manifest(manifest)


def test_no_service() -> None:
    manifest = Manifest(
        machines=[
            Machine(
                host="host1",
                ip="127.0.0.1",
                mac="00:aa:bb:cc:dd:ee",
                services=["web01"],
            ),
            Machine(
                host="host2",
                ip="127.0.0.2",
                mac="ee:aa:bb:cc:dd:ee",
                services=["web01"],
            ),
            Machine(
                host="host3",
                ip="127.0.0.3",
                mac="ee:aa:bb:cc:dd:ee",
                services=["web01"],
            ),
        ],
        service_types=["sto"],
    )
    with pytest.raises(HostDbConfigError, match="not defined in service_types"):
        validate_manifest(manifest)
