"""Verifies the hostdb is correct to find any common mistakes or misconfigurations."""

import argparse

from . import hostdb

# Define command line arguments
parser = argparse.ArgumentParser(description="Allocate a hostname")
parser.add_argument("hostdb_dir", help="Host database config directory")


def main():
    args = parser.parse_args()
    db = hostdb.HostDb.FromTerraform(args.hostdb_dir)
    hostdb.validate(db)
    print("Success")


if __name__ == "__main__":
    main()
