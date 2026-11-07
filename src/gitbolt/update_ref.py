#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces specific to ``git update-ref`` subcommand.
"""

from abc import abstractmethod
from typing import Protocol, override, Literal

from gitbolt._internal_init import errmsg_creator
from gitbolt.exceptions import GitExitingException
from vt.utils.errors.error_specs import ERR_DATA_FORMAT_ERR, ERR_INVALID_USAGE
from vt.utils.errors.error_specs.utils import require_type


class UpdateRefArgsValidator(Protocol):
    """
    The argument validator for ``git update-ref`` subcommand.
    """

    @abstractmethod
    def validate(
        self,
        ref: str | None = None,
        new_oid: str | None = None,
        old_oid: str | None = None,
        *,
        d: bool = False,
        m: str | None = None,
        no_deref: bool = False,
        create_reflog: bool = False,
        stdin: bytes | None = None,
        z: bool = False,
        batch_updates: bool = False,
    ) -> None:
        """
        Validate the inputs provided to the ``git update-ref`` command.

        :raises GitExitingException: When validation fails.
        """
        ...


class UtilUpdateRefArgsValidator(UpdateRefArgsValidator):
    """
    Independent utility to perform ``update_ref()`` argument validation.
    """

    @override
    def validate(
        self,
        ref: str | None = None,
        new_oid: str | None = None,
        old_oid: str | None = None,
        *,
        d: bool = False,
        m: str | None = None,
        no_deref: bool = False,
        create_reflog: bool = False,
        stdin: bytes | None = None,
        z: bool = False,
        batch_updates: bool = False,
    ) -> None:
        """
        Validate the inputs provided to the ``git update-ref`` command.

        This includes:

        * One of ``stdin``, delete (``d``), or ``ref`` + ``new_oid`` is required.
        * ``stdin`` cannot be combined with ``ref``, ``new_oid``, ``old_oid``, ``d``, or ``create_reflog``.
        * ``d`` cannot be combined with ``new_oid`` or ``create_reflog``.
        * ``z`` and ``batch_updates`` require ``stdin``.

        See: `git update-ref documentation <https://git-scm.com/docs/git-update-ref>`_.

        Examples::

            >>> UtilUpdateRefArgsValidator().validate("refs/heads/main", "abc")
            >>> UtilUpdateRefArgsValidator().validate("refs/heads/main", "abc", "def")
            >>> UtilUpdateRefArgsValidator().validate("refs/heads/main", d=True)
            >>> UtilUpdateRefArgsValidator().validate("refs/heads/main", old_oid="def", d=True)
            >>> UtilUpdateRefArgsValidator().validate(stdin=b"create refs/heads/x abc\\n")
            >>> UtilUpdateRefArgsValidator().validate(stdin=b"create refs/heads/x abc\\0", z=True)

        Invalid Examples::

            >>> UtilUpdateRefArgsValidator().validate()
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: Either ref or stdin is required

            >>> UtilUpdateRefArgsValidator().validate("refs/heads/main")
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: new_oid is required when not deleting

            >>> UtilUpdateRefArgsValidator().validate("refs/heads/main", "abc", d=True)
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: d and new_oid are not allowed together

            >>> UtilUpdateRefArgsValidator().validate("refs/heads/main", stdin=b"x")
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: ref and stdin are not allowed together

            >>> UtilUpdateRefArgsValidator().validate(z=True)
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: z requires stdin

            >>> UtilUpdateRefArgsValidator().validate(1, "abc")  # type: ignore[arg-type]
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'ref' must be a string
        """
        self.mandate_required_arguments(
            ref, new_oid, d=d, stdin=stdin, z=z, batch_updates=batch_updates
        )
        self.validate_exclusive_args(
            ref,
            new_oid,
            old_oid,
            d=d,
            create_reflog=create_reflog,
            stdin=stdin,
            z=z,
            batch_updates=batch_updates,
        )
        self.validate_types(
            ref,
            new_oid,
            old_oid,
            d=d,
            m=m,
            no_deref=no_deref,
            create_reflog=create_reflog,
            stdin=stdin,
            z=z,
            batch_updates=batch_updates,
        )

    def mandate_required_arguments(
        self,
        ref: str | None,
        new_oid: str | None,
        *,
        d: bool,
        stdin: bytes | None,
        z: bool,
        batch_updates: bool,
    ) -> None:
        if stdin is not None:
            return
        if z:
            errmsg = "z requires stdin"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if batch_updates:
            errmsg = "batch_updates requires stdin"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if ref is None or ref == "":
            errmsg = errmsg_creator.at_least_one_required("ref", "stdin")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if not d and (new_oid is None or new_oid == ""):
            errmsg = "new_oid is required when not deleting"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    def validate_exclusive_args(
        self,
        ref: str | None,
        new_oid: str | None,
        old_oid: str | None,
        *,
        d: bool,
        create_reflog: bool,
        stdin: bytes | None,
        z: bool,
        batch_updates: bool,
    ) -> None:
        if stdin is not None:
            if ref is not None:
                errmsg = errmsg_creator.not_allowed_together("ref", "stdin")
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
            if new_oid is not None:
                errmsg = errmsg_creator.not_allowed_together("new_oid", "stdin")
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
            if old_oid is not None:
                errmsg = errmsg_creator.not_allowed_together("old_oid", "stdin")
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
            if d:
                errmsg = errmsg_creator.not_allowed_together("d", "stdin")
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
            if create_reflog:
                errmsg = errmsg_creator.not_allowed_together("create_reflog", "stdin")
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
        else:
            if z:
                errmsg = "z requires stdin"
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
            if batch_updates:
                errmsg = "batch_updates requires stdin"
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
            if d and new_oid is not None:
                errmsg = errmsg_creator.not_allowed_together("d", "new_oid")
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
            if d and create_reflog:
                errmsg = errmsg_creator.not_allowed_together("d", "create_reflog")
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)

    def validate_types(
        self,
        ref: str | None,
        new_oid: str | None,
        old_oid: str | None,
        *,
        d: bool,
        m: str | None,
        no_deref: bool,
        create_reflog: bool,
        stdin: bytes | None,
        z: bool,
        batch_updates: bool,
    ) -> None:
        if ref is not None:
            require_type(ref, "ref", str, GitExitingException)
        if new_oid is not None:
            require_type(new_oid, "new_oid", str, GitExitingException)
        if old_oid is not None:
            require_type(old_oid, "old_oid", str, GitExitingException)
        if m is not None:
            require_type(m, "m", str, GitExitingException)
        require_type(d, "d", bool, GitExitingException)
        require_type(no_deref, "no_deref", bool, GitExitingException)
        require_type(create_reflog, "create_reflog", bool, GitExitingException)
        require_type(z, "z", bool, GitExitingException)
        require_type(batch_updates, "batch_updates", bool, GitExitingException)
        if stdin is not None:
            if not isinstance(stdin, (bytes, bytearray)):
                errmsg = "'stdin' must be bytes"
                raise GitExitingException(
                    errmsg, exit_code=ERR_DATA_FORMAT_ERR
                ) from TypeError(errmsg)
