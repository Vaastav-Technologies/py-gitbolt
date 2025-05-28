#!/usr/bin/env python3
# coding=utf-8

"""
interfaces related to processors specific to git commands.
"""
from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import Protocol, override, Unpack, Self, overload, Literal

from vt.utils.commons.commons.op import RootDirOp

from vt.vcs.git.gitlib.models import GitOpts


class ForGit(Protocol):
    """
    Marker interface to mark an operation for git.
    """
    pass


class HasGitUnderneath[G: 'Git'](ForGit, Protocol):
    """
    Stores a reference to main git instance.
    """

    @property
    @abstractmethod
    def underlying_git(self) -> G:
        """
        :return: stored git instance reference.
        """
        ...


class CanOverrideGitOpts(ForGit, Protocol):
    """
    Can override main git command options.

    For example, in ``git --no-pager log -1 master`` git command, ``--no-pager`` is the main command arg.
    """

    @abstractmethod
    def git_opts_override(self, **overrides: Unpack[GitOpts]) -> Self:
        """
        Temporarily override options to the main git command before current subcommand runs.

        Get a new ``Git`` object with the git main command options overridden.

        All the parameters mirror options described in the `git documentation <https://git-scm.com/docs/git>`_.

        For example, in ``git --no-pager log -1 master`` git command, ``--no-pager`` is the main command arg.

        :return: instance with overridden git main command args.
        """
        ...


class GitSubCommand(CanOverrideGitOpts, Protocol):
    """
    Interface for git subcommands, such as:

    * ``add``
    * ``commit``
    * ``pull``
    * ...
    etc.
    """

    @abstractmethod
    def clone(self) -> Self:
        """
        :return: a clone of the underlying subcommand.
        """
        ...

    @abstractmethod
    def _subcmd_from_git(self, git: 'Git') -> 'GitSubCommand':
        """
        Protected. Intended for inheritance only.

        :return: specific implementation of subcommand from ``git``.
        """
        ...


class LsTree(GitSubCommand, RootDirOp, Protocol):
    """
    Interface for ``git ls-tree`` command.
    """

    @abstractmethod
    def ls_tree(self, tree_ish: str, *, d: bool = False, r: bool = False, t: bool = False, long: bool = False,
                z: bool = False, name_only: bool = False, object_only: bool = False, full_name: bool = False,
                full_tree: bool = False, abbrev: int | None = None, format_: str | None = None,
                path: list[str] | None = None) -> str:
        """
        All the parameters are mirrors of the parameters of ``git ls-tree`` CLI command
        from `git ls-tree documentation <https://git-scm.com/docs/git-ls-tree>`_.

        :return: ``ls-tree`` output.
        """
        ...

    @override
    def _subcmd_from_git(self, git: 'Git') -> 'LsTree':
        return git.ls_tree_subcmd


class Add(GitSubCommand, RootDirOp, Protocol):
    """
    Interface for ``git add`` command.
    """

    @overload
    @abstractmethod
    def add(
        self,
        *,
        verbose: bool = False,
        dry_run: bool = False,
        force: bool = False,
        interactive: bool = False,
        patch: bool = False,
        edit: bool = False,
        no_all: bool | None = None,
        no_ignore_removal: bool | None = None,
        sparse: bool = False,
        intent_to_add: bool = False,
        refresh: bool = False,
        ignore_errors: bool = False,
        ignore_missing: bool = False,
        renormalize: bool = False,
        chmod: Literal["+x", "-x"] | None = None,
        pathspec_from_file: Path,
        pathspec_file_null: bool = False,
    ) -> str:
        """
        Add files listed in a file (`pathspec_from_file`) to the index.
        `pathspec_file_null` indicates if the file is NUL terminated.
        No explicit pathspec list is allowed in this overload.

        Mirrors the parameters of ``git add`` CLI command
        from `git add documentation <https://git-scm.com/docs/git-add>`_.
        """

    @overload
    @abstractmethod
    def add(
        self,
        *,
        verbose: bool = False,
        dry_run: bool = False,
        force: bool = False,
        interactive: bool = False,
        patch: bool = False,
        edit: bool = False,
        no_all: bool | None = None,
        no_ignore_removal: bool | None = None,
        sparse: bool = False,
        intent_to_add: bool = False,
        refresh: bool = False,
        ignore_errors: bool = False,
        ignore_missing: bool = False,
        renormalize: bool = False,
        chmod: Literal["+x", "-x"] | None = None,
        pathspec: list[str],
    ) -> str:
        """
        Add files specified by a list of pathspec strings.
        `pathspec_from_file` and `pathspec_file_null` are disallowed here.

        Mirrors the parameters of ``git add`` CLI command
        from `git add documentation <https://git-scm.com/docs/git-add>`_.
        """

    @overload
    @abstractmethod
    def add(
        self,
        *,
        verbose: bool = False,
        dry_run: bool = False,
        force: bool = False,
        interactive: bool = False,
        patch: bool = False,
        edit: bool = False,
        no_all: bool | None = None,
        no_ignore_removal: bool | None = None,
        sparse: bool = False,
        intent_to_add: bool = False,
        refresh: bool = False,
        ignore_errors: bool = False,
        ignore_missing: bool = False,
        renormalize: bool = False,
        chmod: Literal["+x", "-x"] | None = None,
        pathspec_from_file: Literal["-"],
        pathspec_stdin: str,
        pathspec_file_null: bool = False,
    ) -> str:
        """
        Add files listed from stdin (when `pathspec_from_file` is '-').
        The `pathspec_stdin` argument is the string content piped to stdin.

        Mirrors the parameters of ``git add`` CLI command
        from `git add documentation <https://git-scm.com/docs/git-add>`_.
        """

    @override
    def _subcmd_from_git(self, git: 'Git') -> 'Add':
        return git.add_subcmd


class Version(GitSubCommand, Protocol):
    """
    Interface for ``git version`` command.
    """

    @abstractmethod
    def version(self, build_options: bool = False) -> str:
        """
        All the parameters are mirrors of the parameters of ``git version`` CLI command
        from `git version documentation <https://git-scm.com/docs/git-version>`_.

        :return: ``version`` output morphed into ``T``.
        """
        ...

    @override
    def _subcmd_from_git(self, git: 'Git') -> 'Version':
        return git.version_subcmd


class Git(ForGit, CanOverrideGitOpts, Protocol):
    """
    Class designed analogous to documentation provided on `git documentation <https://git-scm.com/docs/git>`_.
    """

    @property
    def version(self) -> str:
        """
        :return: current git version.
        """
        return self.version_subcmd.version()

    @property
    @abstractmethod
    def exec_path(self) -> Path:
        """
        :return: Path to wherever your core Git programs are installed.
        """
        ...

    @property
    @abstractmethod
    def html_path(self) -> Path:
        """
        :return: the path, without trailing slash, where Git’s HTML documentation is installed.
        """
        ...

    @property
    @abstractmethod
    def info_path(self) -> Path:
        """
        :return: the path where the Info files documenting this version of Git are installed.
        """
        ...

    @property
    @abstractmethod
    def man_path(self) -> Path:
        """
        :return: the man path (see man(1)) for the man pages for this version of Git.
        """
        ...

    @property
    @abstractmethod
    def version_subcmd(self) -> Version:
        """
        :return: ``git version`` subcommand.
        """
        ...

    @property
    @abstractmethod
    def ls_tree_subcmd(self) -> LsTree:
        """
        :return: ``git ls-tree`` subcommand.
        """
        ...

    @property
    @abstractmethod
    def add_subcmd(self) -> Add:
        """
        :return: ``git add`` subcommand.
        """
        ...

    @abstractmethod
    def clone(self) -> Self:
        """
        :return: a clone of this class.
        """
        ...
