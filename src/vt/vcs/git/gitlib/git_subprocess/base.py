#!/usr/bin/env python3
# coding=utf-8

"""
Git command interfaces with default implementation using subprocess calls.
"""
from __future__ import annotations

from abc import abstractmethod, ABC
from pathlib import Path
from subprocess import CompletedProcess
from typing import override, Protocol, Unpack

from vt.utils.commons.commons.core_py import fallback_on_none, is_unset

from vt.vcs.git.gitlib import Git, Version, LsTree, CanOverrideGitOpts, HasGitUnderneath, \
    GitSubCommand, ForGit, GitOpts


class GitCommandRunner[T](ForGit, Protocol):
    """
    Interface to facilitate running git commands in subprocess.
    """

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


class HasUnderlyingGitCommand[T](HasGitUnderneath[T], Protocol):
    @override
    @property
    @abstractmethod
    def underlying_git(self) -> GitCommand[T]:
        ...


class GitOptsOverriderCommand[T](CanOverrideGitOpts[T], HasUnderlyingGitCommand[T], Protocol):

    @override
    def git_opts_override(self, **overrides: Unpack[GitOpts]) -> T:
        return self.underlying_git.git(
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


class GitSubcmdCommand[T](GitSubCommand[T], GitOptsOverriderCommand[T], Protocol):

    @override
    @property
    @abstractmethod
    def overrider_git_opts(self) -> GitOptsOverriderCommand[T]:
        ...

    @override
    @abstractmethod
    def _subcmd_git_override(self, git: Git[T]) -> GitSubcmdCommand[T]:
        ...


class VersionCommand[T](Version[T], GitSubcmdCommand['VersionCommand[T]'], Protocol):

    @override
    @abstractmethod
    def _subcmd_git_override(self, git: Git[T]) -> VersionCommand[T]:
        ...


class LsTreeCommand[T](LsTree[T], GitSubcmdCommand['LsTree[T]'], Protocol):

    @override
    @abstractmethod
    def _subcmd_git_override(self, git: Git[T]) -> LsTreeCommand[T]:
        ...


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
        self._main_cmd_opts: GitOpts = {}

    # TODO: check why PyCharm says that Type of 'git' is incompatible with 'Git'.
    @override
    def git(self, **git_main_opts: Unpack[GitOpts]) -> GitCommand[T]:
        _git_cmd = self.clone()
        _main_cmd_opts: GitOpts = {
            'C': fallback_on_none(git_main_opts.get('C'), self._main_cmd_opts.get('C')),
            'c': fallback_on_none(git_main_opts.get('c'), self._main_cmd_opts.get('c')),
            'config_env': fallback_on_none(git_main_opts.get('config_env'), self._main_cmd_opts.get('config_env')),
            'exec_path': fallback_on_none(git_main_opts.get('exec_path'), self._main_cmd_opts.get('exec_path')),
            'paginate': fallback_on_none(git_main_opts.get('paginate'), self._main_cmd_opts.get('paginate')),
            'no_pager': fallback_on_none(git_main_opts.get('no_pager'), self._main_cmd_opts.get('no_pager')),
            'git_dir': fallback_on_none(git_main_opts.get('git_dir'), self._main_cmd_opts.get('git_dir')),
            'work_tree': fallback_on_none(git_main_opts.get('work_tree'), self._main_cmd_opts.get('work_tree')),
            'namespace': fallback_on_none(git_main_opts.get('namespace'), self._main_cmd_opts.get('namespace')),
            'bare': fallback_on_none(git_main_opts.get('bare'), self._main_cmd_opts.get('bare')),
            'no_replace_objects': fallback_on_none(
                git_main_opts.get('no_replace_objects'), self._main_cmd_opts.get('no_replace_objects')
            ),
            'no_lazy_fetch': fallback_on_none(
                git_main_opts.get('no_lazy_fetch'), self._main_cmd_opts.get('no_lazy_fetch')
            ),
            'no_optional_locks': fallback_on_none(
                git_main_opts.get('no_optional_locks'), self._main_cmd_opts.get('no_optional_locks')
            ),
            'no_advice': fallback_on_none(
                git_main_opts.get('no_advice'), self._main_cmd_opts.get('no_advice')
            ),
            'literal_pathspecs': fallback_on_none(
                git_main_opts.get('literal_pathspecs'), self._main_cmd_opts.get('literal_pathspecs')
            ),
            'glob_pathspecs': fallback_on_none(
                git_main_opts.get('glob_pathspecs'), self._main_cmd_opts.get('glob_pathspecs')
            ),
            'noglob_pathspecs': fallback_on_none(
                git_main_opts.get('noglob_pathspecs'), self._main_cmd_opts.get('noglob_pathspecs')
            ),
            'icase_pathspecs': fallback_on_none(
                git_main_opts.get('icase_pathspecs'), self._main_cmd_opts.get('icase_pathspecs')
            ),
            'list_cmds': fallback_on_none(git_main_opts.get('list_cmds'), self._main_cmd_opts.get('list_cmds')),
            'attr_source': fallback_on_none(git_main_opts.get('attr_source'), self._main_cmd_opts.get('attr_source')),
        }
        _git_cmd._main_cmd_opts = _main_cmd_opts
        return _git_cmd

    def compute_main_cmd_args(self) -> list[str]:
        return (
            self._main_cmd_cap_c_args() +
            self._main_cmd_small_c_args() +
            self._main_cmd_config_env_args() +
            self._main_cmd_exec_path_args() +
            self._main_cmd_paginate_args() +
            self._main_cmd_no_pager_args() +
            self._main_cmd_git_dir_args() +
            self._main_cmd_work_tree_args() +
            self._main_cmd_namespace_args() +
            self._main_cmd_bare_args() +
            self._main_cmd_no_replace_objects_args() +
            self._main_cmd_no_lazy_fetch_args() +
            self._main_cmd_no_optional_locks_args() +
            self._main_cmd_no_advice_args() +
            self._main_cmd_literal_pathspecs_args() +
            self._main_cmd_glob_pathspecs_args() +
            self._main_cmd_noglob_pathspecs_args() +
            self._main_cmd_icase_pathspecs_args() +
            self._main_cmd_list_cmds_args() +
            self._main_cmd_attr_source_args()
        )

    def _main_cmd_cap_c_args(self) -> list[str]:
        val = self._main_cmd_opts.get("C")
        if val is not None and not is_unset(val):
            return [item for path in val for item in ["-C", str(path)]]
        return []

    def _main_cmd_small_c_args(self) -> list[str]:
        val = self._main_cmd_opts.get("c")
        if val is not None and not is_unset(val):
            args = []
            for k, v in val.items():
                if is_unset(v):
                    continue  # explicitly skip unset keys
                if v is True or v is None: # treat None as True
                    args += ["-c", k]
                elif v is False:
                    args += ["-c", f"{k}="]
                else:
                    args += ["-c", f"{k}={v}"]
            return args
        return []

    def _main_cmd_config_env_args(self) -> list[str]:
        val = self._main_cmd_opts.get("config_env")
        if val is not None and not is_unset(val):
            return [item for k, v in val.items() for item in ["--config-env", f"{k}={v}"]]
        return []

    def _main_cmd_exec_path_args(self) -> list[str]:
        val = self._main_cmd_opts.get("exec_path")
        if val is not None and not is_unset(val):
            return ["--exec-path", str(val)]
        return []

    def _main_cmd_paginate_args(self) -> list[str]:
        val = self._main_cmd_opts.get("paginate")
        if val is not None and not is_unset(val):
            return ["--paginate"]
        return []

    def _main_cmd_no_pager_args(self) -> list[str]:
        val = self._main_cmd_opts.get("no_pager")
        if val is not None and not is_unset(val):
            return ["--no-pager"]
        return []

    def _main_cmd_git_dir_args(self) -> list[str]:
        val = self._main_cmd_opts.get("git_dir")
        if val is not None and not is_unset(val):
            return ["--git-dir", str(val)]
        return []

    def _main_cmd_work_tree_args(self) -> list[str]:
        val = self._main_cmd_opts.get("work_tree")
        if val is not None and not is_unset(val):
            return ["--work-tree", str(val)]
        return []

    def _main_cmd_namespace_args(self) -> list[str]:
        val = self._main_cmd_opts.get("namespace")
        if val is not None and not is_unset(val):
            return ["--namespace", val]
        return []

    def _main_cmd_bare_args(self) -> list[str]:
        val = self._main_cmd_opts.get("bare")
        if val is not None and not is_unset(val):
            return ["--bare"]
        return []

    def _main_cmd_no_replace_objects_args(self) -> list[str]:
        val = self._main_cmd_opts.get("no_replace_objects")
        if val is not None and not is_unset(val):
            return ["--no-replace-objects"]
        return []

    def _main_cmd_no_lazy_fetch_args(self) -> list[str]:
        val = self._main_cmd_opts.get("no_lazy_fetch")
        if val is not None and not is_unset(val):
            return ["--no-lazy-fetch"]
        return []

    def _main_cmd_no_optional_locks_args(self) -> list[str]:
        val = self._main_cmd_opts.get("no_optional_locks")
        if val is not None and not is_unset(val):
            return ["--no-optional-locks"]
        return []

    def _main_cmd_no_advice_args(self) -> list[str]:
        val = self._main_cmd_opts.get("no_advice")
        if val is not None and not is_unset(val):
            return ["--no-advice"]
        return []

    def _main_cmd_literal_pathspecs_args(self) -> list[str]:
        val = self._main_cmd_opts.get("literal_pathspecs")
        if val is not None and not is_unset(val):
            return ["--literal-pathspecs"]
        return []

    def _main_cmd_glob_pathspecs_args(self) -> list[str]:
        val = self._main_cmd_opts.get("glob_pathspecs")
        if val is not None and not is_unset(val):
            return ["--glob-pathspecs"]
        return []

    def _main_cmd_noglob_pathspecs_args(self) -> list[str]:
        val = self._main_cmd_opts.get("noglob_pathspecs")
        if val is not None and not is_unset(val):
            return ["--noglob-pathspecs"]
        return []

    def _main_cmd_icase_pathspecs_args(self) -> list[str]:
        val = self._main_cmd_opts.get("icase_pathspecs")
        if val is not None and not is_unset(val):
            return ["--icase-pathspecs"]
        return []

    def _main_cmd_list_cmds_args(self) -> list[str]:
        val = self._main_cmd_opts.get("list_cmds")
        if val is not None and not is_unset(val):
            return [item for cmd in val for item in ["--list-cmds", cmd]]
        return []

    def _main_cmd_attr_source_args(self) -> list[str]:
        val = self._main_cmd_opts.get("attr_source")
        if val is not None and not is_unset(val):
            return ["--attr-source", val]
        return []

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
