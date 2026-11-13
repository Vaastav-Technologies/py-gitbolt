#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces specific to ``git replace`` subcommand.
"""

from abc import abstractmethod
from typing import Protocol, override, Literal

from gitbolt._internal_init import errmsg_creator
from gitbolt.exceptions import GitExitingException
from vt.utils.errors.error_specs import ERR_INVALID_USAGE
from vt.utils.errors.error_specs.utils import require_type

REPLACE_FORMATS = ("short", "medium", "long")
ReplaceFormat = Literal["short", "medium", "long"]


class ReplaceArgsValidator(Protocol):
    """
    The argument validator for ``git replace`` subcommand.
    """

    @abstractmethod
    def validate_replace(
        self, object: str, replacement: str, *, force: bool = False
    ) -> None: ...

    @abstractmethod
    def validate_delete(self, object: str, *objects: str) -> None: ...

    @abstractmethod
    def validate_list(
        self, pattern: str | None = None, *, format_: ReplaceFormat | None = None
    ) -> None: ...

    @abstractmethod
    def validate_graft(
        self, commit: str, *parents: str, force: bool = False
    ) -> None: ...

    @abstractmethod
    def validate_convert_graft_file(self, *, force: bool = False) -> None: ...


class UtilReplaceArgsValidator(ReplaceArgsValidator):
    """
    Independent utility to perform ``git replace`` argument validation.

    ``force`` is omitted unless the caller sets it, so Git keeps its default
    (do not overwrite an existing replace ref).
    """

    @override
    def validate_replace(
        self, object: str, replacement: str, *, force: bool = False
    ) -> None:
        """
        >>> UtilReplaceArgsValidator().validate_replace("abc", "def")
        >>> UtilReplaceArgsValidator().validate_replace("abc", "def", force=True)
        >>> UtilReplaceArgsValidator().validate_replace("", "def")
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: 'object' is required
        """
        self._require_non_empty_str(object, "object")
        self._require_non_empty_str(replacement, "replacement")
        require_type(force, "force", bool, GitExitingException)

    @override
    def validate_delete(self, object: str, *objects: str) -> None:
        """
        >>> UtilReplaceArgsValidator().validate_delete("abc")
        >>> UtilReplaceArgsValidator().validate_delete("abc", "def")
        >>> UtilReplaceArgsValidator().validate_delete("")
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: 'object' is required
        """
        self._require_non_empty_str(object, "object")
        for extra in objects:
            self._require_non_empty_str(extra, "object")

    @override
    def validate_list(
        self, pattern: str | None = None, *, format_: ReplaceFormat | None = None
    ) -> None:
        """
        >>> UtilReplaceArgsValidator().validate_list()
        >>> UtilReplaceArgsValidator().validate_list("abc*", format_="medium")
        >>> UtilReplaceArgsValidator().validate_list(format_="wide")
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: Unexpected format_ value. Choose from 'short', 'medium' and 'long'.
        """
        if pattern is not None:
            require_type(pattern, "pattern", str, GitExitingException)
        if format_ is not None:
            if format_ not in REPLACE_FORMATS:
                errmsg = errmsg_creator.errmsg_for_choices(
                    emphasis="format_", choices=list(REPLACE_FORMATS)
                )
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)

    @override
    def validate_graft(
        self, commit: str, *parents: str, force: bool = False
    ) -> None:
        """
        >>> UtilReplaceArgsValidator().validate_graft("abc")
        >>> UtilReplaceArgsValidator().validate_graft("abc", "def", force=True)
        >>> UtilReplaceArgsValidator().validate_graft("")
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: 'commit' is required
        """
        self._require_non_empty_str(commit, "commit")
        for parent in parents:
            self._require_non_empty_str(parent, "parent")
        require_type(force, "force", bool, GitExitingException)

    @override
    def validate_convert_graft_file(self, *, force: bool = False) -> None:
        """
        >>> UtilReplaceArgsValidator().validate_convert_graft_file()
        >>> UtilReplaceArgsValidator().validate_convert_graft_file(force=True)
        """
        require_type(force, "force", bool, GitExitingException)

    def _require_non_empty_str(self, value: str, name: str) -> None:
        require_type(value, name, str, GitExitingException)
        if value == "":
            errmsg = f"'{name}' is required"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
