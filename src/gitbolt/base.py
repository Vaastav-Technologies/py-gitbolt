#!/usr/bin/env python3
# coding=utf-8

"""
interfaces related to processors specific to git commands.
"""

from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Protocol, override, Unpack, Self, overload, Literal

from vt.utils.commons.commons.core_py import UNSET, Unset
from vt.utils.commons.commons.op import RootDirOp
from vt.utils.errors.error_specs import ERR_DATA_FORMAT_ERR

from gitbolt.exceptions import GitExitingException
from gitbolt.models import GitOpts, GitAddOpts, GitLsTreeOpts, GitEnvVars
from gitbolt.ls_tree import LsTreeArgsValidator, UtilLsTreeArgsValidator
from gitbolt.add import AddArgsValidator, UtilAddArgsValidator


class HasGitUnderneath[G: "Git"](Protocol):
    """
    Stores a reference to main git instance.
    """

    @property
    @abstractmethod
    def git(self) -> G:
        """
        :return: stored underlying git instance reference.
        """
        ...


class CanOverrideGitOpts(Protocol):
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


class CanOverrideGitEnvs(Protocol):
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

    # TODO: `pathspec: str` -> `pathspec_or_path: str | Path`.
    #  This will make a convenience method for python use.
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

    class VersionInfo:
        @abstractmethod
        def version(self) -> str: ...

        @abstractmethod
        def semver(self) -> tuple: ...

    class VersionWithBuildInfo(VersionInfo):
        @abstractmethod
        def build_options(self) -> dict[str, str]: ...

    @overload
    @abstractmethod
    def version(self) -> VersionInfo: ...

    @overload
    @abstractmethod
    def version(self, build_options: Literal[True]) -> VersionWithBuildInfo: ...

    @abstractmethod
    def version(
        self, build_options: Literal[True, False] = False
    ) -> VersionInfo | VersionWithBuildInfo:
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


class Worktree(GitSubCommand, Protocol):
    """
    Interface for ``git worktree`` subcommand.
    """

    class WorktreeSubcmd(Protocol):
        """
        Interface for the worktree subcommands.
        """

        @property
        @abstractmethod
        def underlying_worktree(self) -> Worktree:
            """
            :return: underlying worktree for this subcommand.
            """
            ...

    # region worktree list subcommands
    class List(WorktreeSubcmd, Protocol):
        """
        Interface for ``git worktree list`` subcommand.
        """

        @abstractmethod
        @overload
        def list(self, *, verbose: bool = False) -> str:
            ...

        @abstractmethod
        @overload
        def list(self, *, porcelain: Literal[False]) -> str:
            ...

        @abstractmethod
        @overload
        def list(self, *, z: bool = False, porcelain: Literal[True]) -> str:
            ...

        @abstractmethod
        def list(self, *, verbose: bool | Unset = UNSET, porcelain: Literal[True, False] | Unset = UNSET,
                 z: bool | Unset = UNSET) -> str:
            """
            List all the worktrees.

            ``git worktree list`` documentation: https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-list

            :param verbose: https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---verbose
            :param porcelain: https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---porcelain
            :param z: This option can only be used if porcelain is enabled. See
                https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt--z for more details.
            :returns: stdout of the command run.
            """
            ...

    @property
    @abstractmethod
    def list_subcmd(self) -> Worktree.List:
        """
        :returns: ``git worktree list`` subcommand.
        """
        ...

    # endregion

    # region worktree lock subcommands
    class Lock(WorktreeSubcmd, Protocol):
        """
        Interface for ``git worktree lock`` subcommand.
        """

        @abstractmethod
        def lock(self, worktree: Path, reason: str | Literal[False] | Unset = UNSET) -> str:
            """
            Lock a worktree to prevent administrative files form being pruned automatically.

            `git worktree lock documentation
            <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-lock>`_.

            :param worktree: Path to the worktree that is to be locked.
            :param reason: `a reason for why a worktree is locked
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-lock>`_.
            :return: git worktree lock output.
            """
            ...

    @property
    @abstractmethod
    def lock_subcmd(self) -> Worktree.Lock:
        """
        :returns: ``git worktree lock`` subcommand.
        """
        ...

    # endregion

    # region worktree unlock subcommands
    class UnLock(WorktreeSubcmd, Protocol):
        """
        Interface for ``git worktree unlock`` subcommand.
        """

        @abstractmethod
        def unlock(self, worktree: Path) -> str:
            """
            Unlock a locked worktree for pruning or deletion.

            `git worktree unlock documentation
            <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-unlock>`_.

            :param worktree: Path to the worktree that is to be unlocked.
            :return: git worktree unlock output.
            """
            ...

    @property
    @abstractmethod
    def unlock_subcmd(self) -> Worktree.Lock:
        """
        :returns: ``git worktree unlock`` subcommand.
        """
        ...

    # endregion

    # region worktree move subcommands
    class Move(WorktreeSubcmd, Protocol):
        """
        Interface for ``git worktree move`` subcommand.
        """

        @abstractmethod
        def move(self, worktree: Path, new_path: Path, *, force: bool | Unset = UNSET, reforce: bool | Unset = UNSET,
                 relative_paths: bool | Unset = UNSET) -> str:
            """
            Move the worktree. Documentation: https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-move

            Also, info on ``git worktree move -h``.

            :param worktree: Path to the worktree that is to be moved.
            :param new_path: Path where the worktree is to be moved.
            :param force: `force move a worktree even when it is locked <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---force>`_.
            :param reforce: multiple force arguments for moving a locked worktree.
            :param relative_paths: `use relative paths for worktree <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---no-relative-paths>`_.
            :return: output of ``git worktree move``.
            """

    @property
    @abstractmethod
    def move_subcmd(self) -> Worktree.Move:
        """
        :returns: ``git worktree move`` subcommand.
        """
        ...

    # endregion

    # region worktree prune subcommands
    class Prune(WorktreeSubcmd, Protocol):
        """
        Interface for ``git worktree prune`` subcommand.

        Documentation: https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-prune
        """

        @abstractmethod
        def prune(self, *, dry_run: bool | Unset = UNSET, verbose: bool | Unset = UNSET,
                  expire: int | datetime | Unset = UNSET) -> str:
            """
            Prune worktrees satisfying pruning conditions.

            :param dry_run: `Just dry run the operation and do not actually prune anything.
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---dry-run>`_.
            :param verbose: `be verbose while pruning
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---verbose>`_.
            :param expire: `prune worktrees older than this expiration time
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---expiretime>`_.
            :returns: prune output in string format.
            """
            ...

    @property
    @abstractmethod
    def prune_subcmd(self) -> Worktree.Prune:
        """
        :returns: ``git worktree prune`` subcommand.
        """
        ...
    # endregion

    # region worktree remove subcommands
    class Remove(WorktreeSubcmd, Protocol):
        """
        Interface for ``git worktree remove`` subcommand.

        Documentation: https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-remove
        """

        @abstractmethod
        def remove(self, worktree: Path, *, force: bool | Unset = UNSET, reforce: bool = False) -> str:
            """
            Remove worktree.

            :param worktree: path of the worktree to remove.
            :param force: `force remove this worktree
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---force>`_.
            :param reforce: unclean but locked worktree needs multiple force arguments for worktree removal.
            :returns: remove output in string format.
            """
            ...

    @property
    @abstractmethod
    def remove_subcmd(self) -> Worktree.Remove:
        """
        :returns: ``git worktree remove`` subcommand.
        """
        ...
    # endregion

    # region worktree repair subcommands
    class Repair(WorktreeSubcmd, Protocol):
        """
        Interface for ``git worktree repair`` subcommand.

        Documentation: https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-repair
        """

        @abstractmethod
        def repair(self, *worktrees: Path, relative_paths: Unset | bool = UNSET) -> str:
            """
            Repair worktree(s).

            :param worktrees: paths of the worktree to repair.
            :param relative_paths: `use relative paths for worktree
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---relative-paths>`_.
            :returns: remove output in string format.
            """
            ...

    @property
    @abstractmethod
    def repair_subcmd(self) -> Worktree.Repair:
        """
        :returns: ``git worktree repair`` subcommand.
        """
        ...
    # endregion

    # region worktree add subcommand
    class Add(WorktreeSubcmd, Protocol):
        """
        Interface for ``git worktree add`` subcommand.

        Documentation: https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-add
        """

        def add(self, worktree: Path, commit_ish: str | None = None, *, force: bool | Unset = UNSET,
                reforce: bool = False, new_branch: str | None = None, new_branch_force: str | None = None,
                orphan: bool | Unset = UNSET, detach: bool | Unset = UNSET, checkout: bool | Unset = UNSET,
                lock: bool | Unset = UNSET, reason: str | Unset = UNSET, quiet: bool | Unset = UNSET,
                track: bool | Unset = UNSET, guess_remote: bool | Unset = UNSET,
                relative_paths: bool | Unset = UNSET) -> str:
            """
            Add worktree.

            :param worktree: path of the worktree to add.
            :param commit_ish: `add a worktree by checking out commit-ish
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-addpathcommit-ish>`_.
            :param force: `force remove this worktree
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---force>`_.
            :param reforce: add a missing but locked worktree path.
            :param new_branch: `add a new branch for worktree.
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-addpathcommit-ish>`_.
            :param new_branch_force: `add a new branch for worktree. Creates a branch at commit_ish even if it
                exists already
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-addpathcommit-ish>`_.
            :param orphan: `orphan unborn branch worktree
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-addpathcommit-ish>`_.
            :param detach: `create a detached worktree
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---detach>`_.
            :param checkout: `checkout the branch in worktree
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---checkout>`_.
            :param lock: `keep the worktree locked after creation
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---lock>`_.
            :param reason: `explanation of why a worktree is locked
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---reasonstring>`_.
            :param quiet: `suppress add feedback messages
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---quiet>`_.
            :param track: `track certain upstream branch
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---track>`_.
            :param guess_remote: `check if a branch already exists on remote that matches this one
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---guess-remote>`_.
            :param relative_paths: `link worktrees using relative paths instead of absolute path (the default)
                <https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt---relative-paths>`_.
            :returns: add output in string format.
            """
            ...


    @property
    @abstractmethod
    def add_subcmd(self) -> Worktree.Add:
        """
        :returns: ``git worktree add`` subcommand.
        """
        ...
    # endregion


class Git(CanOverrideGitOpts, CanOverrideGitEnvs, Protocol):
    """
    Class designed analogous to documentation provided on `git documentation <https://git-scm.com/docs/git>`_.
    """

    def version(self) -> Version.VersionInfo:
        """
        :return: current git version.
        """
        return self.version_subcmd.version()

    @abstractmethod
    def exec_path(self) -> Path:
        """
        :return: Path to wherever your core Git programs are installed.
        """
        ...

    @abstractmethod
    def html_path(self) -> Path:
        """
        :return: the path, without trailing slash, where Git’s HTML documentation is installed.
        """
        ...

    @abstractmethod
    def info_path(self) -> Path:
        """
        :return: the path where the Info files documenting this version of Git are installed.
        """
        ...

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

    @property
    @abstractmethod
    def worktree_subcmd(self) -> Worktree:
        """
        :return: ``git worktree`` subcommand.
        """
        ...

    @abstractmethod
    def clone(self) -> Self:
        """
        :return: a clone of this class.
        """
        ...
