"""Exceptions for the hostdb package."""


class HostDbException(Exception):
    """Error raised working with the host database."""


class HostDbConfigError(HostDbException):
    """Exception raised for errors in configuration"""
