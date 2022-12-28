#!/usr/bin/env python
#
# Tool for allocating a hostname from a list of words and set of existing
# hosts.  The tool prints out a new hostname that should be added to the
# database.

import argparse

from . import hostdb

# Define command line arguments
parser = argparse.ArgumentParser(description="Allocate a hostname")
parser.add_argument(
    "--num", type=int, default=5, help="Number of hostnames to allocate"
)

HOSTDB_DIRS = ["hosts/prod", "hosts/dev"]


def main():
    args = parser.parse_args()
    dbs = [hostdb.HostDb.FromTerraform(path) for path in HOSTDB_DIRS]
    new_hosts = hostdb.allocate_hostnames(dbs, args.num)
    for host in new_hosts:
        print(host)


if __name__ == "__main__":
    main()
