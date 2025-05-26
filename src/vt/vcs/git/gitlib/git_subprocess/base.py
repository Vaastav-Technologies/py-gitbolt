#!/usr/bin/env python3
# coding=utf-8

"""
Git command interfaces with default implementation using subprocess calls.
"""
from __future__ import annotations

from abc import abstractmethod, ABC
from pathlib import Path
from typing import override, Protocol, Unpack, Self

from vt.utils.commons.commons.core_py import is_unset, not_none_not_unset

from vt.vcs.git.gitlib import Git, Version, LsTree, GitOpts
from vt.vcs.git.gitlib.git_subprocess.runner import GitCommandRunner
from vt.vcs.git.gitlib.utils import merge_git_opts


class GitCommand(Git, ABC):
    """
    Runs git as a command.
    """

    def __init__(self, runner: GitCommandRunner):
        """
        :param runner: a ``GitCommandRunner`` which eventually runs the cli command in a subprocess.
        """
        self.runner: GitCommandRunner = runner
        self._main_cmd_opts: GitOpts = {}

    @override
    def git(self, **git_main_opts: Unpack[GitOpts]) -> GitCommand:
        _git_cmd = self.clone()
        _main_cmd_opts = merge_git_opts(git_main_opts, self._main_cmd_opts)
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
        if not_none_not_unset(val):
            return [item for path in val for item in ["-C", str(path)]]
        return []

    def _main_cmd_small_c_args(self) -> list[str]:
        val = self._main_cmd_opts.get("c")
        if not_none_not_unset(val):
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
        if not_none_not_unset(val):
            return [item for k, v in val.items() for item in ["--config-env", f"{k}={v}"]]
        return []

    def _main_cmd_exec_path_args(self) -> list[str]:
        val = self._main_cmd_opts.get("exec_path")
        if not_none_not_unset(val):
            return ["--exec-path", str(val)]
        return []

    def _main_cmd_paginate_args(self) -> list[str]:
        val = self._main_cmd_opts.get("paginate")
        if not_none_not_unset(val):
            return ["--paginate"]
        return []

    def _main_cmd_no_pager_args(self) -> list[str]:
        val = self._main_cmd_opts.get("no_pager")
        if not_none_not_unset(val):
            return ["--no-pager"]
        return []

    def _main_cmd_git_dir_args(self) -> list[str]:
        val = self._main_cmd_opts.get("git_dir")
        if not_none_not_unset(val):
            return ["--git-dir", str(val)]
        return []

    def _main_cmd_work_tree_args(self) -> list[str]:
        val = self._main_cmd_opts.get("work_tree")
        if not_none_not_unset(val):
            return ["--work-tree", str(val)]
        return []

    def _main_cmd_namespace_args(self) -> list[str]:
        val = self._main_cmd_opts.get("namespace")
        if not_none_not_unset(val):
            return ["--namespace", val]
        return []

    def _main_cmd_bare_args(self) -> list[str]:
        val = self._main_cmd_opts.get("bare")
        if not_none_not_unset(val):
            return ["--bare"]
        return []

    def _main_cmd_no_replace_objects_args(self) -> list[str]:
        val = self._main_cmd_opts.get("no_replace_objects")
        if not_none_not_unset(val):
            return ["--no-replace-objects"]
        return []

    def _main_cmd_no_lazy_fetch_args(self) -> list[str]:
        val = self._main_cmd_opts.get("no_lazy_fetch")
        if not_none_not_unset(val):
            return ["--no-lazy-fetch"]
        return []

    def _main_cmd_no_optional_locks_args(self) -> list[str]:
        val = self._main_cmd_opts.get("no_optional_locks")
        if not_none_not_unset(val):
            return ["--no-optional-locks"]
        return []

    def _main_cmd_no_advice_args(self) -> list[str]:
        val = self._main_cmd_opts.get("no_advice")
        if not_none_not_unset(val):
            return ["--no-advice"]
        return []

    def _main_cmd_literal_pathspecs_args(self) -> list[str]:
        val = self._main_cmd_opts.get("literal_pathspecs")
        if not_none_not_unset(val):
            return ["--literal-pathspecs"]
        return []

    def _main_cmd_glob_pathspecs_args(self) -> list[str]:
        val = self._main_cmd_opts.get("glob_pathspecs")
        if not_none_not_unset(val):
            return ["--glob-pathspecs"]
        return []

    def _main_cmd_noglob_pathspecs_args(self) -> list[str]:
        val = self._main_cmd_opts.get("noglob_pathspecs")
        if not_none_not_unset(val):
            return ["--noglob-pathspecs"]
        return []

    def _main_cmd_icase_pathspecs_args(self) -> list[str]:
        val = self._main_cmd_opts.get("icase_pathspecs")
        if not_none_not_unset(val):
            return ["--icase-pathspecs"]
        return []

    def _main_cmd_list_cmds_args(self) -> list[str]:
        val = self._main_cmd_opts.get("list_cmds")
        if not_none_not_unset(val):
            return [item for cmd in val for item in ["--list-cmds", cmd]]
        return []

    def _main_cmd_attr_source_args(self) -> list[str]:
        val = self._main_cmd_opts.get("attr_source")
        if not_none_not_unset(val):
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

    @override
    @property
    @abstractmethod
    def version_subcmd(self) -> VersionCommand[Self]:
        ...

    @override
    @property
    @abstractmethod
    def ls_tree_subcmd(self) -> LsTreeCommand[Self]:
        ...

    def _get_path(self, path_opt_str: str) -> Path:
        main_opts = self.compute_main_cmd_args()
        main_opts.append(path_opt_str)
        _path_str = self.runner.run_git_command(main_opts, [], check=True, text=True,
                                    capture_output=True).stdout.strip()
        return Path(_path_str)


class VersionCommand[U: GitCommand](Version[U], Protocol):
    pass


class LsTreeCommand[U: GitCommand](LsTree[U], Protocol):
    pass
