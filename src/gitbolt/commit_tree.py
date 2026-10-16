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

CommitTreeLogPart = tuple[Literal["m"], str] | tuple[Literal["F"], Path | Literal["-"]]
"""One ``-m`` / ``-F`` paragraph, in the order Git should apply them."""


def log_has_f_dash(log: list[CommitTreeLogPart] | None) -> bool:
    """True when ``log`` contains ``('F', '-')`` (``-F -``)."""
    if log is None:
        return False
    return any(kind == "F" and value == "-" for kind, value in log)


def log_has_f_path(log: list[CommitTreeLogPart] | None) -> bool:
    """True when ``log`` contains a path ``-F`` (not ``-``)."""
    if log is None:
        return False
    return any(kind == "F" and value != "-" for kind, value in log)


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
        log: list[CommitTreeLogPart] | None = None,
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
        log: list[CommitTreeLogPart] | None = None,
        stdin: bytes | None = None,
        S: bool | str = False,
        no_gpg_sign: bool = False,
    ) -> None:
        """
        Validate the inputs provided to the ``git commit-tree`` command.

        This includes:

        * ``tree`` is required.
        * A log message must come from ``m``, ``F``, ``log``, or ``stdin`` (Git would wait on stdin otherwise).
        * ``log`` is an ordered list of ``('m', text)`` / ``('F', path_or_dash)`` so ``-m`` and ``-F``
          can be given any number of times, in any order.
        * ``log`` cannot be combined with ``m`` or ``F``.
        * ``stdin`` is required when ``F`` is ``'-'`` or ``log`` contains ``('F', '-')``.
        * ``stdin`` is not allowed with a path ``F``.
        * ``stdin`` is not allowed with ``m`` unless ``F`` is ``'-'``.
        * ``S`` and ``no_gpg_sign`` cannot be combined.
        * Types for ``tree``, parents, ``m``, ``F``, ``log``, ``stdin``, ``S``, and ``no_gpg_sign``.

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
            >>> UtilCommitTreeArgsValidator().validate(
            ...     "abc", log=[("m", "a"), ("F", Path("b.txt")), ("m", "c")]
            ... )
            >>> UtilCommitTreeArgsValidator().validate("abc", log=[("F", "-")], stdin=b"msg")

        Invalid Examples::

            >>> UtilCommitTreeArgsValidator().validate("abc")
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: Either m, F, log or stdin is required

            >>> UtilCommitTreeArgsValidator().validate("abc", F="-", stdin=None)
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: stdin is required when F is '-'

            >>> UtilCommitTreeArgsValidator().validate("abc", F=Path("msg.txt"), stdin=b"x")
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: F and stdin are not allowed together

            >>> UtilCommitTreeArgsValidator().validate("abc", m="msg", stdin=b"x")
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: m and stdin are not allowed together

            >>> UtilCommitTreeArgsValidator().validate("abc", m="msg", log=[("m", "x")])
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: m and log are not allowed together

            >>> UtilCommitTreeArgsValidator().validate("abc", m="msg", S=True, no_gpg_sign=True)
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: S and no_gpg_sign are not allowed together

            >>> UtilCommitTreeArgsValidator().validate(1, m="msg")  # type: ignore[arg-type]
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'tree' must be a string
        """
        self.mandate_required_arguments(tree, m=m, F=F, log=log, stdin=stdin)
        self.validate_exclusive_args(
            m=m, F=F, log=log, stdin=stdin, S=S, no_gpg_sign=no_gpg_sign
        )
        self.validate_types(
            tree, *p, m=m, F=F, log=log, stdin=stdin, S=S, no_gpg_sign=no_gpg_sign
        )

    def mandate_required_arguments(
        self,
        tree: str,
        *,
        m: str | list[str] | None,
        F: Path | list[Path] | Literal["-"] | None,
        log: list[CommitTreeLogPart] | None,
        stdin: bytes | None,
    ) -> None:
        if tree is None or (isinstance(tree, str) and tree == ""):
            errmsg = "'tree' is required"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if m is None and F is None and log is None and stdin is None:
            errmsg = errmsg_creator.at_least_one_required("m", "F", "log", "stdin")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if (F == "-" or log_has_f_dash(log)) and stdin is None:
            errmsg = "stdin is required when F is '-'"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    def validate_exclusive_args(
        self,
        *,
        m: str | list[str] | None,
        F: Path | list[Path] | Literal["-"] | None,
        log: list[CommitTreeLogPart] | None,
        stdin: bytes | None,
        S: bool | str,
        no_gpg_sign: bool,
    ) -> None:
        if log is not None and m is not None:
            errmsg = errmsg_creator.not_allowed_together("m", "log")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if log is not None and F is not None:
            errmsg = errmsg_creator.not_allowed_together("F", "log")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        f_is_path = (F is not None and F != "-") or log_has_f_path(log)
        uses_f_dash = F == "-" or log_has_f_dash(log)
        if f_is_path and stdin is not None:
            errmsg = errmsg_creator.not_allowed_together("F", "stdin")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if m is not None and stdin is not None and not uses_f_dash:
            errmsg = errmsg_creator.not_allowed_together("m", "stdin")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if log is not None and stdin is not None and not uses_f_dash:
            errmsg = errmsg_creator.not_allowed_together("log", "stdin")
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
        log: list[CommitTreeLogPart] | None,
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
        if log is not None:
            if not isinstance(log, list):
                errmsg = "'log' must be a list"
                raise GitExitingException(
                    errmsg, exit_code=ERR_DATA_FORMAT_ERR
                ) from TypeError(errmsg)
            if not log:
                errmsg = "'log' must not be empty"
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
            for part in log:
                if not isinstance(part, tuple) or len(part) != 2:
                    errmsg = "'log' items must be ('m', str) or ('F', Path | '-')"
                    raise GitExitingException(
                        errmsg, exit_code=ERR_DATA_FORMAT_ERR
                    ) from TypeError(errmsg)
                kind, value = part
                if kind == "m":
                    if not isinstance(value, str):
                        errmsg = "'log m' must be a string"
                        raise GitExitingException(
                            errmsg, exit_code=ERR_DATA_FORMAT_ERR
                        ) from TypeError(errmsg)
                elif kind == "F":
                    if value != "-" and not isinstance(value, Path):
                        errmsg = "'log F' must be a pathlib.Path"
                        raise GitExitingException(
                            errmsg, exit_code=ERR_DATA_FORMAT_ERR
                        ) from TypeError(errmsg)
                else:
                    errmsg = "'log' kind must be 'm' or 'F'"
                    raise GitExitingException(
                        errmsg, exit_code=ERR_INVALID_USAGE
                    ) from ValueError(errmsg)
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
