#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces specific to ``git hash-object`` subcommand.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Protocol, override, Literal

from gitbolt._internal_init import errmsg_creator
from gitbolt.exceptions import GitExitingException
from vt.utils.commons.commons.core_py import has_atleast_one_arg
from vt.utils.errors.error_specs import ERR_DATA_FORMAT_ERR, ERR_INVALID_USAGE
from vt.utils.errors.error_specs.utils import require_type, require_iterable

_HASH_OBJECT_TYPES = ("commit", "tree", "blob", "tag")


class HashObjectArgsValidator(Protocol):
    """
    The argument validator for ``git hash-object`` subcommand.
    """

    @abstractmethod
    def validate(
        self,
        file_path: Path | None = None,
        *file_paths: Path,
        t: Literal["commit", "tree", "blob", "tag"] = "blob",
        path: Path | None = None,
        no_filters: bool = False,
        literally: bool = False,
        stdin: bytes | None = None,
        stdin_paths: list[Path] | None = None,
        w: bool = False,
    ) -> None:
        """
        Validate the inputs provided to the ``git hash-object`` command.

        Either a file path or stdin must be present. ``stdin_paths`` counts as stdin
        because Git reads those paths from standard input.

        :raises GitExitingException: When validation fails.
        """
        ...


class UtilHashObjectArgsValidator(HashObjectArgsValidator):
    """
    Independent utility function sort of interface to perform hash_object() arguments validation.
    """

    @override
    def validate(
        self,
        file_path: Path | None = None,
        *file_paths: Path,
        t: Literal["commit", "tree", "blob", "tag"] = "blob",
        path: Path | None = None,
        no_filters: bool = False,
        literally: bool = False,
        stdin: bytes | None = None,
        stdin_paths: list[Path] | None = None,
        w: bool = False,
    ) -> None:
        """
        Validate the inputs provided to the ``git hash-object`` command.

        This includes:

        * Either a file path or stdin must be present. ``stdin_paths`` is stdin.
        * ``file_path`` / extra file paths cannot be combined with ``stdin_paths``.
        * ``stdin`` cannot be combined with ``stdin_paths``.
        * ``path`` cannot be combined with ``no_filters``.
        * ``path`` cannot be combined with ``stdin_paths``.
        * Types for ``Path``, ``list[Path]``, object type literal, bools, and ``bytes``.

        All validations will raise a ``GitExitingException`` with a specific exit code:

        * ``TypeError`` leads to ``ERR_DATA_FORMAT_ERR``.
        * ``ValueError`` leads to ``ERR_INVALID_USAGE``.

        See: `git hash-object documentation <https://git-scm.com/docs/git-hash-object>`_.

        Examples::

            >>> UtilHashObjectArgsValidator().validate(Path("README.md"))
            >>> UtilHashObjectArgsValidator().validate(Path("a.txt"), Path("b.txt"), no_filters=True)
            >>> UtilHashObjectArgsValidator().validate(stdin=b"blob-bytes")
            >>> UtilHashObjectArgsValidator().validate(stdin_paths=[Path("a.txt")])
            >>> UtilHashObjectArgsValidator().validate(Path("a.txt"), path=Path("filters/a.txt"))
            >>> UtilHashObjectArgsValidator().validate(Path("a.txt"), t="commit", literally=True, w=True)

        Invalid Examples::

            >>> UtilHashObjectArgsValidator().validate()
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: Either file_path or stdin is required

            >>> UtilHashObjectArgsValidator().validate(Path("a.txt"), stdin_paths=[Path("b.txt")])
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: file_path and stdin_paths are not allowed together

            >>> UtilHashObjectArgsValidator().validate(stdin=b"x", stdin_paths=[Path("a.txt")])
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: stdin and stdin_paths are not allowed together

            >>> UtilHashObjectArgsValidator().validate(Path("a.txt"), path=Path("p"), no_filters=True)
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: path and no_filters are not allowed together

            >>> UtilHashObjectArgsValidator().validate(path=Path("p"), stdin_paths=[Path("a.txt")])
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: path and stdin_paths are not allowed together

            >>> UtilHashObjectArgsValidator().validate("a.txt")  # type: ignore[arg-type]
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'file_path' must be a pathlib.Path

            >>> UtilHashObjectArgsValidator().validate(Path("a.txt"), t="blobb")  # type: ignore[arg-type]
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: Unexpected t value. Choose from 'commit', 'tree', 'blob' and 'tag'.
        """
        self.mandate_required_arguments(
            file_path,
            *file_paths,
            stdin=stdin,
            stdin_paths=stdin_paths,
        )
        self.validate_exclusive_args(
            file_path,
            *file_paths,
            path=path,
            no_filters=no_filters,
            stdin=stdin,
            stdin_paths=stdin_paths,
        )
        self.validate_types(
            file_path,
            *file_paths,
            t=t,
            path=path,
            no_filters=no_filters,
            literally=literally,
            stdin=stdin,
            stdin_paths=stdin_paths,
            w=w,
        )

    def mandate_required_arguments(
        self,
        file_path: Path | None,
        *file_paths: Path,
        stdin: bytes | None,
        stdin_paths: list[Path] | None,
    ) -> None:
        """
        Either a file path or stdin must be provided. ``stdin_paths`` counts as stdin.

        >>> UtilHashObjectArgsValidator().mandate_required_arguments(Path("a.txt"), stdin=None, stdin_paths=None)
        >>> UtilHashObjectArgsValidator().mandate_required_arguments(None, stdin=b"x", stdin_paths=None)
        >>> UtilHashObjectArgsValidator().mandate_required_arguments(None, stdin=None, stdin_paths=[Path("a.txt")])

        >>> UtilHashObjectArgsValidator().mandate_required_arguments(None, stdin=None, stdin_paths=None)
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: Either file_path or stdin is required
        """
        has_file_path = has_atleast_one_arg(file_path, *file_paths, enforce_type=False)
        has_stdin = stdin is not None or stdin_paths is not None
        if not has_file_path and not has_stdin:
            errmsg = errmsg_creator.at_least_one_required("file_path", "stdin")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    def validate_exclusive_args(
        self,
        file_path: Path | None,
        *file_paths: Path,
        path: Path | None,
        no_filters: bool,
        stdin: bytes | None,
        stdin_paths: list[Path] | None,
    ) -> None:
        """
        Check that exclusive args are not provided together.

        >>> UtilHashObjectArgsValidator().validate_exclusive_args(
        ...     Path("a.txt"), path=None, no_filters=False, stdin=None, stdin_paths=None
        ... )
        >>> UtilHashObjectArgsValidator().validate_exclusive_args(
        ...     Path("a.txt"), stdin_paths=[Path("b.txt")], path=None, no_filters=False, stdin=None
        ... )
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: file_path and stdin_paths are not allowed together
        """
        has_files = has_atleast_one_arg(file_path, *file_paths, enforce_type=False)
        if has_files and stdin_paths is not None:
            errmsg = errmsg_creator.not_allowed_together("file_path", "stdin_paths")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if stdin is not None and stdin_paths is not None:
            errmsg = errmsg_creator.not_allowed_together("stdin", "stdin_paths")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if path is not None and no_filters:
            errmsg = errmsg_creator.not_allowed_together("path", "no_filters")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if path is not None and stdin_paths is not None:
            errmsg = errmsg_creator.not_allowed_together("path", "stdin_paths")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    def validate_types(
        self,
        file_path: Path | None,
        *file_paths: Path,
        t: Literal["commit", "tree", "blob", "tag"],
        path: Path | None,
        no_filters: bool,
        literally: bool,
        stdin: bytes | None,
        stdin_paths: list[Path] | None,
        w: bool,
    ) -> None:
        if file_path is not None:
            self._require_path(file_path, "file_path")
        for extra_path in file_paths:
            self._require_path(extra_path, "file_path")
        if t not in _HASH_OBJECT_TYPES:
            errmsg = errmsg_creator.errmsg_for_choices(
                emphasis="t", choices=list(_HASH_OBJECT_TYPES)
            )
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if path is not None:
            self._require_path(path, "path")
        require_type(no_filters, "no_filters", bool, GitExitingException)
        require_type(literally, "literally", bool, GitExitingException)
        require_type(w, "w", bool, GitExitingException)
        if stdin is not None:
            if not isinstance(stdin, (bytes, bytearray)):
                errmsg = "'stdin' must be bytes"
                raise GitExitingException(
                    errmsg, exit_code=ERR_DATA_FORMAT_ERR
                ) from TypeError(errmsg)
        if stdin_paths is not None:
            require_iterable(stdin_paths, "stdin_paths", Path, list, GitExitingException)

    def _require_path(self, value: Path, name: str) -> None:
        if not isinstance(value, Path):
            errmsg = f"'{name}' must be a pathlib.Path"
            raise GitExitingException(
                errmsg, exit_code=ERR_DATA_FORMAT_ERR
            ) from TypeError(errmsg)
