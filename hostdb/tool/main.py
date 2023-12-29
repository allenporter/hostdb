#!/usr/bin/env python
#
# Tool for allocating a hostname from a list of words and set of existing
# hosts.  The tool prints out a new hostname that should be added to the
# database.

from argparse import (
    ArgumentParser,
    _SubParsersAction as SubParsersAction,
)
import sys
import pathlib
import logging
import traceback
from typing import Any

from hostdb import hostdb, naming
from hostdb.exceptions import HostDbException


class AllocateAction:
    """Allocate a hostname."""

    @classmethod
    def register(
        cls, subparsers: SubParsersAction  # type: ignore[type-arg]
    ) -> ArgumentParser:
        allocate_cmd = subparsers.add_parser(
            "allocate",
            help="Allocate hostnames",
            description="Allocate an unused hostname for use as another machine",
        )
        allocate_cmd.add_argument(
            "--num", type=int, default=5, help="Number of hostnames to allocate"
        )
        allocate_cmd.add_argument(
            "--path",
            type=str,
            required=True,
            help="Hostdb inventory configuration file",
        )
        allocate_cmd.set_defaults(cls=AllocateAction)

    def run(
        self, num: int, path: str, **kwargs: Any  # pylint: disable=unused-argument
    ) -> None:
        """Run the allocate command."""
        db = hostdb.HostDb.from_yaml(pathlib.Path(path))
        new_hosts = naming.allocate_hostnames(db.hostnames, num)
        for host in new_hosts:
            print(host)


class ValidateAction:
    """Validate a hostdb."""

    @classmethod
    def register(
        cls, subparsers: SubParsersAction  # type: ignore[type-arg]
    ) -> ArgumentParser:
        validate_cmd = subparsers.add_parser(
            "validate",
            help="Validate hostdb configuration",
            description="Validate hostdb configuration",
        )
        validate_cmd.add_argument(
            "--path",
            type=str,
            required=True,
            help="Hostdb inventory configuration file",
        )
        validate_cmd.set_defaults(cls=ValidateAction)

    def run(self, path: str, **kwargs: Any) -> None:
        """Run the validate command."""
        db = hostdb.HostDb.from_yaml(pathlib.Path(path))
        hostdb.validate(db)
        print("Success")


# Define command line arguments
def _make_parser() -> ArgumentParser:
    """Return the argument parser."""
    parser = ArgumentParser(description="Allocate a hostname")
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    )
    subparsers = parser.add_subparsers(dest="command", help="Command", required=True)
    AllocateAction.register(subparsers)
    ValidateAction.register(subparsers)

    return parser


def main():
    parser = _make_parser()
    args = parser.parse_args()

    if args.log_level:
        logging.basicConfig(level=args.log_level)

    action = args.cls()
    try:
        action.run(**vars(args))
    except HostDbException as err:
        if args.log_level == "DEBUG":
            traceback.print_exc(file=sys.stderr)
        print("flux-local error: ", err, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
