#!/usr/bin/env python
#
# Tool for allocating a hostname from a list of words and set of existing
# hosts.  The tool prints out a new hostname that should be added to the
# database.

import argparse
import os
import sys

from . import hostdb

# Define command line arguments
parser = argparse.ArgumentParser(description="Allocate a hostname")
parser.add_argument(
    "--num", type=int, default=5, help="Number of hostnames to allocate"
)
parser.add_argument(
    "--terraform_dirs", type=str, nargs="+", help="Hostdb inventory directories"
)

TERRAFORM_DIRS = "TERRAFORM_DIRS"
HOSTDB_DIRS = ["hosts/prod", "hosts/dev"]


def main():
    args = parser.parse_args()
    dirs = []
    if TERRAFORM_DIRS in os.environ:
        dirs = os.environ[TERRAFORM_DIRS].split(",")
    if args.terraform_dirs:
        dirs = args.terraform_dirs
    if not dirs:
        print("Required environment var TERRAFORM_DIRS or --terraform_dirs not set")
        sys.exit(1)

    dbs = [hostdb.HostDb.FromTerraform(path) for path in dirs]
    new_hosts = hostdb.allocate_hostnames(dbs, args.num)
    for host in new_hosts:
        print(host)


if __name__ == "__main__":
    main()
