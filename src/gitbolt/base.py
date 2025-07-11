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
from vt.utils.errors.error_specs import ERR_DATA_FORMAT_ERR

from gitbolt.exceptions import GitExitingException
from gitbolt.models import GitOpts, GitAddOpts, GitLsTreeOpts, GitEnvVars
from gitbolt.ls_tree import LsTreeArgsValidator, UtilLsTreeArgsValidator
from gitbolt.add import AddArgsValidator, UtilAddArgsValidator


class ForGit(Protocol):
    """
    Marker interface to mark an operation for git.
    """

    pass


class HasGitUnderneath[G: "Git"](ForGit, Protocol):
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


class CanOverrideGitEnvs(ForGit, Protocol):
    """
    Can override main git command environment variables.

    For example, in ``GIT_COMMITTER_NAME=vt git --no-pager commit -m "a message"`` git command,
    ``GIT_COMMITTER_NAME=ss``, particularly ``GIT_COMMITTER_NAME`` is the git environment variable.
    """

    @abstractmethod
    def git_envs_override(self, **overrides: Unpack[GitEnvVars]) -> Self:
        """
        Temporarily override environment variables supplied to the git command before current subcommand runs.

        Get a new ``Git`` object with the git environment variables overridden.

        All the environment variables mirror envs described in the `git documentation <https://git-scm.com/docs/git#_environment_variables>`_.

        For example, in ``GIT_COMMITTER_NAME=vt git --no-pager commit -m "a message"`` git command,
        ``GIT_COMMITTER_NAME=vt``, particularly ``GIT_COMMITTER_NAME`` is the git environment variable.

        :return: instance with overridden git environment variables.
        """
        ...


class GitSubCommand(CanOverrideGitOpts, CanOverrideGitEnvs, Protocol):
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
    def _subcmd_from_git(self, git: "Git") -> Self:
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
    def ls_tree(self, tree_ish: str, **ls_tree_opts: Unpack[GitLsTreeOpts]) -> str:
        """
        All the parameters are mirrors of the parameters of ``git ls-tree`` CLI command
        from `git ls-tree documentation <https://git-scm.com/docs/git-ls-tree>`_.

        :param tree_ish: A tree-ish identifier (commit SHA, branch name, etc.).
        :param ls_tree_opts: Keyword arguments mapping to supported options for ``git ls-tree``.
        :return: ``ls-tree`` output.
        """
        ...

    @override
    def _subcmd_from_git(self, git: "Git") -> "LsTree":
        return git.ls_tree_subcmd

    @property
    def args_validator(self) -> LsTreeArgsValidator:
        """
        The argument validator for ``git ls-tree`` subcommand.

        :return: a validator for ls_tree subcommand arguments.
        """
        return UtilLsTreeArgsValidator()


class Add(GitSubCommand, RootDirOp, Protocol):
    """
    Interface for ``git add`` command.
    """

    @overload
    @abstractmethod
    def add(
        self, pathspec: str, *pathspecs: str, **add_opts: Unpack[GitAddOpts]
    ) -> str:
        """
        Add files specified by a list of pathspec strings.
        `pathspec_from_file` and `pathspec_file_null` are disallowed here.

        Mirrors the parameters of ``git add`` CLI command
        from `git add documentation <https://git-scm.com/docs/git-add>`_.

        :return: output of ``git add``.
        """

    @overload
    @abstractmethod
    def add(
        self,
        *,
        pathspec_from_file: Path,
        pathspec_file_nul: bool = False,
        **add_opts: Unpack[GitAddOpts],
    ) -> str:
        """
        Add files listed in a file (`pathspec_from_file`) to the index.
        `pathspec_file_null` indicates if the file is NUL terminated.
        No explicit pathspec list is allowed in this overload.

        Mirrors the parameters of ``git add`` CLI command
        from `git add documentation <https://git-scm.com/docs/git-add>`_.

        :return: output of ``git add``.
        """

    @overload
    @abstractmethod
    def add(
        self,
        *,
        pathspec_from_file: Literal["-"],
        pathspec_stdin: str,
        pathspec_file_nul: bool = False,
        **add_opts: Unpack[GitAddOpts],
    ) -> str:
        """
        Add files listed from stdin (when `pathspec_from_file` is '-').
        The `pathspec_stdin` argument is the string content piped to stdin.

        Mirrors the parameters of ``git add`` CLI command
        from `git add documentation <https://git-scm.com/docs/git-add>`_.

        :return: output of ``git add``.
        """

    @property
    def args_validator(self) -> AddArgsValidator:
        """
        The argument validator for ``git add`` subcommand.

        :return: a validator for add subcommand arguments.
        """
        return UtilAddArgsValidator()

    @override
    def _subcmd_from_git(self, git: "Git") -> "Add":
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

        :return: ``version`` output.
        """
        ...

    @staticmethod
    def _require_valid_args(build_options: bool = False) -> None:
        """
        Require that arguments sent to the version command is valid.

        Examples:

        Correct:

        >>> Version._require_valid_args()

        Error:

        >>> Version._require_valid_args(1) # type: ignore[arg-type] # required bool, supplied int
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: build_options should be bool.

        :param build_options: argument to be validated.
        :raise GitExitingException: if supplied ``build_options`` is invalid.
        """
        if not isinstance(build_options, bool):
            errmsg = "build_options should be bool."
            raise GitExitingException(
                errmsg, exit_code=ERR_DATA_FORMAT_ERR
            ) from TypeError(errmsg)

    @override
    def _subcmd_from_git(self, git: "Git") -> "Version":
        return git.version_subcmd


class Git(CanOverrideGitOpts, CanOverrideGitEnvs, Protocol):
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
