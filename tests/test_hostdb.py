"""Tests for hostdb."""

import random

import pytest

from hostdb.hostdb import HostDb, HostDbConfigError, allocate_hostnames, validate

DIR = "."


@pytest.fixture
def fixed_seed() -> None:
    """Fixture to apply a fixed seed."""
    random.seed(0)


def test_empty() -> None:
    """Test structure of an empty hostdb."""
    db = HostDb(
        {
            "values": {
                "outputs": {
                    "hosts": {
                        "value": {},
                    },
                    "node_ids": {
                        "value": {},
                    },
                    "services": {
                        "value": {},
                    },
                },
            },
        }
    )
    assert db.hosts == {}
    assert list(db.hostnames) == []
    assert db.services == {}
    assert db.service_groups == {}


def test_hostdb_parsing() -> None:
    """Test basic parsing of a hostdb."""
    db = HostDb(
        {
            "values": {
                "outputs": {
                    "hosts": {
                        "value": {
                            "linear": {
                                "ip": "10.10.21.27",
                                "cpus": "2",
                                "memory": "2048",
                                "target_node": "pelican",
                            },
                        },
                    },
                    "node_ids": {
                        "value": {
                            "linear": "100",
                        },
                    },
                    "services": {
                        "value": {
                            "cfg01": "linear",
                        },
                    },
                },
            },
        }
    )
    assert "linear" in db.hosts
    assert db.hosts["linear"].get("cpus") == "2"
    assert list(db.hostnames) == ["linear"]
    assert db.services == {"cfg01": "linear"}
    assert db.service_groups == {"cfg": {"cfg01": "linear"}}

    validate(db)


def test_missing_host_for_service() -> None:
    """Test validation logic for a service pointing to a missing host."""
    db = HostDb(
        {
            "values": {
                "outputs": {
                    "hosts": {
                        "value": {},
                    },
                    "node_ids": {
                        "value": {},
                    },
                    "services": {
                        "value": {
                            "cfg01": "linear",
                        },
                    },
                },
            },
        }
    )

    with pytest.raises(HostDbConfigError, match="not found in hosts"):
        validate(db)


def test_allocate_hostnames(fixed_seed) -> None:
    """Exercising allocating hostnames."""

    db = HostDb(
        {
            "values": {
                "outputs": {
                    "hosts": {
                        "value": {
                            "linear": {},
                        }
                    },
                    "node_ids": {
                        "value": {},
                    },
                    "services": {
                        "value": {},
                    },
                }
            }
        }
    )
    hostnames = allocate_hostnames([db], 5, rand=random.Random(1))
    assert hostnames == ["exile", "friend", "falcon", "lagoon", "earth"]


def test_hostnames_allocated(fixed_seed) -> None:
    """Exercises omitting some hostnames that are already allocated."""

    db = HostDb(
        {
            "values": {
                "outputs": {
                    "hosts": {
                        "value": {
                            "friend": {},
                            "lagoon": {},
                        }
                    },
                    "node_ids": {
                        "value": {},
                    },
                    "services": {
                        "value": {},
                    },
                }
            }
        }
    )
    hostnames = allocate_hostnames([db], 5)
    assert hostnames == ["exile", "frozen", "falcon", "laser", "earth"]
