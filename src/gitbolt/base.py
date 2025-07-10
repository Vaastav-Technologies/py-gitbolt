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


class Branch(GitSubCommand, Protocol):
    """
    Interface for ``git branch`` subcommand.
    """

    @abstractmethod
    def create_branch(
        self,
        branch_name: str,
        start_point: str | None = None,
        *,
        force: bool | None = None,
        track: bool | None = None,
        recurse_submodules: bool | None = None,
    ) -> str:
        """
        Create a new Git branch.

        Equivalent to ``git branch <branch_name> [<start_point>]`` with additional options.

        :param branch_name:
            Name of the new branch to create.

        :param start_point:
            Optional starting point (commit, tag, branch, etc.). Defaults to HEAD.

        :param force:
            **Tri-state.**
            - If True, emits ``--force`` or ``-f`` to allow overwriting an existing branch.
            - If False, emits ``--no-force`` to explicitly avoid forced creation.
            - If None, the option is not passed.

        :param track:
            **Tri-state.**
            - If True, sets up the new branch to track a remote branch.
            - If False, emits ``--no-track`` to disable tracking explicitly.
            - If None, leaves tracking behavior to Git defaults.

        :param recurse_submodules:
            **Tri-state.**
            - If True, emits ``--recurse-submodules`` to apply the branch operation recursively into submodules.
            - If False, emits ``--no-recurse-submodules``.
            - If None, submodule behavior is not specified.

        :return: Output of ``git branch``.

        See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt---create
        """
        ...

    @abstractmethod
    def set_upstream(
        self, branch_name: str | None = None, *, set_upstream_to: str | Literal[False]
    ) -> str:
        """
        Set the upstream branch for a local branch.

        Equivalent to ``git branch --set-upstream-to=<branch> [<branch_name>]``.

        :param branch_name:
            Local branch to configure. Defaults to the current branch if not specified.

        :param set_upstream_to:
            Target upstream branch.
            Use a remote-tracking branch name (e.g. origin/main).

            - If given a string, sets the upstream to that branch (emits ``--set-upstream-to=<branch>``).
            - If set to ``False``, emits ``--no-set-upstream``.

        :return: Output of ``git branch``.

        See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt---set-upstream-to
        """
        ...

    @abstractmethod
    def unset_upstream(
        self, branch_name: str | None = None, *, unset_upstream_: bool = True
    ) -> str:
        """
        Unset the upstream branch for a local branch.

        Equivalent to ``git branch --unset-upstream [<branch_name>]``.

        :param branch_name:
            Local branch whose upstream configuration should be removed. Defaults to the current branch.

        :param unset_upstream_:
            **Bi-state.**
            - If True (default), emits ``--unset-upstream``.
            - If False, emits ``--no-unset-upstream``.

        :return: Output of ``git branch``.

        See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt---unset-upstream
        """
        ...

    @abstractmethod
    def rename_branch(
        self,
        new_branch: str,
        old_branch: str | None = None,
        *,
        force: bool | None = None,
    ) -> str:
        """
        Rename an existing branch.

        Equivalent to ``git branch -m|-M [<old_branch>] <new_branch>``.

        :param new_branch:
            The new name for the branch.

        :param old_branch:
            The current name of the branch to rename. If None, renames the current branch.

        :param force:
            **Tri-state.**
            - If True, performs forced rename using ``-M``.
            - If False, uses ``-m`` for safe rename.
            - If None, defers to Git’s default behavior.

        :return: Output of ``git branch``.

        See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt--m
        """
        ...

    @abstractmethod
    def copy_branch(
        self,
        new_branch: str,
        old_branch: str | None = None,
        *,
        force: bool | None = None,
    ) -> str:
        """
        Create a copy of an existing branch.

        Equivalent to ``git branch -c|-C [<old_branch>] <new_branch>``.

        :param new_branch:
            Name for the new (copied) branch.

        :param old_branch:
            Source branch to copy. If None, uses the current branch as the source.

        :param force:
            **Tri-state.**
            - If True, performs forced copy using ``-C``.
            - If False, uses ``-c`` for safe copy.
            - If None, leaves behavior to Git default.

        :return: Output of ``git branch``.

        See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt--c
        """
        ...

    @abstractmethod
    def delete_branch(
        self,
        branch_name: str,
        *branch_names: str,
        force: bool | None = None,
        remote: bool | None = None,
    ) -> str:
        """
        Delete one or more branches.

        Equivalent to ``git branch -d|-D [-r] <branch-name>...``

        :param branch_name:
            First branch to delete.

        :param branch_names:
            Additional branches to delete.

        :param force:
            **Tri-state.**
            - If True, forces delete using ``-D``.
            - If False, deletes safely using ``-d``.
            - If None, leaves deletion behavior to Git default.

        :param remote:
            **Tri-state.**
            - If True, deletes remote-tracking branches (``-r``).
            - If False, emits ``--no-remote`` (though Git has no exact flag, useful for internal logic).
            - If None, omits remote flag entirely.

        :return: Output of ``git branch``.

        See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt--d
        """
        ...

    @abstractmethod
    def edit_description(self, branch_name: str | None = None) -> str:
        """
        Edit a branch's description.

        Equivalent to ``git branch --edit-description [<branch-name>]``.

        :param branch_name:
            Branch whose description you want to edit. Defaults to current branch if omitted.

        :return: Output of ``git branch``.

        See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt---edit-description
        """
        ...

    @overload
    @abstractmethod
    def list_branches(
        self,
        *patterns: str,
        color: Literal["always", "never", "auto"] | bool = ...,
        show_current: bool = ...,
        verbose: Literal[1, 2] | bool = ...,
        abbrev: int | Literal[False] = ...,
        sort: str | Literal[False] = ...,
        merged: str | None = ...,
        no_merged: str | None = ...,
        contains: str | None = ...,
        no_contains: str | None = ...,
        remotes: Literal[True] = ...,
        all_: bool = ...,
        points_at: str | Literal[False] = ...,
        format_: str | Literal[False] = ...,
        list_only: bool = ...,
        ignore_case: bool = ...,
        omit_empty: bool = ...,
    ) -> str: ...

    @overload
    @abstractmethod
    def list_branches(
        self,
        *patterns: str,
        color: Literal["always", "never", "auto"] | bool = ...,
        show_current: bool = ...,
        column: str | bool = ...,
        abbrev: int | Literal[False] = ...,
        sort: str | Literal[False] = ...,
        merged: str | None = ...,
        no_merged: str | None = ...,
        contains: str | None = ...,
        no_contains: str | None = ...,
        remotes: Literal[True] = ...,
        all_: bool = ...,
        points_at: str | Literal[False] = ...,
        format_: str | Literal[False] = ...,
        list_only: bool = ...,
        ignore_case: bool = ...,
        omit_empty: bool = ...,
    ) -> str: ...

    @abstractmethod
    def list_branches(
        self,
        *patterns: str,
        color: Literal["always", "never", "auto"] | bool | None = None,
        show_current: bool | None = None,
        verbose: Literal[1, 2] | bool | None = None,
        column: str | bool | None = None,
        abbrev: int | Literal[False] | None = None,
        sort: str | Literal[False] | None = None,
        merged: str | None = None,
        no_merged: str | None = None,
        contains: str | None = None,
        no_contains: str | None = None,
        points_at: str | Literal[False] | None = None,
        format_: str | Literal[False] | None = None,
        remotes: Literal[True] | None = None,
        all_: bool | None = None,
        list_only: bool | None = None,
        ignore_case: bool | None = None,
        omit_empty: bool | None = None,
    ) -> str:
        """
        List branches with advanced filtering, formatting, and display options.

        This is equivalent to the ``git branch`` command with various modifiers for sorting,
        verbosity, formatting, filtering by commit or pattern, and output customization.

        :param patterns: Shell-style glob patterns used to filter branch names.

        :param color: **Tri-state.**
            Controls coloring of the output.
            - If one of "always", "never", or "auto", passes ``--color=<value>``.
            - If True, emits ``--color``.
            - If False, emits ``--no-color``.
            - If None, does not pass any color option.

        :param show_current: If True, emits ``--show-current`` to print the current branch only.

        :param verbose: **Tri-state (with levels).**
            Controls the verbosity level.
            - 1: Emits ``-v`` for one-line verbose display.
            - 2: Emits ``-vv`` to show upstream info.
            - True: Emits ``--verbose``.
            - False: Emits ``--no-verbose``.
            - None: No verbosity flag passed.
            Note: Cannot be used with ``--column``.

        :param column: **Tri-state.**
            Controls multi-column layout.
            - If a string, uses ``--column=<layout>``.
            - If True, emits ``--column``.
            - If False, emits ``--no-column``.
            - If None, no column flag is passed.
            Note: Cannot be used with ``--verbose``.

        :param abbrev: Length of abbreviated commit hashes.
            - If an integer, emits ``--abbrev=<n>``.
            - If False, disables abbreviation using ``--no-abbrev``.
            - If None, abbreviation is not affected.

        :param sort: Sort branches using the given key.
            - If str, emits ``--sort=<key>``.
            - If False, disables sorting with ``--no-sort``.
            - If None, does not emit any sorting option.

        :param merged: Show branches merged into the specified commit.

        :param no_merged: Show branches not merged into the specified commit.

        :param contains: Show branches that contain the specified commit.

        :param no_contains: Show branches that do not contain the specified commit.

        :param points_at: **Tri-state.**
            - If a string, emits ``--points-at=<object>``.
            - If False, emits ``--no-points-at``.
            - If None, does not emit any points-at flag.

        :param format_: **Tri-state.**
            Customizes output formatting.
            - If str, emits ``--format=<fmt>``.
            - If False, emits ``--no-format``.
            - If None, uses default Git formatting.

        :param remotes: If True, shows only remote-tracking branches (``--remotes``).

        :param all_: If True, shows both local and remote branches (``--all``).

        :param list_only: If True, restricts the output to branch names only (``--list``).

        :param ignore_case: If True, pattern matching is case-insensitive (``--ignore-case``).

        :param omit_empty: If True, suppresses empty sections (``--omit-empty``).

        :return: Output of ``git branch``.

        See also: https://git-scm.com/docs/git-branch#_listing_branches
        """
        ...


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

    @property
    @abstractmethod
    def branch_subcmd(self) -> Branch:
        """
        :return: ``git branch`` subcommand.
        """
        ...

    @abstractmethod
    def clone(self) -> Self:
        """
        :return: a clone of this class.
        """
        ...
