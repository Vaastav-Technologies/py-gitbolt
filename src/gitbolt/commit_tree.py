#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces specific to ``git commit-tree`` subcommand.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Protocol, override, Literal

from gitbolt._internal_init import errmsg_creator
from gitbolt.exceptions import GitExitingException
from vt.utils.errors.error_specs import ERR_DATA_FORMAT_ERR, ERR_INVALID_USAGE
from vt.utils.errors.error_specs.utils import require_type


class CommitTreeArgsValidator(Protocol):
    """
    The argument validator for ``git commit-tree`` subcommand.
    """

    @abstractmethod
    def validate(
        self,
        tree: str,
        *p: str,
        m: str | list[str] | None = None,
        F: Path | list[Path] | Literal["-"] | None = None,
        stdin: bytes | None = None,
        S: bool | str = False,
        no_gpg_sign: bool = False,
    ) -> None:
        """
        Validate the inputs provided to the ``git commit-tree`` command.

        :raises GitExitingException: When validation fails.
        """
        ...


class UtilCommitTreeArgsValidator(CommitTreeArgsValidator):
    """
    Independent utility to perform ``commit_tree()`` argument validation.
    """

    @override
    def validate(
        self,
        tree: str,
        *p: str,
        m: str | list[str] | None = None,
        F: Path | list[Path] | Literal["-"] | None = None,
        stdin: bytes | None = None,
        S: bool | str = False,
        no_gpg_sign: bool = False,
    ) -> None:
        """
        Validate the inputs provided to the ``git commit-tree`` command.

        This includes:

        * ``tree`` is required.
        * A log message must come from ``m``, ``F``, or ``stdin`` (Git would wait on stdin otherwise).
        * ``stdin`` is required when ``F`` is ``'-'``.
        * ``stdin`` is not allowed with a path ``F``.
        * ``stdin`` is not allowed with ``m`` unless ``F`` is ``'-'``.
        * ``S`` and ``no_gpg_sign`` cannot be combined.
        * Types for ``tree``, parents, ``m``, ``F``, ``stdin``, ``S``, and ``no_gpg_sign``.

        All validations raise ``GitExitingException``:

        * ``TypeError`` leads to ``ERR_DATA_FORMAT_ERR``.
        * ``ValueError`` leads to ``ERR_INVALID_USAGE``.

        See: `git commit-tree documentation <https://git-scm.com/docs/git-commit-tree>`_.

        Examples::

            >>> UtilCommitTreeArgsValidator().validate("abc", m="msg")
            >>> UtilCommitTreeArgsValidator().validate("abc", "parent", m="msg")
            >>> UtilCommitTreeArgsValidator().validate("abc", F=Path("msg.txt"))
            >>> UtilCommitTreeArgsValidator().validate("abc", F="-", stdin=b"msg")
            >>> UtilCommitTreeArgsValidator().validate("abc", stdin=b"msg")
            >>> UtilCommitTreeArgsValidator().validate("abc", m=["a", "b"])

        Invalid Examples::

            >>> UtilCommitTreeArgsValidator().validate("abc")
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: Either m, F or stdin is required

            >>> UtilCommitTreeArgsValidator().validate("abc", F="-", stdin=None)
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: stdin is required when F is '-'

            >>> UtilCommitTreeArgsValidator().validate("abc", F=Path("msg.txt"), stdin=b"x")
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: F and stdin are not allowed together

            >>> UtilCommitTreeArgsValidator().validate("abc", m="msg", stdin=b"x")
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: m and stdin are not allowed together

            >>> UtilCommitTreeArgsValidator().validate("abc", m="msg", S=True, no_gpg_sign=True)
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: S and no_gpg_sign are not allowed together

            >>> UtilCommitTreeArgsValidator().validate(1, m="msg")  # type: ignore[arg-type]
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'tree' must be a string
        """
        self.mandate_required_arguments(tree, m=m, F=F, stdin=stdin)
        self.validate_exclusive_args(m=m, F=F, stdin=stdin, S=S, no_gpg_sign=no_gpg_sign)
        self.validate_types(tree, *p, m=m, F=F, stdin=stdin, S=S, no_gpg_sign=no_gpg_sign)

    def mandate_required_arguments(
        self,
        tree: str,
        *,
        m: str | list[str] | None,
        F: Path | list[Path] | Literal["-"] | None,
        stdin: bytes | None,
    ) -> None:
        if tree is None or (isinstance(tree, str) and tree == ""):
            errmsg = "'tree' is required"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if m is None and F is None and stdin is None:
            errmsg = errmsg_creator.at_least_one_required("m", "F", "stdin")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if F == "-" and stdin is None:
            errmsg = "stdin is required when F is '-'"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    def validate_exclusive_args(
        self,
        *,
        m: str | list[str] | None,
        F: Path | list[Path] | Literal["-"] | None,
        stdin: bytes | None,
        S: bool | str,
        no_gpg_sign: bool,
    ) -> None:
        f_is_path = F is not None and F != "-"
        if f_is_path and stdin is not None:
            errmsg = errmsg_creator.not_allowed_together("F", "stdin")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if m is not None and stdin is not None and F != "-":
            errmsg = errmsg_creator.not_allowed_together("m", "stdin")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if self._s_requested(S) and no_gpg_sign:
            errmsg = errmsg_creator.not_allowed_together("S", "no_gpg_sign")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    def validate_types(
        self,
        tree: str,
        *p: str,
        m: str | list[str] | None,
        F: Path | list[Path] | Literal["-"] | None,
        stdin: bytes | None,
        S: bool | str,
        no_gpg_sign: bool,
    ) -> None:
        require_type(tree, "tree", str, GitExitingException)
        for parent in p:
            require_type(parent, "p", str, GitExitingException)
        if m is not None:
            if isinstance(m, list):
                if not m:
                    errmsg = "'m' must not be empty"
                    raise GitExitingException(
                        errmsg, exit_code=ERR_INVALID_USAGE
                    ) from ValueError(errmsg)
                for msg in m:
                    require_type(msg, "m", str, GitExitingException)
            else:
                require_type(m, "m", str, GitExitingException)
        if F is not None:
            if F == "-":
                pass
            elif isinstance(F, list):
                if not F:
                    errmsg = "'F' must not be empty"
                    raise GitExitingException(
                        errmsg, exit_code=ERR_INVALID_USAGE
                    ) from ValueError(errmsg)
                for file_path in F:
                    self._require_path(file_path, "F")
            else:
                self._require_path(F, "F")
        if stdin is not None:
            if not isinstance(stdin, (bytes, bytearray)):
                errmsg = "'stdin' must be bytes"
                raise GitExitingException(
                    errmsg, exit_code=ERR_DATA_FORMAT_ERR
                ) from TypeError(errmsg)
        if not isinstance(S, (bool, str)):
            errmsg = "'S' must be a bool or str"
            raise GitExitingException(
                errmsg, exit_code=ERR_DATA_FORMAT_ERR
            ) from TypeError(errmsg)
        if isinstance(S, str) and S == "":
            errmsg = "'S' keyid must not be empty"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        require_type(no_gpg_sign, "no_gpg_sign", bool, GitExitingException)

    def _require_path(self, value: Path, name: str) -> None:
        if not isinstance(value, Path):
            errmsg = f"'{name}' must be a pathlib.Path"
            raise GitExitingException(
                errmsg, exit_code=ERR_DATA_FORMAT_ERR
            ) from TypeError(errmsg)

    def _s_requested(self, S: bool | str) -> bool:
        return S is True or isinstance(S, str)
