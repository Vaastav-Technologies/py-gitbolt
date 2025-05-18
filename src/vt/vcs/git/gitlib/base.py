#!/usr/bin/env python3
# coding=utf-8

"""
interfaces related to processors specific to git commands.
"""
from __future__ import annotations
from abc import abstractmethod
from pathlib import Path
from subprocess import CompletedProcess
from typing import Protocol


class ForGit(Protocol):
    """
    Marker interface to mark an operation for git.
    """
    pass


class GitCommandRunner[T](ForGit, Protocol):
    """
    Interface to facilitate running git commands in subprocess.
    """

    GIT_CMD: str = 'git'

    @abstractmethod
    def run_git_command(self, main_cmd_args: list[str], subcommand_args: list[str], *subprocess_run_args,
                        **subprocess_run_kwargs) -> CompletedProcess[T]:
        """
        Run git subcommands in a separate process.

        :param main_cmd_args: git's main command args, i.e. ``git --no-pager log -1 master``. Here, ``--no-pager``
            is the main command arg.
        :param subcommand_args: git subcommand args, i.e. ``git --no-pager log -1 master``. Here, ``-1 master`` are
            the subcommand args.
        :param subprocess_run_args: Any extra arguments ``(*args)`` to be sent to ``subprocess.run()``.
        :param subprocess_run_kwargs: Any extra keyword arguments ``(**kwargs)`` to be sent to ``subprocess.run()``.
        :return: ``CompletedProcess[T]`` instance with captured out, err and return-code.
        :raise CalledProcessError[T]: in case the process called returns non-zero return-code.
        """
        ...


class GitSubCommand[T](ForGit, Protocol):
    """
    Interface for git subcommands, such as:

    * ``add``
    * ``commit``
    * ``pull``
    * ...
    etc.
    """

    @abstractmethod
    def git_opts_override(self, *, cwd: list[str] | list[Path] | None = None, c: dict[str, str] | None = None,
                          config_env: dict[str, str] | None = None, exec_path: str | Path, paginate: bool = False,
                          no_pager: bool = False, git_dir: str | Path | None = None,
                          work_tree: str | Path | None = None, namespace: str | None = None, bare: bool = False,
                          no_replace_objects: bool = False, no_lazy_fetch: bool, no_optional_locks: bool = False,
                          no_advice: bool = False, literal_pathspecs: bool = False, glob_pathspecs: bool = False,
                          no_glob_pathspecs: bool = False, icase_pathspecs: bool = False,
                          list_cmds: list[str] | None = None, attr_source: str | None = None) -> T:
        """
        Temporarily override options to the main git command before current subcommand runs.
        All the parameters mirror options described in the `git documentation <https://git-scm.com/docs/git>`_.

        For example, in ``git --no-pager log -1 master`` git command, ``--no-pager`` is the main command arg.

        :return: the subcommand instance with overridden git main command args.
        """
        ...


class LsTree[T](GitSubCommand['LsTree[T]'], Protocol):
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


class Git[T](ForGit, Protocol):

    @abstractmethod
    def git(self, *, cwd: list[str] | list[Path] | None = None, c: dict[str, str] | None = None,
            config_env: dict[str, str] | None = None, exec_path: str | Path, paginate: bool = False,
            no_pager: bool = False, git_dir: str | Path | None = None, work_tree: str | Path | None = None,
            namespace: str | None = None, bare: bool = False, no_replace_objects: bool = False, no_lazy_fetch: bool,
            no_optional_locks: bool = False, no_advice: bool = False, literal_pathspecs: bool = False,
            glob_pathspecs: bool = False, no_glob_pathspecs: bool = False, icase_pathspecs: bool = False,
            list_cmds: list[str] | None = None, attr_source: str | None = None) -> Git[T]:
        """
        All the parameters are mirrors of the parameters of ``git ls-tree`` CLI command
        from `git documentation <https://git-scm.com/docs/git>`_.

        :param cwd: param mirror for ``-C``.
        :param c: exact mirror.
        :param config_env: exact mirror.
        :param exec_path: exact mirror.
        :param paginate: exact mirror.
        :param no_pager: exact mirror.
        :param git_dir: exact mirror.
        :param work_tree: exact mirror.
        :param namespace: exact mirror.
        :param bare: exact mirror.
        :param no_replace_objects: exact mirror.
        :param no_lazy_fetch: exact mirror.
        :param no_optional_locks: exact mirror.
        :param no_advice: exact mirror.
        :param literal_pathspecs: exact mirror.
        :param glob_pathspecs: exact mirror.
        :param no_glob_pathspecs: param mirror for ``--noglob-pathspecs``.
        :param icase_pathspecs: exact mirror.
        :param attr_source: exact mirror.
        :param list_cmds: exact mirror.
        :return: overridden options for ``git``.
        """
        ...

    @property
    @abstractmethod
    def git_version_subcmd(self) -> Version[T]:
        ...

    @property
    @abstractmethod
    def ls_tree(self) -> LsTree[T]:
        ...

    @property
    def version(self) -> T:
        return self.git_version_subcmd.version()

    @property
    def html_path(self) -> Path:
        ...

    @property
    def info_path(self) -> Path:
        ...

    @property
    def man_path(self) -> Path:
        ...
