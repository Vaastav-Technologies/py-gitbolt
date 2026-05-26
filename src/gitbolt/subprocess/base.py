#!/usr/bin/env python3
# coding=utf-8

"""
Git command interfaces with default implementation using subprocess calls.
"""

from __future__ import annotations

from abc import abstractmethod, ABC
from collections.abc import Callable
from contextlib import AbstractContextManager
from pathlib import Path
from subprocess import CompletedProcess, Popen, PIPE
from types import SimpleNamespace
from typing import override, Protocol, Unpack, Self, overload, Literal, Any

from vt.utils.commons.commons.core_py import is_unset, not_none_not_unset
from vt.utils.commons.commons.op import RootDirOp
from vt.utils.errors.error_specs import ERR_INVALID_USAGE

from gitbolt import Git, Version, LsTree, GitSubCommand, HasGitUnderneath, Add
from gitbolt.exceptions import GitExitingException
from gitbolt.subprocess.add import AddCLIArgsBuilder, IndividuallyOverridableACAB
from gitbolt.subprocess.ls_tree import (
    LsTreeCLIArgsBuilder,
    IndividuallyOverridableLTCAB,
)
from gitbolt.subprocess.runner import GitCommandRunner
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
        self._env_vars: GitEnvVars | None = None

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
    def build_git_envs(self) -> dict[str, str] | None:
        """
        Terminal operation to build and return effective Git environment variables
        from the merged ``GitEnvVars`` object.

        Skips values that are ``Unset`` or ``None``-like using ``not_none_not_unset()``.
        Converts ``Path`` and ``datetime`` instances to ``str``.

        :return: A cleaned and normalized GitEnvVars dict suitable for use in subprocesses.
        """
        if self._env_vars is None:
            return None
        else:
            env: dict[str, str] = {}
            for key, val in self._env_vars.items():
                if not_none_not_unset(val):
                    env[key] = str(val)
            return env

    @override
    def git_envs_override(self, **overrides: Unpack[GitEnvVars]) -> Self:
        _git_cmd = self.clone()
        if self._env_vars:
            _env_vars = merge_git_envs(overrides, self._env_vars)
        else:
            _env_vars = overrides
        _git_cmd._env_vars = _env_vars
        return _git_cmd

    # endregion

    @override
    def html_path(self) -> Path:
        html_path_str = "--html-path"
        return self._get_path(html_path_str)

    @override
    def info_path(self) -> Path:
        info_path_str = "--info-path"
        return self._get_path(info_path_str)

    @override
    def man_path(self) -> Path:
        man_path_str = "--man-path"
        return self._get_path(man_path_str)

    @override
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

        :returns: An unchecked subcommand instance that simply runs the asked command in a ``subprocess.run()`` with
            optional ``subprocess.Popen()``.
        """
        ...

    @abstractmethod
    def session(self, **commands: list[str] | Callable[[], Popen[bytes]]) -> GitSession:
        """
        Run long-running git session with multiple unchecked subcommands using ``subprocess.Popen`` and
        communicate with them.

        Client/Caller can communicate with ``GitSession``'s processes with their stdin and stdout.

        Examples:

        Obtain a session:

        >>> import gitbolt
        >>> _git = gitbolt.get_git_command()
        >>> ses = _git.session(ls_tree=["ls-tree", "HEAD"], cat_file=["cat-file", "--batch"])
        >>> with ses:   # start the session by ctx mgr
        ...     pass    # any communication can be done by Popen semantics.

        Start the session in one go:

        >>> with _git.session(cat_file=["cat-file", "--batch"]) as ses: # obtain, start and ctx manage the session.
        ...     pass    # any communication can be done by Popen semantics.

        :param commands: list of string git commands suppliable to ``subprocess.Popen`` or ``subprocess.Popen`` lambdas.
        :returns: A (not yet started) long-running ``GitSession`` context manager.
        """
        ...


class GitSession(HasGitUnderneath[GitCommand], AbstractContextManager):
    def __init__(self, git: GitCommand, **commands: Callable[[], Popen[bytes]]):
        """
        Reusable and reentrant context Manager to start a git long-running session. Useful when a command is to be
        held in open state and be communicated with its stdin and stdout. This is way faster that spawning multiple
        processes each time.

        Examples:

        Obtain a session:

        >>> import gitbolt
        >>> from gitbolt.subprocess.base import GitSession
        >>> _git = gitbolt.get_git_command()
        >>> ses = GitSession(_git, ls_tree= lambda : _git.subcmd_unchecked.popen(["ls-tree", "HEAD"], text=False),
        ...                 cat_file= lambda : _git.subcmd_unchecked.popen(["cat-file", "--batch"], text=False))
        >>> with ses:   # start the session by ctx mgr
        ...     pass    # any communication can be done by Popen semantics.

        Start the session in one go:

        >>> with GitSession(_git, cat_file= lambda : _git.subcmd_unchecked.popen(["cat-file", "--batch"], text=False)) as ses: # obtain, start and ctx manage the session.
        ...     pass    # any communication can be done by Popen semantics.

        :param git: ``gitbolt.subprocess.GitCommand`` instance.
        :param commands: commands in kwargs fashion.
        """
        self._git = git
        self.unstarted_commands: dict[str, Callable[[], Popen[bytes]]] = commands
        self.started_commands: dict[str, Popen[bytes]] = dict()
        self._commands: SimpleNamespace | None = None
        self.__started = False
        self.__done = False
        self.__depth = 0

    @override
    def __enter__(self) -> Self:
        if self.depth == 0:
            processes_started_keys: list[str] = []
            for unstarted_command_key, unstarted_command in self.unstarted_commands.items():
                self.started_commands[unstarted_command_key] = unstarted_command().__enter__()
                processes_started_keys.append(unstarted_command_key)
            self._commands = SimpleNamespace(**self.started_commands)
            for pk in processes_started_keys:
                del self.unstarted_commands[pk]
            self.__started = True
        self.__depth += 1
        return self

    @override
    @property
    def git(self) -> GitCommand:
        return self._git

    @override
    def __exit__(self, exc_type, exc_value, traceback, /) -> Literal[False]:
        self.__depth -= 1
        if self.__depth == 0:
            process_done_keys: list[str] = []
            for started_popen_key, started_popen in self.started_commands.items():
                started_popen.__exit__(exc_type, exc_value, traceback)
                process_done_keys.append(started_popen_key)
            self._commands = None
            for pk in process_done_keys:
                del self.started_commands[pk]
            self.__done = True
        return False

    @property
    def started(self) -> bool:
        """
        :returns: Whether the session has started.
        """
        return self.__started

    @property
    def done(self) -> bool:
        """
        :returns: Whether the session has completed and thus exited/closed.
        """
        return self.__done

    @property
    def active(self) -> bool:
        """
        :returns: Whether the session is currently actively running.
        """
        return self.started and not self.done

    @property
    def commands(self) -> SimpleNamespace:
        """
        :returns: All the registered commands and these can be accessed by member notations.
        :raises RuntimeError: if commands are queried when the session is inactive.
        """
        if self._commands is None or not self.active:
            raise RuntimeError("GitSession not active")
        return self._commands

    @property
    def depth(self) -> int:
        """
        :returns: The current session depth. Multilevel context managers increment the depth each y one.
        """
        return self.__depth


class GitSubcmdCommand(GitSubCommand, HasGitUnderneath["GitCommand"], Protocol):
    """
    A ``GitSubCommand`` that holds a reference to ``git`` and provides ``git_opts_override`` by default.
    """

    @override
    def git_opts_override(self, **overrides: Unpack[GitOpts]) -> Self:
        overridden_git = self.git.git_opts_override(**overrides)
        self._set_underlying_git(overridden_git)
        return self

    @override
    def git_envs_override(self, **overrides: Unpack[GitEnvVars]) -> Self:
        overridden_git = self.git.git_envs_override(**overrides)
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
    class _Cache:
        def __init__(self):
            self.version = None
            self.semver = None
            self.build_options = None

    class VersionInfoForCmd(Version.VersionInfo):
        def __init__(self, rosetta_supplier: Callable[[], str]):
            self.rosetta_supplier = rosetta_supplier
            self.rosetta: str | None = None
            self._cache = VersionCommand._Cache()

        @override
        def version(self) -> str:
            if self.rosetta is None:
                self.rosetta = self.rosetta_supplier()
            if self._cache.version is not None:
                return self._cache.version
            v_str = self.rosetta.splitlines()[0]
            self._cache.version = v_str
            return v_str

        @override
        def semver(self) -> tuple:
            if self._cache.semver is not None:
                return self._cache.semver
            t_ver = self.version().split()[-1].split(".")
            return tuple(t_ver)

        @override
        def __str__(self):
            if self.rosetta is None:
                self.rosetta = self.rosetta_supplier()
            return self.rosetta

    class VersionWithBuildInfoForCmd(VersionInfoForCmd, Version.VersionWithBuildInfo):
        def __init__(
            self, rosetta_supplier: Callable[[], str], splitter_expr: str = ": "
        ):
            super().__init__(rosetta_supplier)
            self.splitter_expr = splitter_expr

        @override
        def build_options(self) -> dict[str, str]:
            if self.rosetta is None:
                self.rosetta = self.rosetta_supplier()
            if self._cache.build_options is not None:
                return self._cache.build_options
            if not self.rosetta.splitlines()[1:]:
                errmsg = "Unable to populate build_options as possibly --build-options switch wasn't used."
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)

            self._cache.build_options = {}
            for b_str in self.rosetta.splitlines()[1:]:
                if self.splitter_expr in b_str:
                    b_k, b_v = b_str.split(self.splitter_expr)
                    self._cache.build_options[b_k] = b_v
            return self._cache.build_options


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
        main_cmd_args = self.git.build_main_cmd_args()
        env_vars = self.git.build_git_envs()

        # Run the git command
        result = self.git.runner.run_git_command(
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
        main_cmd_args = self.git.build_main_cmd_args()
        env_vars = self.git.build_git_envs()

        # Run the git command
        result = self.git.runner.run_git_command(
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

    # TODO: the static type-safety of `run()` is not correct.
    #  `run([..], text=True, _input=b'<some-str>')` is incorrect
    #  as this should raise static-type check safety issue because text=True and _input is bytes. Similarly
    #  `run([..], text=False, _input='<some-bytes>')` does not raise issue as well.
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
        main_cmd_args = self.git_main_cmd_args()
        envs_vars = self.git_envs(subprocess_run_kwargs.pop("env", None))
        cwd = subprocess_run_kwargs.pop("cwd", self.root_dir)
        capture_output = subprocess_run_kwargs.pop("capture_output", True)
        check = subprocess_run_kwargs.pop("check", True)
        # Run the git command
        result = self.git.runner.run_git_command(
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

    @overload
    def popen(
        self,
        subcommand_args: list[str],
        *popen_args: Any,
        text: Literal[True] = True,
        **popen_kwargs: Any,
    ) -> Popen[str]: ...

    @overload
    def popen(
        self,
        subcommand_args: list[str],
        *popen_args: Any,
        text: Literal[False] = False,
        **popen_kwargs: Any,
    ) -> Popen[bytes]: ...

    def popen(
        self,
        subcommand_args: list[str],
        *popen_args: Any,
        text: Literal[True, False] = False,
        **popen_kwargs: Any,
    ) -> Popen[str] | Popen[bytes]:
        """
        Open unchecked git subcommand communicable process, using ``subprocess.Popen``.

        All the arguments are congruent to ``subprocess.Popen`` and mostly passes as-is.

        :param subcommand_args: the full subcommand argument list.
        :param popen_args: additional subprocess positionals.
        :param text: ``_input`` and returns both are str if this value is ``True``. Else, bytes are considered.
        :param popen_kwargs: additional subprocess keyword arguments.

        :return: ``Popen`` capturing all the required stdout, stderr etc and streaming stdin.
        """
        main_cmd_args = self.git_main_cmd_args()
        envs_vars = self.git_envs(popen_kwargs.pop("env", None))
        cwd = popen_kwargs.pop("cwd", self.root_dir)
        stdin = popen_kwargs.pop("stdin", PIPE)
        stdout = popen_kwargs.pop("stdout", PIPE)
        stderr = popen_kwargs.pop("stderr", PIPE)
        bufsize = popen_kwargs.pop("bufsize", 0)
        # Popen the git command
        result = self.git.runner.popen_git_command(
            main_cmd_args,
            subcommand_args,
            *popen_args,
            text=text,
            env=envs_vars,
            cwd=cwd,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            bufsize=bufsize,
            **popen_kwargs,
        )
        return result

    def make_cmd(self, subcommand_args: list[str]) -> list[str]:
        """
        Make full runnable command for execution from the supplied ``subcommand_args``.

        As knowledge of the git program and the main command is encapsulated within this ``UncheckedSubcmd`` thus,
        this is a convenience method for any external entities that want to run commands in their own subprocess.

        :param subcommand_args: arguments for subcommand.
        :returns: a fully made and runnable command for some external ``subprocess`` call.
        """
        return self.git.runner.make_cmd(self.git.build_main_cmd_args(), subcommand_args)

    def git_main_cmd_args(self) -> list[str]:
        """
        Get CLI args for git main cli command.

        For example, ``--no-pager --no-advice`` is the git main command in ``git --no-pager --no-advice log master -1``.

        :return: CLI args for git main cli command.
        """
        return self.git.build_main_cmd_args()

    def git_envs(
        self, extra_git_envs: dict[str, str] | None = None
    ) -> dict[str, str] | None:
        """
        Get Git environment variables from the merged ``GitEnvVars`` object.

        Skips values that are ``Unset`` or ``None``-like using ``not_none_not_unset()``.
        Converts ``Path`` and ``datetime`` instances to ``str``.

        :param extra_git_envs: extraneous git envs supplied by the caller. These will be merged into the resultant
            git envs and then returned.
        :return: A cleaned and normalized GitEnvVars dict suitable for use in subprocesses.
        """
        env_vars = self.git.build_git_envs()
        if extra_git_envs and env_vars is not None:
            env_vars.update(extra_git_envs)
        return env_vars
