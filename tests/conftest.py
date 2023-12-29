"""Test fixtures."""

import random

import pytest


@pytest.fixture
def fixed_seed() -> None:
    """Fixture to apply a fixed seed."""
    random.seed(0)
