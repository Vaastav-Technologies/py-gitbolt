#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces for ``git update-ref`` subcommand with default implementation for subprocess calls.
"""

from abc import abstractmethod
from typing import Protocol, override

from gitbolt.subprocess.constants import UPDATE_REF_CMD


class UpdateRefCLIArgsBuilder(Protocol):
    """
    Interface to facilitate building of cli arguments for ``git update-ref`` subcommand.
    """

    @abstractmethod
    def build(
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
    ) -> list[str]:
        """
        Build the complete list of subcommand arguments to be passed to ``git update-ref``.

        :return: Complete list of subcommand arguments.
        """
        ...


class IndividuallyOverridableURCAB(UpdateRefCLIArgsBuilder):
    """
    Individually Overridable Update Ref CLI Args Builder.
    """

    @override
    def build(
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
    ) -> list[str]:
        """
        Build the full list of arguments to be passed to ``git update-ref``.

        >>> builder = IndividuallyOverridableURCAB()

        Update a ref:

        >>> builder.build("refs/heads/main", "abc")
        ['update-ref', 'refs/heads/main', 'abc']

        Update with old value:

        >>> builder.build("refs/heads/main", "abc", "def")
        ['update-ref', 'refs/heads/main', 'abc', 'def']

        Delete:

        >>> builder.build("refs/heads/main", d=True)
        ['update-ref', '-d', 'refs/heads/main']
        >>> builder.build("refs/heads/main", old_oid="def", d=True)
        ['update-ref', '-d', 'refs/heads/main', 'def']

        Stdin:

        >>> builder.build(stdin=b"create refs/heads/x abc\\n")
        ['update-ref', '--stdin']
        >>> builder.build(stdin=b"create refs/heads/x abc\\0", z=True, batch_updates=True)
        ['update-ref', '--stdin', '-z', '--batch-updates']

        Flags:

        >>> builder.build("HEAD", "abc", m="move head", no_deref=True, create_reflog=True)
        ['update-ref', '-m', 'move head', '--no-deref', '--create-reflog', 'HEAD', 'abc']
        """
        sub_cmd_args = [UPDATE_REF_CMD]
        sub_cmd_args.extend(self.m_arg(m))
        sub_cmd_args.extend(self.no_deref_arg(no_deref))
        sub_cmd_args.extend(self.create_reflog_arg(create_reflog))
        sub_cmd_args.extend(self.stdin_arg(stdin))
        sub_cmd_args.extend(self.z_arg(z))
        sub_cmd_args.extend(self.batch_updates_arg(batch_updates))
        sub_cmd_args.extend(self.d_arg(d))
        sub_cmd_args.extend(self.operand_args(ref, new_oid, old_oid, d=d, stdin=stdin))
        return sub_cmd_args

    def m_arg(self, m: str | None) -> list[str]:
        """
        Return ``-m <reason>`` if a reason is provided.

        >>> IndividuallyOverridableURCAB().m_arg("reason")
        ['-m', 'reason']
        >>> IndividuallyOverridableURCAB().m_arg(None)
        []
        """
        return ["-m", m] if m is not None else []

    def no_deref_arg(self, no_deref: bool | None) -> list[str]:
        """
        Return ``--no-deref`` if requested.

        >>> IndividuallyOverridableURCAB().no_deref_arg(True)
        ['--no-deref']
        >>> IndividuallyOverridableURCAB().no_deref_arg(False)
        []
        """
        return ["--no-deref"] if no_deref else []

    def create_reflog_arg(self, create_reflog: bool | None) -> list[str]:
        """
        Return ``--create-reflog`` if requested.

        >>> IndividuallyOverridableURCAB().create_reflog_arg(True)
        ['--create-reflog']
        >>> IndividuallyOverridableURCAB().create_reflog_arg(False)
        []
        """
        return ["--create-reflog"] if create_reflog else []

    def stdin_arg(self, stdin: bytes | None) -> list[str]:
        """
        Return ``--stdin`` if stdin bytes are provided.

        >>> IndividuallyOverridableURCAB().stdin_arg(b"create refs/heads/x abc\\n")
        ['--stdin']
        >>> IndividuallyOverridableURCAB().stdin_arg(None)
        []
        """
        return ["--stdin"] if stdin is not None else []

    def z_arg(self, z: bool | None) -> list[str]:
        """
        Return ``-z`` if requested.

        >>> IndividuallyOverridableURCAB().z_arg(True)
        ['-z']
        >>> IndividuallyOverridableURCAB().z_arg(False)
        []
        """
        return ["-z"] if z else []

    def batch_updates_arg(self, batch_updates: bool | None) -> list[str]:
        """
        Return ``--batch-updates`` if requested.

        >>> IndividuallyOverridableURCAB().batch_updates_arg(True)
        ['--batch-updates']
        >>> IndividuallyOverridableURCAB().batch_updates_arg(False)
        []
        """
        return ["--batch-updates"] if batch_updates else []

    def d_arg(self, d: bool | None) -> list[str]:
        """
        Return ``-d`` if deleting.

        >>> IndividuallyOverridableURCAB().d_arg(True)
        ['-d']
        >>> IndividuallyOverridableURCAB().d_arg(False)
        []
        """
        return ["-d"] if d else []

    def operand_args(
        self,
        ref: str | None,
        new_oid: str | None,
        old_oid: str | None,
        *,
        d: bool,
        stdin: bytes | None,
    ) -> list[str]:
        """
        Return ref / oid operands. ``--stdin`` takes no operands.

        >>> IndividuallyOverridableURCAB().operand_args("refs/heads/main", "abc", None, d=False, stdin=None)
        ['refs/heads/main', 'abc']
        >>> IndividuallyOverridableURCAB().operand_args("refs/heads/main", None, "def", d=True, stdin=None)
        ['refs/heads/main', 'def']
        >>> IndividuallyOverridableURCAB().operand_args(None, None, None, d=False, stdin=b"x")
        []
        """
        if stdin is not None:
            return []
        args: list[str] = []
        if ref is not None:
            args.append(ref)
        if d:
            if old_oid is not None:
                args.append(old_oid)
            return args
        if new_oid is not None:
            args.append(new_oid)
        if old_oid is not None:
            args.append(old_oid)
        return args
