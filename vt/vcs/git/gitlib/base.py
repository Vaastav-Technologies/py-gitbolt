#!/usr/bin/env python3
# coding=utf-8

"""
interfaces related to processors specific to git commands.
"""
from __future__ import annotations
from abc import abstractmethod
from subprocess import CompletedProcess
from typing import Protocol


class ForGit(Protocol):
    """
    Marker interface to mark a command runner for git.
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
    def git_opts_override(self, *, exec_path: bool = False, paginate: bool = False, no_pager: bool = False,
                          git_dir: str | None = None, work_tree: str | None = None, namespace: str | None = None) -> T:
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


class Git[T](ForGit, Protocol):
    @property
    @abstractmethod
    def ls_tree(self) -> LsTree[T]:
        ...
