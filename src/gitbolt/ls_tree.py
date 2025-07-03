#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces specific to ``git ls-tree`` subcommand.
"""

from abc import abstractmethod
from typing import Protocol, Unpack, override, Literal

from vt.utils.errors.error_specs import ERR_INVALID_USAGE
from vt.utils.errors.error_specs.utils import require_type, require_iterable

from gitbolt.exceptions import GitExitingException
from gitbolt.models import GitLsTreeOpts


class LsTreeArgsValidator(Protocol):
    """
    The argument validator for ``git ls-tree`` subcommand.
    """

    @abstractmethod
    def validate(self, tree_ish: str, **ls_tree_opts: Unpack[GitLsTreeOpts]) -> None:
        """
        Validate arguments passed to the ls-tree() method.

        :param tree_ish: A tree-ish identifier (commit SHA, branch name, etc.).
        :param ls_tree_opts: Keyword arguments mapping to supported options for ``git ls-tree``.
        """
        ...


class UtilLsTreeArgsValidator(LsTreeArgsValidator):
    """
    Independent utility function sort of interface to perform ``ls_tree()`` arguments validation.
    """

    @override
    def validate(self, tree_ish: str, **ls_tree_opts: Unpack[GitLsTreeOpts]) -> None:
        """
        Validate the inputs provided to the ``git ls-tree`` command.

        This utility ensures type safety and logical correctness of arguments
        passed to the ``git ls-tree`` subcommand.

        This includes:
        * Enforcing that ``tree_ish`` is a string.
        * Checking that each supported boolean flag (like ``d``, ``r``, ``z``, etc.)
          is a valid boolean if provided.
        * Validating that ``abbrev`` is an integer between 0 and 40 (inclusive).
        * Ensuring ``format_`` is a string if specified.
        * Checking that ``path`` is a list of strings if specified.

        All validations will raise a ``GitExitingException`` with a specific
        exit code depending on the nature of the failure:

        * ``TypeError`` leads to ``ERR_DATA_FORMAT_ERR``.
        * ``ValueError`` leads to ``ERR_INVALID_USAGE``.

        See: `git ls-tree documentation <https://git-scm.com/docs/git-ls-tree>`_.

        :param tree_ish: A valid Git tree-ish identifier (e.g., branch name, commit hash).
        :param ls_tree_opts: Keyword arguments that map to valid ls-tree options.
        :raises GitExitingException: When validation fails.

        Examples::

            >>> UtilLsTreeArgsValidator().validate("HEAD", d=True, abbrev=10)
            >>> UtilLsTreeArgsValidator().validate("abc123", format_="%(objectname)", path=["src/", "README.md"])
            >>> UtilLsTreeArgsValidator().validate("main", name_only=False, z=True)


        Invalid Examples (will raise GitExitingException), printing these just for doctesting::

            >>> UtilLsTreeArgsValidator().validate(42) # type: ignore[arg-type] # tree_ish expects str and int is provided
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'tree_ish' must be a string

            >>> UtilLsTreeArgsValidator().validate("HEAD", abbrev="abc") # type: ignore[arg-type] # abbrev expects int and str is provided
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'abbrev' must be an int

            >>> UtilLsTreeArgsValidator().validate("HEAD", abbrev=True) # type: ignore[arg-type] # abbrev expects int and bool is provided
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'abbrev' must be an int

            >>> UtilLsTreeArgsValidator().validate("HEAD", abbrev=100)
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: abbrev must be between 0 and 40.

            >>> UtilLsTreeArgsValidator().validate("HEAD",
            ...                       path="src/")  # type: ignore[arg-type] as path expects list[str] and str is provided.
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'path' must be a non-str iterable

            >>> UtilLsTreeArgsValidator().validate("HEAD",
            ...                       path=1)  # type: ignore[arg-type] as path expects list[str] and str is provided.
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'path' must be a non-str iterable

            >>> UtilLsTreeArgsValidator().validate("HEAD",
            ...                         z="yes")  # type: ignore[arg-type] as z expects bool and str is provided.
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'z' must be a boolean
        """
        require_type(tree_ish, "tree_ish", str, GitExitingException)

        bool_keys: list[
            Literal[
                "d",
                "r",
                "t",
                "long",
                "z",
                "name_only",
                "object_only",
                "full_name",
                "full_tree",
                "name_status",
            ]
        ] = [
            "d",
            "r",
            "t",
            "long",
            "z",
            "name_only",
            "object_only",
            "full_name",
            "full_tree",
            "name_status",
        ]

        for key in bool_keys:
            if key in ls_tree_opts:
                the_key = ls_tree_opts[key]
                require_type(the_key, key, bool, GitExitingException)

        if "abbrev" in ls_tree_opts:
            abbrev = ls_tree_opts["abbrev"]
            require_type(abbrev, "abbrev", int, GitExitingException)
            if not (0 <= abbrev <= 40):
                errmsg = "abbrev must be between 0 and 40."
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)

        if "format_" in ls_tree_opts:
            format_ = ls_tree_opts["format_"]
            require_type(format_, "format_", str, GitExitingException)

        if "path" in ls_tree_opts:
            path = ls_tree_opts["path"]
            require_iterable(path, "path", str, list, GitExitingException)
