"""Tests for the hostname allocation logic."""

import random

import pytest

from hostdb.naming import allocate_hostnames


@pytest.mark.parametrize(
    ("allocated", "expected"),
    [
        ({}, ["exile", "friend", "falcon", "lagoon", "earth"]),
        ({"linear"}, ["exile", "friend", "falcon", "lagoon", "earth"]),
        ({"lagoon", "friend"}, ["exile", "frozen", "falcon", "laser", "earth"]),
    ],
)
def test_allocate_hostnames(
    fixed_seed: None, allocated: set[str], expected: list[str]
) -> None:
    """Exercising allocating hostnames."""
    hostnames = allocate_hostnames(allocated, 5, rand=random.Random(1))
    assert hostnames == expected
