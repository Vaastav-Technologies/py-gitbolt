#!/usr/bin/env python3
# coding=utf-8

"""
interfaces related to processors specific to git commands.
"""
from __future__ import annotations
from abc import abstractmethod
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol, override, TypedDict, Unpack

from vt.utils.commons.commons.op import RootDirOp


class ForGit(Protocol):
    """
    Marker interface to mark an operation for git.
    """
    pass


class GitOpts(TypedDict, total=False):
    """
    All the parameters are mirrors of the options of the ``git`` CLI command
    from `git documentation <https://git-scm.com/docs/git>`_.

    These options are applied before any git subcommand (like ``log``, ``commit``, etc.).

    For example, in ``git --no-pager log -1 master`` git command, ``--no-pager`` is the main command option.
    """

    C: Sequence[Path] | None
    """
    Mirror of ``-C <path>``.

    Run as if git was started in the specified path(s) instead of the current working directory.
    Can be specified multiple times.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt--Cltpathgt>`_.
    """

    c: dict[str, str] | None
    """
    Mirror of ``-c <name>=<value>``.

    Sets a configuration variable for the duration of the git command.
    Equivalent to using ``git config`` temporarily.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt--cltnamegtltvaluegt>`_.
    """

    config_env: dict[str, str] | None
    """
    Mirror of ``--config-env=<name>=<env-var>``.

    Set configuration variables from environment variables, useful in environments where configuration is set externally.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---config-envltnamegtltenvvargt>`_.
    """

    exec_path: Path | None
    """
    Mirror of ``--exec-path[=<path>]``.

    Path to the directory where git-core executables are located.
    If not set, uses the default from the environment or compiled-in path.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---exec-pathltpathgt>`_.
    """

    paginate: bool | None
    """
    Mirror of ``--paginate``.

    Forces git to use a pager for output, even if stdout is not a terminal.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---paginate>`_.
    """

    no_pager: bool | None
    """
    Mirror of ``--no-pager``.

    Disables the use of a pager for output.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---no-pager>`_.
    """

    git_dir: Path | None
    """
    Mirror of ``--git-dir=<path>``.

    Sets the path to the git repository (i.e., the ``.git`` directory).

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---git-dirltpathgt>`_.
    """

    work_tree: Path | None
    """
    Mirror of ``--work-tree=<path>``.

    Sets the working tree root for the repository.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---work-treeltpathgt>`_.
    """

    namespace: str | None
    """
    Mirror of ``--namespace=<namespace>``.

    Sets the git namespace for refs, useful in server environments or special ref layouts.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---namespaceltpathgt>`_.
    """

    bare: bool | None
    """
    Mirror of ``--bare``.

    Treat the repository as a bare repository.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---bare>`_.
    """

    no_replace_objects: bool | None
    """
    Mirror of ``--no-replace-objects``.

    Disables use of replacement objects that might otherwise override objects in the repo.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---no-replace-objects>`_.
    """

    no_lazy_fetch: bool | None
    """
    Mirror of ``--no-lazy-fetch``.

    Prevents git from auto-fetching missing objects on demand.
    Introduced in newer git versions.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---no-lazy-fetch>`_.
    """

    no_optional_locks: bool | None
    """
    Mirror of ``--no-optional-locks``.

    Prevents git from taking optional locks (used for performance tuning).

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---no-optional-locks>`_.
    """

    no_advice: bool | None
    """
    Mirror of ``--no-advice``.

    Suppresses all advice messages that git might normally print.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---no-advice>`_.
    """

    literal_pathspecs: bool | None
    """
    Mirror of ``--literal-pathspecs``.

    Treat pathspecs literally (no wildcards, no globbing).

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---literal-pathspecs>`_.
    """

    glob_pathspecs: bool | None
    """
    Mirror of ``--glob-pathspecs``.

    Enable globbing in pathspecs.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---glob-pathspecs>`_.
    """

    noglob_pathspecs: bool | None
    """
    Mirror of ``--noglob-pathspecs``.

    Disable globbing for pathspecs.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---noglob-pathspecs>`_.
    """

    icase_pathspecs: bool | None
    """
    Mirror of ``--icase-pathspecs``.

    Makes pathspecs case-insensitive (useful on case-insensitive filesystems).

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---icase-pathspecs>`_.
    """

    list_cmds: Sequence[str] | None
    """
    Mirror of ``--list-cmds=<category>``.

    Used to list available commands grouped by category.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---list-cmdsltgroupgtltgroupgt82308203>`_.
    """

    attr_source: str | None
    """
    Mirror of ``--attr-source=<tree-ish>``.

    Specifies the source tree for attribute lookups.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---attr-sourcelttree-ishgt>`_.
    """


class HasGitUnderneath[T](Protocol):
    """
    Stores a reference to main git instance.
    """

    @property
    @abstractmethod
    def underlying_git(self) -> Git[T]:
        """
        :return: stored git instance reference.
        """
        ...


class CanOverrideGitOpts[T](HasGitUnderneath[T], Protocol):
    """
    Can override main git command options.

    For example, in ``git --no-pager log -1 master`` git command, ``--no-pager`` is the main command arg.
    """

    @abstractmethod
    def git_opts_override(self, **overrides: Unpack[GitOpts]) -> T:
        """
        Temporarily override options to the main git command before current subcommand runs.
        All the parameters mirror options described in the `git documentation <https://git-scm.com/docs/git>`_.

        For example, in ``git --no-pager log -1 master`` git command, ``--no-pager`` is the main command arg.

        :return: the subcommand instance with overridden git main command args.
        """
        ...


class GitSubCommand[T](CanOverrideGitOpts[T], Protocol):
    """
    Interface for git subcommands, such as:

    * ``add``
    * ``commit``
    * ``pull``
    * ...
    etc.
    """

    @property
    @abstractmethod
    def overrider_git_opts(self) -> CanOverrideGitOpts[T]:
        """
        :return: the overrider object that helps override main git command options.
        """
        ...

    # TODO: check why PyCharm says that Type of 'git_opts_override' is incompatible with 'CanOverrideGitOpts'.
    @override
    def git_opts_override(self, **overrides: Unpack[GitOpts]) -> T:
        ano_git = self.overrider_git_opts.git_opts_override(
            C=overrides.get("C"),
            c=overrides.get("c"),
            config_env=overrides.get("config_env"),
            exec_path=overrides.get("exec_path"),
            paginate=overrides.get("paginate"),
            no_pager=overrides.get("no_pager"),
            git_dir=overrides.get("git_dir"),
            work_tree=overrides.get("work_tree"),
            namespace=overrides.get("namespace"),
            bare=overrides.get("bare"),
            no_replace_objects=overrides.get("no_replace_objects"),
            no_lazy_fetch=overrides.get("no_lazy_fetch"),
            no_optional_locks=overrides.get("no_optional_locks"),
            no_advice=overrides.get("no_advice"),
            literal_pathspecs=overrides.get("literal_pathspecs"),
            glob_pathspecs=overrides.get("glob_pathspecs"),
            noglob_pathspecs=overrides.get("noglob_pathspecs"),
            icase_pathspecs=overrides.get("icase_pathspecs"),
            list_cmds=overrides.get("list_cmds"),
            attr_source=overrides.get("attr_source"))
        return self._subcmd_git_override(ano_git)

    @abstractmethod
    def _subcmd_git_override(self, git: Git[T]) -> GitSubCommand[T]:
        ...


class LsTree[T](GitSubCommand['LsTree[T]'], RootDirOp, Protocol):
    """
    Interface for ``git ls-tree`` command.
    """

    @abstractmethod
    def ls_tree(self, tree_ish: str, *, d: bool = False, r: bool = False, t: bool = False, long: bool = False,
                z: bool = False, name_only: bool = False, object_only: bool = False, full_name: bool = False,
                full_tree: bool = False, abbrev: int | None = None, format_: str | None = None,
                path: list[str] | None = None) -> T:
        """
        All the parameters are mirrors of the parameters of ``git ls-tree`` CLI command
        from `git ls-tree documentation <https://git-scm.com/docs/git-ls-tree>`_.

        :return: ``ls-tree`` output morphed into ``T``.
        """
        ...

    @override
    @abstractmethod
    def _subcmd_git_override(self, git: Git[T]) -> LsTree[T]:
        ...


class Version[T](GitSubCommand['Version[T]'], Protocol):
    """
    Interface for ``git version`` command.
    """

    @abstractmethod
    def version(self, build_options: bool = False) -> T:
        """
        All the parameters are mirrors of the parameters of ``git version`` CLI command
        from `git version documentation <https://git-scm.com/docs/git-version>`_.

        :return: ``version`` output morphed into ``T``.
        """
        ...

    @override
    @abstractmethod
    def _subcmd_git_override(self, git: Git[T]) -> Version[T]:
        ...


class Git[T](ForGit, Protocol):
    """
    Class designed analogous to documentation provided on `git documentation <https://git-scm.com/docs/git>`_.
    """

    @abstractmethod
    def git(self, **git_main_opts: Unpack[GitOpts]) -> Git[T]:
        """
        Get a new ``Git`` object with the git main command options overridden.

        All the parameters in ``**git_main_opts`` are mirrors of the parameters of the ``git`` CLI command from
        `git documentation <https://git-scm.com/docs/git>`_.

        For example, in ``git --no-pager log -1 master`` git command, ``--no-pager`` is the main command option.

        :param git_main_opts: All the parameters are mirrors of the parameters of the ``git`` CLI command
            from `git documentation <https://git-scm.com/docs/git>`_.
        :return: overridden options for ``git``.
        """
        ...

    @property
    @abstractmethod
    def version_subcmd(self) -> Version[T]:
        """
        :return: ``git version`` subcommand.
        """
        ...

    @property
    @abstractmethod
    def ls_tree_subcmd(self) -> LsTree[T]:
        """
        :return: ``git ls-tree`` subcommand.
        """
        ...

    @property
    def version(self) -> T:
        """
        :return: current git version.
        """
        return self.version_subcmd.version()

    @property
    def exec_path(self) -> Path:
        """
        :return: Path to wherever your core Git programs are installed.
        """
        ...

    @property
    def html_path(self) -> Path:
        """
        :return: the path, without trailing slash, where Git’s HTML documentation is installed.
        """
        ...

    @property
    def info_path(self) -> Path:
        """
        :return: the path where the Info files documenting this version of Git are installed.
        """
        ...

    @property
    def man_path(self) -> Path:
        """
        :return: the man path (see man(1)) for the man pages for this version of Git.
        """
        ...

    @abstractmethod
    def clone(self) -> Git[T]:
        """
        :return: a clone of this class.
        """
        ...
