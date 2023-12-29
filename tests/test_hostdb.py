"""Tests for hostdb."""

import pathlib

import pytest

from hostdb.hostdb import HostDb
from hostdb.manifest import Manifest, Machine
from hostdb.exceptions import HostDbException


TESTDATA = pathlib.Path.cwd() / pathlib.Path("tests/testdata")


def test_empty() -> None:
    """Test structure of an empty hostdb."""
    db = HostDb(Manifest())
    assert db.hosts == {}
    assert list(db.hostnames) == []
    assert db.services == {}
    assert db.service_groups == {}


def test_hostdb_parsing() -> None:
    """Test basic parsing of a hostdb."""
    manifest = Manifest(
        machines=[
            Machine(host="linear", ip="10.10.21.27", services=["cfg01"]),
        ],
        service_types=["cfg"],
    )
    db = HostDb(manifest)
    assert "linear" in db.hosts
    assert db.hosts["linear"].ip == "10.10.21.27"
    assert list(db.hostnames) == ["linear"]
    assert db.services == {"cfg01": "linear"}
    assert db.service_groups == {"cfg": {"cfg01": "linear"}}


def test_hostnames_parsed(fixed_seed) -> None:
    """Exercising allocating hostnames."""
    manifest = Manifest(
        machines=[
            Machine(host="linear"),
        ],
    )
    db = HostDb(manifest)
    assert list(db.hostnames) == ["linear"]


def test_hostnames_allocated(fixed_seed) -> None:
    """Exercises omitting some hostnames that are already allocated."""
    manifest = Manifest(
        machines=[
            Machine(host="friend"),
            Machine(host="lagoon"),
        ],
    )
    db = HostDb(manifest)
    assert list(db.hostnames) == ["friend", "lagoon"]


def test_cluster_config(fixed_seed) -> None:
    """Exercises reading a cluster configuration file from disk."""

    db = HostDb.from_yaml(TESTDATA / "config.yaml")
    assert list(db.hostnames) == ["friend", "lagoon", "latin"]


def test_invalid_yaml() -> None:
    """Exercises reading an invalid configuration file."""
    with pytest.raises(HostDbException, match=r"did not find expected"):
        HostDb.from_yaml(pathlib.Path.cwd() / "setup.cfg")


def test_invalid_yaml() -> None:
    """Exercises reading an invalid configuration file."""
    with pytest.raises(HostDbException, match=r"Could not parse"):
        HostDb.from_yaml(TESTDATA / "invalid_config.yaml")