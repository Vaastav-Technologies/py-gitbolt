#!/usr/bin/env python3
# coding=utf-8

"""
interfaces related to exceptions specific to git.
"""

from vt.utils.errors.error_specs.exceptions import VTException, VTCmdException


class GitException(VTException):
    """
    ``VTException`` specific to git.

    Examples:

      * raise exception:

        >>> raise GitException()
        Traceback (most recent call last):
        gitlib.exceptions.GitException

      * raise exception with a message:

        >>> raise GitException('unexpected.')
        Traceback (most recent call last):
        gitlib.exceptions.GitException: unexpected.

      * raise exception from another exception:

        >>> raise GitException() from ValueError
        Traceback (most recent call last):
        gitlib.exceptions.GitException: ValueError

    ... rest examples mimic ``VTException`` examples.
    """
    pass


class GitCmdException(GitException, VTCmdException):
    """
    A ``GitException`` and also a ``VTCmdException``.

    Examples:

      * raise exception:

        >>> raise GitCmdException
        Traceback (most recent call last):
        gitlib.exceptions.GitCmdException

        >>> raise GitCmdException()
        Traceback (most recent call last):
        gitlib.exceptions.GitCmdException

        >>> raise GitCmdException(exit_code=23)
        Traceback (most recent call last):
        gitlib.exceptions.GitCmdException

      * obtain error code:

        >>> try:
        ...     raise GitCmdException
        ... except GitCmdException as e:
        ...     e.exit_code
        1

        >>> try:
        ...     raise GitCmdException('a message', exit_code=10)
        ... except GitCmdException as e:
        ...     e.exit_code
        10

        >>> try:
        ...     raise GitCmdException('a message', exit_code=15) from ValueError
        ... except GitCmdException as e:
        ...     e.exit_code
        15

        >>> try:
        ...     raise GitCmdException('main message', exit_code=23) from ValueError('cause message.')
        ... except GitCmdException as e:
        ...     e.exit_code
        23

      * raise exception with a message:

        >>> raise GitCmdException('unexpected.')
        Traceback (most recent call last):
        gitlib.exceptions.GitCmdException: unexpected.

      * raise exception from another exception:

        >>> raise GitCmdException() from ValueError
        Traceback (most recent call last):
        gitlib.exceptions.GitCmdException: ValueError

      * raise exception from another exception with message:

        >>> raise GitCmdException() from ValueError('cause message')
        Traceback (most recent call last):
        gitlib.exceptions.GitCmdException: ValueError: cause message

    ... rest examples mimic ``VTCmdException``.
    """
    pass
