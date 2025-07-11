#!/usr/bin/env python3
# coding=utf-8

"""
Git command interfaces with default implementation using subprocess calls.
"""

from __future__ import annotations

from abc import abstractmethod, ABC
from pathlib import Path
from subprocess import CompletedProcess
from typing import override, Protocol, Unpack, Self, overload, Literal, Any

from vt.utils.commons.commons.core_py import is_unset, not_none_not_unset
from vt.utils.commons.commons.op import RootDirOp

from gitbolt import Git, Version, LsTree, GitSubCommand, HasGitUnderneath, Add
from gitbolt.git_subprocess.add import AddCLIArgsBuilder, IndividuallyOverridableACAB
from gitbolt.git_subprocess.ls_tree import (
    LsTreeCLIArgsBuilder,
    IndividuallyOverridableLTCAB,
)
from gitbolt.git_subprocess.runner import GitCommandRunner
from gitbolt.models import GitOpts, GitLsTreeOpts, GitAddOpts, GitEnvVars
from gitbolt.utils import merge_git_opts, merge_git_envs


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
        self._env_vars: GitEnvVars = {}

    # region build_main_cmd_args
    def build_main_cmd_args(self) -> list[str]:
        """
        Terminal operation to build and return CLI args for git main cli command.

        For example, ``--no-pager --no-advice`` is the git main command in ``git --no-pager --no-advice log master -1``.

        :return: CLI args for git main cli command.
        """
        return (
            self._main_cmd_cap_c_args()
            + self._main_cmd_small_c_args()
            + self._main_cmd_config_env_args()
            + self._main_cmd_exec_path_args()
            + self._main_cmd_paginate_args()
            + self._main_cmd_no_pager_args()
            + self._main_cmd_git_dir_args()
            + self._main_cmd_work_tree_args()
            + self._main_cmd_namespace_args()
            + self._main_cmd_bare_args()
            + self._main_cmd_no_replace_objects_args()
            + self._main_cmd_no_lazy_fetch_args()
            + self._main_cmd_no_optional_locks_args()
            + self._main_cmd_no_advice_args()
            + self._main_cmd_literal_pathspecs_args()
            + self._main_cmd_glob_pathspecs_args()
            + self._main_cmd_noglob_pathspecs_args()
            + self._main_cmd_icase_pathspecs_args()
            + self._main_cmd_list_cmds_args()
            + self._main_cmd_attr_source_args()
        )

    @override
    def git_opts_override(self, **overrides: Unpack[GitOpts]) -> Self:
        _git_cmd = self.clone()
        _main_cmd_opts = merge_git_opts(overrides, self._main_cmd_opts)
        _git_cmd._main_cmd_opts = _main_cmd_opts
        return _git_cmd

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
                if v is True or v is None:  # treat None as True
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
            return [
                item for k, v in val.items() for item in ["--config-env", f"{k}={v}"]
            ]
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

    # endregion

    # region build_git_envs
    def build_git_envs(self) -> dict[str, str]:
        """
        Terminal operation to build and return effective Git environment variables
        from the merged ``GitEnvVars`` object.

        Skips values that are ``Unset`` or ``None``-like using ``not_none_not_unset()``.
        Converts ``Path`` and ``datetime`` instances to ``str``.

        :return: A cleaned and normalized GitEnvVars dict suitable for use in subprocesses.
        """
        env: dict[str, str] = {}
        for key, val in self._env_vars.items():
            if not_none_not_unset(val):
                env[key] = str(val)
        return env

    @override
    def git_envs_override(self, **overrides: Unpack[GitEnvVars]) -> Self:
        _git_cmd = self.clone()
        _env_vars = merge_git_envs(overrides, self._env_vars)
        _git_cmd._env_vars = _env_vars
        return _git_cmd

    # endregion

    @override
    @property
    def html_path(self) -> Path:
        html_path_str = "--html-path"
        return self._get_path(html_path_str)

    @override
    @property
    def info_path(self) -> Path:
        info_path_str = "--info-path"
        return self._get_path(info_path_str)

    @override
    @property
    def man_path(self) -> Path:
        man_path_str = "--man-path"
        return self._get_path(man_path_str)

    @override
    @property
    def exec_path(self) -> Path:
        exec_path_str = "--exec-path"
        return self._get_path(exec_path_str)

    def _get_path(self, path_opt_str: str) -> Path:
        main_opts = self.build_main_cmd_args()
        main_opts.append(path_opt_str)
        _path_str = self.runner.run_git_command(
            main_opts, [], check=True, text=True, capture_output=True
        ).stdout.strip()
        return Path(_path_str)

    @override
    @property
    @abstractmethod
    def version_subcmd(self) -> VersionCommand: ...

    @override
    @property
    @abstractmethod
    def ls_tree_subcmd(self) -> LsTreeCommand: ...

    @override
    @property
    @abstractmethod
    def add_subcmd(self) -> AddCommand: ...

    @property
    @abstractmethod
    def subcmd_unchecked(self) -> UncheckedSubcmd:
        """
        Run an unchecked git subcommand using subprocess.
        """
        ...


class GitSubcmdCommand(GitSubCommand, HasGitUnderneath["GitCommand"], Protocol):
    """
    A ``GitSubCommand`` that holds a reference to ``git`` and provides ``git_opts_override`` by default.
    """

    @override
    def git_opts_override(self, **overrides: Unpack[GitOpts]) -> Self:
        overridden_git = self.underlying_git.git_opts_override(**overrides)
        self._set_underlying_git(overridden_git)
        return self

    @override
    def git_envs_override(self, **overrides: Unpack[GitEnvVars]) -> Self:
        overridden_git = self.underlying_git.git_envs_override(**overrides)
        self._set_underlying_git(overridden_git)
        return self

    @abstractmethod
    def _set_underlying_git(self, git: "GitCommand") -> None:
        """
        Protected. Designed to be overridden not called publicly.

        Set the `_underlying_git` in the derived class.

        :param git: git to override current class's `underlying_git` to.
        """
        ...


class VersionCommand(Version, GitSubcmdCommand, Protocol):
    pass


class LsTreeCommand(LsTree, GitSubcmdCommand, Protocol):
    """
    A composable class for building arguments for the `git ls-tree` subcommand, which is run later in a subprocess.

    Intended usage includes CLI tooling, scripting, or Git plumbing automation, especially in
    contexts where it's useful to dynamically generate Git commands.
    """

    @override
    def ls_tree(self, tree_ish: str, **ls_tree_opts: Unpack[GitLsTreeOpts]) -> str:
        self.args_validator.validate(tree_ish, **ls_tree_opts)
        sub_cmd_args = self.cli_args_builder.build(tree_ish, **ls_tree_opts)
        main_cmd_args = self.underlying_git.build_main_cmd_args()
        env_vars = self.underlying_git.build_git_envs()

        # Run the git command
        result = self.underlying_git.runner.run_git_command(
            main_cmd_args,
            sub_cmd_args,
            check=True,
            text=True,
            capture_output=True,
            cwd=self.root_dir,
            env=env_vars,
        )

        return result.stdout.strip()

    @property
    def cli_args_builder(self) -> LsTreeCLIArgsBuilder:
        """
        The builder assembles the subcommand CLI portion of the git command invocation, such as
        in ``git --no-pager ls-tree -r HEAD``, where ``-r HEAD`` is the subcommand argument list.

        :return: Builder the complete list of subcommand CLI arguments to be passed to ``git ls-tree`` subprocess.
        """
        return IndividuallyOverridableLTCAB()


class AddCommand(Add, GitSubcmdCommand, Protocol):
    # TODO: check why PyCharm says that add() signature is incompatible with base class but mypy says okay.

    @override
    @overload
    def add(
        self, pathspec: str, *pathspecs: str, **add_opts: Unpack[GitAddOpts]
    ) -> str: ...

    @override
    @overload
    def add(
        self,
        *,
        pathspec_from_file: Path,
        pathspec_file_nul: bool = False,
        **add_opts: Unpack[GitAddOpts],
    ) -> str: ...

    @override
    @overload
    def add(
        self,
        *,
        pathspec_from_file: Literal["-"],
        pathspec_stdin: str,
        pathspec_file_nul: bool = False,
        **add_opts: Unpack[GitAddOpts],
    ) -> str: ...

    @override
    def add(
        self,
        pathspec: str | None = None,
        *pathspecs: str,
        pathspec_from_file: Path | Literal["-"] | None = None,
        pathspec_stdin: str | None = None,
        pathspec_file_nul: bool = False,
        **add_opts: Unpack[GitAddOpts],
    ) -> str:
        self.args_validator.validate(
            pathspec,
            *pathspecs,
            pathspec_from_file=pathspec_from_file,
            pathspec_stdin=pathspec_stdin,
            pathspec_file_nul=pathspec_file_nul,
            **add_opts,
        )
        sub_cmd_args = self.cli_args_builder.build(
            pathspec,
            *pathspecs,
            pathspec_from_file=pathspec_from_file,
            pathspec_file_nul=pathspec_file_nul,
            **add_opts,
        )
        main_cmd_args = self.underlying_git.build_main_cmd_args()
        env_vars = self.underlying_git.build_git_envs()

        # Run the git command
        result = self.underlying_git.runner.run_git_command(
            main_cmd_args,
            sub_cmd_args,
            _input=pathspec_stdin,
            check=True,
            text=True,
            capture_output=True,
            cwd=self.root_dir,
            env=env_vars,
        )

        return result.stdout.strip()

    @property
    def cli_args_builder(self) -> AddCLIArgsBuilder:
        """
        The builder assembles the subcommand CLI portion of the git command invocation, such as
        in ``git --no-pager add --ignore-missing add-file.py``, where ``--ignore-missing add-file.py`` is the
        subcommand argument list.

        :return: Builder the complete list of subcommand CLI arguments to be passed to ``git add`` subprocess.
        """
        return IndividuallyOverridableACAB()


class UncheckedSubcmd(GitSubcmdCommand, RootDirOp, Protocol):
    """
    Unchecked git subcommand. Runs subcommands directly in subprocess.
    """

    @override
    def _subcmd_from_git(self, git: "Git") -> Self:
        return self

    @overload
    def run(
        self,
        subcommand_args: list[str],
        *subprocess_run_args: Any,
        _input: str,
        text: Literal[True],
        **subprocess_run_kwargs: Any,
    ) -> CompletedProcess[str]: ...

    @overload
    def run(
        self,
        subcommand_args: list[str],
        *subprocess_run_args: Any,
        _input: bytes,
        text: Literal[False],
        **subprocess_run_kwargs: Any,
    ) -> CompletedProcess[bytes]: ...

    @overload
    def run(
        self,
        subcommand_args: list[str],
        *subprocess_run_args: Any,
        text: Literal[True],
        **subprocess_run_kwargs: Any,
    ) -> CompletedProcess[str]: ...

    @overload
    def run(
        self,
        subcommand_args: list[str],
        *subprocess_run_args: Any,
        text: Literal[False] = ...,
        **subprocess_run_kwargs: Any,
    ) -> CompletedProcess[bytes]: ...

    def run(
        self,
        subcommand_args: list[str],
        *subprocess_run_args: Any,
        _input: str | bytes | None = None,
        text: Literal[True, False] = False,
        **subprocess_run_kwargs,
    ) -> CompletedProcess[str] | CompletedProcess[bytes]:
        """
        Run unchecked git subcommand using subprocess

        :param subcommand_args: the full subcommand argument list.
        :param subprocess_run_args: additional subprocess positionals.
        :param _input: any stdin to be passed to the subprocess.
        :param text: ``_input`` and returns both are str if this value is ``True``. Else, bytes are considered.
        :param subprocess_run_kwargs: additional subprocess keyword arguments.

        :return: ``CompletedProcess`` capturing all the required stdout, stderr, return-code etc.
        """
        main_cmd_args = self.underlying_git.build_main_cmd_args()
        envs_vars = self.underlying_git.build_git_envs()
        another_supplied_env = subprocess_run_kwargs.pop("env", None)
        if another_supplied_env:
            envs_vars.update(another_supplied_env)
        cwd = subprocess_run_kwargs.pop("cwd", None) or self.root_dir
        capture_output = subprocess_run_kwargs.pop("capture_output", None) or True
        check = subprocess_run_kwargs.pop("check", None) or True
        # Run the git command
        result = self.underlying_git.runner.run_git_command(
            main_cmd_args,
            subcommand_args,
            *subprocess_run_args,
            _input=_input,
            text=text,
            env=envs_vars,
            cwd=cwd,
            capture_output=capture_output,
            check=check,
            **subprocess_run_kwargs,
        )
        return result
