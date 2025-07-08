#!/usr/bin/env python3
# coding=utf-8

"""
Exceptions specific to git.
"""

from vt.utils.errors.error_specs.exceptions import VTException, VTExitingException


class GitException(VTException):
    """
    ``VTException`` specific to git.

    Examples:

      * raise exception:

        >>> raise GitException()
        Traceback (most recent call last):
        gitbolt.exceptions.GitException

      * raise exception with a message:

        >>> raise GitException('unexpected.')
        Traceback (most recent call last):
        gitbolt.exceptions.GitException: unexpected.

      * raise exception from another exception:

        >>> raise GitException() from ValueError
        Traceback (most recent call last):
        gitbolt.exceptions.GitException: ValueError

    ... rest examples mimic ``VTException`` examples.
    """

    pass


class GitExitingException(GitException, VTExitingException):
    """
    ``GitException`` that carries an ``exit_code``.
    """

    pass
