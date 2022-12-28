#!/usr/bin/python3

import unittest
import hostdb

class TestSum(unittest.TestCase):

  def test_success(self):
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

    hostdb.hostdb.validate_hostdb(hosts, services)

  def test_duplicate_ip(self):
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

    with self.assertRaises(validate_hostdb.ConfigError):
      validate_hostdb.Validate(hosts, services)

  def test_duplicate_mac(self):
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

    with self.assertRaises(validate_hostdb.ConfigError):
      validate_hostdb.Validate(hosts, services)

  def test_no_service(self):
    hosts = {
      'host1': {
        'ip': '127.0.0.1',
        'mac': '00:aa:bb:cc:dd:ee',
      },
    }
    services = {
      'web01': 'host99',
    }

    with self.assertRaises(validate_hostdb.ConfigError):
      validate_hostdb.Validate(hosts, services)


if __name__ == "__main__":
  unittest.main()
