#!/usr/bin/env python3
# coding=utf-8

"""
Git command interfaces with default implementation using subprocess calls.
"""
from __future__ import annotations

import subprocess
from abc import abstractmethod
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
    pass


class LsTreeCommand[T](LsTree[T], GitSubcmdCommand['LsTree[T]'], Protocol):
    pass


class GitCommand[T](Git[T]):
    """
    Runs git as a command.
    """

    def __init__(self, runner: GitCommandRunner[T], *,
                 cwd: Sequence[Path] | None = None,
                 c: dict[str, str] | None = None,
                 config_env: dict[str, str] | None = None,
                 exec_path: Path | None = None,
                 paginate: bool = False,
                 no_pager: bool = False,
                 git_dir: Path | None = None,
                 work_tree: Path | None = None,
                 namespace: str | None = None,
                 bare: bool = False,
                 no_replace_objects: bool = False,
                 no_lazy_fetch: bool,
                 no_optional_locks: bool = False,
                 no_advice: bool = False,
                 literal_pathspecs: bool = False,
                 glob_pathspecs: bool = False,
                 no_glob_pathspecs: bool = False,
                 icase_pathspecs: bool = False,
                 list_cmds: Sequence[str] | None = None,
                 attr_source: str | None = None):
        """
        :param runner: a ``GitCommandRunner`` which eventually runs the cli command in a subprocess.

        ... all other params are mirrors of ``Git`` ctor params.
        """
        self.runner = runner
        self.cwd = cwd
        self.c = c
        self.config_env = config_env
        self.opt_exec_path = exec_path
        self.paginate = paginate
        self.no_pager = no_pager
        self.git_dir = git_dir
        self.work_tree = work_tree
        self.namespace = namespace
        self.bare = bare
        self.no_replace_objects = no_replace_objects
        self.no_lazy_fetch = no_lazy_fetch
        self.no_optional_locks = no_optional_locks
        self.no_advice = no_advice
        self.literal_pathspecs = literal_pathspecs
        self.glob_pathspecs = glob_pathspecs
        self.no_glob_pathspecs = no_glob_pathspecs
        self.icase_pathspecs = icase_pathspecs
        self.list_cmds = list_cmds
        self.attr_source = attr_source

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
        return GitCommand[T](
            runner=self.runner,
            cwd=fallback_on_none(cwd, self.cwd),
            c=fallback_on_none(c, self.c),
            config_env=fallback_on_none(config_env, self.config_env),
            exec_path=fallback_on_none(exec_path, self.exec_path),
            paginate=fallback_on_none_strict(paginate, self.paginate),
            no_pager=fallback_on_none_strict(no_pager, self.no_pager),
            git_dir=fallback_on_none(git_dir, self.git_dir),
            work_tree=fallback_on_none(work_tree, self.work_tree),
            namespace=fallback_on_none(namespace, self.namespace),
            bare=fallback_on_none_strict(bare, self.bare),
            no_replace_objects=fallback_on_none_strict(no_replace_objects, self.no_replace_objects),
            no_lazy_fetch=fallback_on_none_strict(no_lazy_fetch, self.no_lazy_fetch),
            no_optional_locks=fallback_on_none_strict(no_optional_locks, self.no_optional_locks),
            no_advice=fallback_on_none_strict(no_advice, self.no_advice),
            literal_pathspecs=fallback_on_none_strict(literal_pathspecs, self.literal_pathspecs),
            glob_pathspecs=fallback_on_none_strict(glob_pathspecs, self.glob_pathspecs),
            no_glob_pathspecs=fallback_on_none_strict(no_glob_pathspecs, self.no_glob_pathspecs),
            icase_pathspecs=fallback_on_none_strict(icase_pathspecs, self.icase_pathspecs),
            list_cmds=fallback_on_none(list_cmds, self.list_cmds),
            attr_source=fallback_on_none(attr_source, self.attr_source)
        )

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
    def git_version_subcmd(self) -> VersionCommand[T]:
        pass

    @override
    @property
    def ls_tree(self) -> LsTree[T]:
        pass

    @override
    @property
    def html_path(self) -> Path:
        ...

    @override
    @property
    def info_path(self) -> Path:
        ...

    @override
    @property
    def man_path(self) -> Path:
        ...
