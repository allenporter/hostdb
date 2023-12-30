"""Tests for hostdb."""

import pathlib

import pytest

from hostdb.hostdb import HostDb
from hostdb.manifest import Manifest, Machine
from hostdb.exceptions import HostDbException


EXAMPLES = pathlib.Path.cwd() / pathlib.Path("examples")
EXAMPLE_CONFIG = EXAMPLES / "manifest.yaml"
TESTDATA = pathlib.Path.cwd() / pathlib.Path("tests/testdata")
INVALID_CONFIG = TESTDATA / "invalid/invalid_config.yaml"
INCLUDES_CONFIG = TESTDATA / "includes/manifest.yaml"
INCLUDES_INVALID_CONFIG = TESTDATA / "includes_invalid/manifest.yaml"


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

    db = HostDb.from_yaml(EXAMPLE_CONFIG)
    assert list(db.hostnames) == ["friend", "lagoon", "latin"]


def test_not_yaml_format() -> None:
    """Exercises reading an invalid configuration file."""
    with pytest.raises(HostDbException, match=r"did not find expected"):
        HostDb.from_yaml(pathlib.Path.cwd() / "setup.cfg")


def test_yaml_list_not_dict() -> None:
    """Exercises reading an invalid configuration file."""
    with pytest.raises(HostDbException, match=r"Could not parse"):
        HostDb.from_yaml(INVALID_CONFIG)


def test_file_not_exists() -> None:
    """Exercises reading an invalid configuration file."""
    with pytest.raises(HostDbException, match=r"Could not read"):
        HostDb.from_yaml(TESTDATA / "does-not-exist.yaml")


def test_includes_config() -> None:
    """Exercises reading a cluster configuration file from disk."""

    db = HostDb.from_yaml(INCLUDES_CONFIG)
    assert list(db.hostnames) == ["friend", "lagoon", "latin"]
    assert len(db.manifest.network) == 1
    assert db.services == {"rtr01": "friend", "sto01": "lagoon"}
    assert db.manifest.network[0].subnet == "192.168.1.0/24"
    assert db.manifest.hardware_labels == ["nvidia_gpu", "intel_gpu", "edgeos"]


def test_include_invalid_file(fixed_seed) -> None:
    """Exercises reading a configuration file that includes a missing file."""
    with pytest.raises(HostDbException, match=r"includes_invalid/missing.yaml' does not exist"):
        HostDb.from_yaml(INCLUDES_INVALID_CONFIG)
