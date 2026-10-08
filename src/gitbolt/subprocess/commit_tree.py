#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces for ``git commit-tree`` subcommand with default implementation for subprocess calls.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Protocol, override, Literal

from gitbolt.subprocess.constants import COMMIT_TREE_CMD


class CommitTreeCLIArgsBuilder(Protocol):
    """
    Interface to facilitate building of cli arguments for ``git commit-tree`` subcommand.
    """

    @abstractmethod
    def build(
        self,
        tree: str,
        *p: str,
        m: str | list[str] | None = None,
        F: Path | list[Path] | Literal["-"] | None = None,
        S: bool | str = False,
        no_gpg_sign: bool = False,
    ) -> list[str]:
        """
        Build the complete list of subcommand arguments to be passed to ``git commit-tree``.

        :return: Complete list of subcommand arguments.
        """
        ...


class IndividuallyOverridableCTCAB(CommitTreeCLIArgsBuilder):
    """
    Individually Overridable Commit Tree CLI Args Builder.

    Build CLI args to run ``git commit-tree`` in a subprocess. Each arg former can be overridden.
    """

    @override
    def build(
        self,
        tree: str,
        *p: str,
        m: str | list[str] | None = None,
        F: Path | list[Path] | Literal["-"] | None = None,
        S: bool | str = False,
        no_gpg_sign: bool = False,
    ) -> list[str]:
        """
        Build the full list of arguments to be passed to ``git commit-tree``.

        >>> builder = IndividuallyOverridableCTCAB()

        Tree and message:

        >>> builder.build("abc", m="msg")
        ['commit-tree', 'abc', '-m', 'msg']

        Parents:

        >>> builder.build("abc", "p1", "p2", m="msg")
        ['commit-tree', 'abc', '-p', 'p1', '-p', 'p2', '-m', 'msg']

        Message file:

        >>> _msg = Path("msg.txt")
        >>> builder.build("abc", F=_msg) == ["commit-tree", "abc", "-F", str(_msg)]
        True

        Stdin via ``-F -``:

        >>> builder.build("abc", F="-")
        ['commit-tree', 'abc', '-F', '-']

        GPG sign:

        >>> builder.build("abc", m="msg", S=True)
        ['commit-tree', 'abc', '-S', '-m', 'msg']
        >>> builder.build("abc", m="msg", S="ABC123")
        ['commit-tree', 'abc', '-SABC123', '-m', 'msg']
        >>> builder.build("abc", m="msg", no_gpg_sign=True)
        ['commit-tree', 'abc', '--no-gpg-sign', '-m', 'msg']

        Multiple ``-m``:

        >>> builder.build("abc", m=["a", "b"])
        ['commit-tree', 'abc', '-m', 'a', '-m', 'b']
        """
        sub_cmd_args = [COMMIT_TREE_CMD]
        sub_cmd_args.append(tree)
        sub_cmd_args.extend(self.parent_args(*p))
        sub_cmd_args.extend(self.s_arg(S))
        sub_cmd_args.extend(self.no_gpg_sign_arg(no_gpg_sign))
        sub_cmd_args.extend(self.m_args(m))
        sub_cmd_args.extend(self.F_args(F))
        return sub_cmd_args

    def parent_args(self, *p: str) -> list[str]:
        """
        Return ``-p <parent>`` for each parent.

        >>> IndividuallyOverridableCTCAB().parent_args("p1", "p2")
        ['-p', 'p1', '-p', 'p2']
        >>> IndividuallyOverridableCTCAB().parent_args()
        []
        """
        args: list[str] = []
        for parent in p:
            args.extend(["-p", parent])
        return args

    def s_arg(self, S: bool | str) -> list[str]:
        """
        Return ``-S`` or ``-S<keyid>``.

        >>> IndividuallyOverridableCTCAB().s_arg(True)
        ['-S']
        >>> IndividuallyOverridableCTCAB().s_arg("KEY")
        ['-SKEY']
        >>> IndividuallyOverridableCTCAB().s_arg(False)
        []
        """
        if S is True:
            return ["-S"]
        if isinstance(S, str):
            return [f"-S{S}"]
        return []

    def no_gpg_sign_arg(self, no_gpg_sign: bool | None) -> list[str]:
        """
        Return ``--no-gpg-sign`` if requested.

        >>> IndividuallyOverridableCTCAB().no_gpg_sign_arg(True)
        ['--no-gpg-sign']
        >>> IndividuallyOverridableCTCAB().no_gpg_sign_arg(False)
        []
        """
        return ["--no-gpg-sign"] if no_gpg_sign else []

    def m_args(self, m: str | list[str] | None) -> list[str]:
        """
        Return ``-m <message>`` for each paragraph.

        >>> IndividuallyOverridableCTCAB().m_args("msg")
        ['-m', 'msg']
        >>> IndividuallyOverridableCTCAB().m_args(["a", "b"])
        ['-m', 'a', '-m', 'b']
        >>> IndividuallyOverridableCTCAB().m_args(None)
        []
        """
        if m is None:
            return []
        messages = m if isinstance(m, list) else [m]
        args: list[str] = []
        for msg in messages:
            args.extend(["-m", msg])
        return args

    def F_args(self, F: Path | list[Path] | Literal["-"] | None) -> list[str]:
        """
        Return ``-F <file>`` for each file, or ``-F -``.

        >>> IndividuallyOverridableCTCAB().F_args("-")
        ['-F', '-']
        >>> _msg = Path("msg.txt")
        >>> IndividuallyOverridableCTCAB().F_args(_msg) == ["-F", str(_msg)]
        True
        >>> IndividuallyOverridableCTCAB().F_args(None)
        []
        """
        if F is None:
            return []
        if F == "-":
            return ["-F", "-"]
        files = F if isinstance(F, list) else [F]
        args: list[str] = []
        for file_path in files:
            args.extend(["-F", str(file_path)])
        return args
