"""Test for the hostname validation logic."""

import pytest
from hostdb.hostdb import validate_raw, HostDbConfigError


def test_success() -> None:
    hosts = {
        'host1': {
            'ip': '127.0.0.1',
            'mac': '00:aa:bb:cc:dd:ee',
         },
         'host2': {
            'ip': '127.0.0.2',
            'mac': 'bb:aa:bb:cc:dd:ee',
         },
         'host3': {
            'ip': '127.0.0.3',
            'mac': 'ee:aa:bb:cc:dd:ee',
         },
    }
    services = {
        'web01': 'host1',
        'sto01': 'host2',
    }

    validate_raw(hosts, services)

def test_duplicate_ip():
    hosts = {
        'host1': {
            'ip': '127.0.0.1',
            'mac': '00:aa:bb:cc:dd:ee',
        },
        'host2': {
            'ip': '127.0.0.1',
            'mac': 'bb:aa:bb:cc:dd:ee',
        },
        'host3': {
            'ip': '127.0.0.3',
            'mac': 'ee:aa:bb:cc:dd:ee',
        },
    }
    services = {
        'web01': 'host1',
        'sto01': 'host2',
    }

    with pytest.raises(HostDbConfigError):
        validate_raw(hosts, services)

def test_duplicate_mac() -> None:
    hosts = {
        'host1': {
            'ip': '127.0.0.1',
            'mac': '00:aa:bb:cc:dd:ee',
        },
        'host2': {
            'ip': '127.0.0.2',
            'mac': 'ee:aa:bb:cc:dd:ee',
        },
        'host3': {
            'ip': '127.0.0.3',
            'mac': 'ee:aa:bb:cc:dd:ee',
        },
    }
    services = {
        'web01': 'host1',
        'sto01': 'host2',
    }

    with pytest.raises(HostDbConfigError):
        validate_raw(hosts, services)

def test_no_service() -> None:
    hosts = {
        'host1': {
            'ip': '127.0.0.1',
            'mac': '00:aa:bb:cc:dd:ee',
        },
    }
    services = {
        'web01': 'host99',
    }

    with pytest.raises(HostDbConfigError):
        validate_raw(hosts, services)
