#!/usr/bin/env python3
# coding=utf-8

"""
Git command interfaces with default implementation using subprocess calls.
"""
from __future__ import annotations

import subprocess
from abc import abstractmethod, ABC
from pathlib import Path
from subprocess import CompletedProcess, CalledProcessError
from typing import override
from collections.abc import Sequence

from mypy.semanal_shared import Protocol
from vt.utils.commons.commons.core_py import fallback_on_none, fallback_on_none_strict

from vt.vcs.git.gitlib import Git, GitCommandRunner, Version, LsTree, CanOverrideGitOpts, HasGitUnderneath, \
    GitSubCommand
from vt.vcs.git.gitlib.exceptions import GitCmdException


class SimpleGitCR[T](GitCommandRunner[T]):
    """
    Simple git command runner that simply runs everything `as-is` in a subprocess.
    """

    def run_git_command(self, main_cmd_args: list[str], subcommand_args: list[str], *subprocess_run_args,
                        **subprocess_run_kwargs) -> CompletedProcess[T]:
        try:
            return subprocess.run([GitCommandRunner.GIT_CMD, *main_cmd_args, *subcommand_args],
                                  *subprocess_run_args, **subprocess_run_kwargs)
        except CalledProcessError as e:
            raise GitCmdException(called_process_error=e) from e


class HasUnderlyingGitCommand[T](HasGitUnderneath[T], Protocol):
    @override
    @property
    @abstractmethod
    def underlying_git(self) -> GitCommand[T]:
        ...


class GitOptsOverriderCommand[T](CanOverrideGitOpts[T], HasUnderlyingGitCommand[T], Protocol):

    @override
    def git_opts_override(self, *,
                          cwd: Sequence[Path] | None = None,
                          c: dict[str, str] | None = None,
                          config_env: dict[str, str] | None = None,
                          exec_path: Path | None = None,
                          paginate: bool | None = None,
                          no_pager: bool | None = None,
                          git_dir: Path | None = None,
                          work_tree: Path | None = None,
                          namespace: str | None = None,
                          bare: bool | None = None,
                          no_replace_objects: bool | None = None,
                          no_lazy_fetch: bool | None = None,
                          no_optional_locks: bool | None = None,
                          no_advice: bool | None = None,
                          literal_pathspecs: bool | None = None,
                          glob_pathspecs: bool | None = None,
                          no_glob_pathspecs: bool | None = None,
                          icase_pathspecs: bool | None = None,
                          list_cmds: Sequence[str] | None = None,
                          attr_source: str | None = None) -> T:
        return self.underlying_git.git(
            cwd=cwd,
            c=c,
            config_env=config_env,
            exec_path=exec_path,
            paginate=paginate,
            no_pager=no_pager,
            git_dir=git_dir,
            work_tree=work_tree,
            namespace=namespace,
            bare=bare,
            no_replace_objects=no_replace_objects,
            no_lazy_fetch=no_lazy_fetch,
            no_optional_locks=no_optional_locks,
            no_advice=no_advice,
            literal_pathspecs=literal_pathspecs,
            glob_pathspecs=glob_pathspecs,
            no_glob_pathspecs=no_glob_pathspecs,
            icase_pathspecs=icase_pathspecs,
            list_cmds=list_cmds,
            attr_source=attr_source)


class GitSubcmdCommand[T](GitSubCommand[T], GitOptsOverriderCommand[T], Protocol):

    @override
    @property
    @abstractmethod
    def overrider_git_opts(self) -> GitOptsOverriderCommand[T]:
        ...


class VersionCommand[T](Version[T], GitSubcmdCommand['VersionCommand[T]'], Protocol):
    VERSION_CMD: str = 'version'


class LsTreeCommand[T](LsTree[T], GitSubcmdCommand['LsTree[T]'], Protocol):
    LS_TREE_CMD: str = 'ls-tree'


class GitCommand[T](Git[T], ABC):
    """
    Runs git as a command.
    """

    def __init__(self, runner: GitCommandRunner[T]):
        """
        :param runner: a ``GitCommandRunner`` which eventually runs the cli command in a subprocess.

        ... all other params are mirrors of ``Git`` ctor params.
        """
        self.runner = runner
        self.cwd: Sequence[Path] | None = None
        self.c: dict[str, str] | None = None
        self.config_env: dict[str, str] | None = None
        self.opt_exec_path: Path | None = None
        self.paginate: bool = False
        self.no_pager: bool = False
        self.git_dir: Path | None = None
        self.work_tree: Path | None = None
        self.namespace: str | None = None
        self.bare: bool = False
        self.no_replace_objects: bool = False
        self.no_lazy_fetch: bool = False
        self.no_optional_locks: bool = False
        self.no_advice: bool = False
        self.literal_pathspecs: bool = False
        self.glob_pathspecs: bool = False
        self.no_glob_pathspecs: bool = False
        self.icase_pathspecs: bool = False
        self.list_cmds: Sequence[str] | None = None
        self.attr_source: str | None = None

    # TODO: check why PyCharm says that Type of 'git' is incompatible with 'Git'.
    @override
    def git(self, *,
            cwd: Sequence[Path] | None = None,
            c: dict[str, str] | None = None,
            config_env: dict[str, str] | None = None,
            exec_path: Path | None = None,
            paginate: bool | None = None,
            no_pager: bool | None = None,
            git_dir: Path | None = None,
            work_tree: Path | None = None,
            namespace: str | None = None,
            bare: bool | None = None,
            no_replace_objects: bool | None = None,
            no_lazy_fetch: bool | None = None,
            no_optional_locks: bool | None = None,
            no_advice: bool | None = None,
            literal_pathspecs: bool | None = None,
            glob_pathspecs: bool | None = None,
            no_glob_pathspecs: bool | None = None,
            icase_pathspecs: bool | None = None,
            list_cmds: Sequence[str] | None = None,
            attr_source: str | None = None) -> GitCommand[T]:
        _git_cmd = self.clone()
        _git_cmd.cwd = fallback_on_none(cwd, self.cwd)
        _git_cmd.c = fallback_on_none(c, self.c)
        _git_cmd.config_env = fallback_on_none(config_env, self.config_env)
        _git_cmd.opt_exec_path = fallback_on_none(exec_path, self.opt_exec_path)
        _git_cmd.paginate = fallback_on_none_strict(paginate, self.paginate)
        _git_cmd.no_pager = fallback_on_none_strict(no_pager, self.no_pager)
        _git_cmd.git_dir = fallback_on_none(git_dir, self.git_dir)
        _git_cmd.work_tree = fallback_on_none(work_tree, self.work_tree)
        _git_cmd.namespace = fallback_on_none(namespace, self.namespace)
        _git_cmd.bare = fallback_on_none_strict(bare, self.bare)
        _git_cmd.no_replace_objects = fallback_on_none_strict(no_replace_objects, self.no_replace_objects)
        _git_cmd.no_lazy_fetch = fallback_on_none_strict(no_lazy_fetch, self.no_lazy_fetch)
        _git_cmd.no_optional_locks = fallback_on_none_strict(no_optional_locks, self.no_optional_locks)
        _git_cmd.no_advice = fallback_on_none_strict(no_advice, self.no_advice)
        _git_cmd.literal_pathspecs = fallback_on_none_strict(literal_pathspecs, self.literal_pathspecs)
        _git_cmd.glob_pathspecs = fallback_on_none_strict(glob_pathspecs, self.glob_pathspecs)
        _git_cmd.no_glob_pathspecs = fallback_on_none_strict(no_glob_pathspecs, self.no_glob_pathspecs)
        _git_cmd.icase_pathspecs = fallback_on_none_strict(icase_pathspecs, self.icase_pathspecs)
        _git_cmd.list_cmds = fallback_on_none(list_cmds, self.list_cmds)
        _git_cmd.attr_source = fallback_on_none(attr_source, self.attr_source)
        return _git_cmd

    def compute_main_cmd_args(self) -> list[str]:
        """
        :return: constructed git main command args, for example, ``--no-pager`` is a git main command arg in
            ``git --no-pager log -10``.
        """
        args = []

        # Handle -C (change directory)
        if self.cwd:
            for path in self.cwd:
                args += ['-C', str(path)]

        # Handle -c key=value (set config values)
        if self.c:
            for k, v in self.c.items():
                args += ['-c', f'{k}={v}']

        # --config-env is available in newer versions of git
        if self.config_env:
            for k, v in self.config_env.items():
                args += ['--config-env', f'{k}={v}']

        if self.opt_exec_path:
            args += ['--exec-path', str(self.opt_exec_path)]

        if self.paginate:
            args.append('--paginate')

        if self.no_pager:
            args.append('--no-pager')

        if self.git_dir:
            args += ['--git-dir', str(self.git_dir)]

        if self.work_tree:
            args += ['--work-tree', str(self.work_tree)]

        if self.namespace:
            args += ['--namespace', self.namespace]

        if self.bare:
            args.append('--bare')

        if self.no_replace_objects:
            args.append('--no-replace-objects')

        if self.no_lazy_fetch:
            args.append('--no-lazy-fetch')

        if self.no_optional_locks:
            args.append('--no-optional-locks')

        if self.no_advice:
            args.append('--no-advice')

        if self.literal_pathspecs:
            args.append('--literal-pathspecs')

        if self.glob_pathspecs:
            args.append('--glob-pathspecs')

        if self.no_glob_pathspecs:
            args.append('--noglob-pathspecs')

        if self.icase_pathspecs:
            args.append('--icase-pathspecs')

        if self.list_cmds:
            for cmd in self.list_cmds:
                args += ['--list-cmds', cmd]

        if self.attr_source:
            args += ['--attr-source', self.attr_source]

        return args

    @override
    @property
    def html_path(self) -> Path:
        html_path_str = '--html-path'
        return self._get_path(html_path_str)

    @override
    @property
    def info_path(self) -> Path:
        info_path_str = '--info-path'
        return self._get_path(info_path_str)

    @override
    @property
    def man_path(self) -> Path:
        man_path_str = '--man-path'
        return self._get_path(man_path_str)

    @override
    @property
    def exec_path(self) -> Path:
        exec_path_str = '--exec-path'
        return self._get_path(exec_path_str)

    def _get_path(self, path_opt_str: str) -> Path:
        main_opts = self.compute_main_cmd_args()
        main_opts.append(path_opt_str)
        _path_str = self.runner.run_git_command(main_opts, [], check=True, text=True,
                                    capture_output=True).stdout.strip()
        return Path(_path_str)

    @override
    @abstractmethod
    def clone(self) -> GitCommand[T]:
        ...
