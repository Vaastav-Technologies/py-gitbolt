#!/usr/bin/env python3
# coding=utf-8

"""
Simple and direct implementations of git commands using subprocess calls.
"""

from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import override, Literal, overload

from vt.utils.commons.commons.op import RootDirOp

from gitbolt.base import Version
from gitbolt.add import AddArgsValidator
from gitbolt.subprocess import (
    GitCommand,
    VersionCommand,
    LsTreeCommand,
    GitSubcmdCommand,
    AddCommand,
    UncheckedSubcmd,
)
from gitbolt.subprocess.add import AddCLIArgsBuilder
from gitbolt.subprocess.constants import VERSION_CMD
from gitbolt.subprocess.ls_tree import LsTreeCLIArgsBuilder
from gitbolt.subprocess.runner import GitCommandRunner
from gitbolt.subprocess.runner.simple import SimpleGitCR
from gitbolt.ls_tree import LsTreeArgsValidator


class GitSubcmdCommandImpl(GitSubcmdCommand, ABC):
    def __init__(self, git: GitCommand):
        self._underlying_git = git

    @property
    def underlying_git(self) -> GitCommand:
        return self._underlying_git

    def _set_underlying_git(self, git: "GitCommand") -> None:
        self._underlying_git = git


class VersionCommandImpl(VersionCommand, GitSubcmdCommandImpl):
    @overload
    def version(self) -> Version.VersionInfo: ...

    @overload
    def version(self, build_options: Literal[True]) -> Version.VersionWithBuildInfo: ...

    @override
    def version(
        self, build_options: Literal[True, False] = False
    ) -> Version.VersionInfo | Version.VersionWithBuildInfo:
        self._require_valid_args(build_options)
        main_cmd_args = self.underlying_git.build_main_cmd_args()
        sub_cmd_args = [VERSION_CMD]
        env_vars = self.underlying_git.build_git_envs()
        if build_options:
            sub_cmd_args.append("--build-options")

        def rosetta_supplier():
            return self.underlying_git.runner.run_git_command(
                main_cmd_args,
                sub_cmd_args,
                check=True,
                text=True,
                capture_output=True,
                env=env_vars,
            ).stdout.strip()

        if build_options:
            return VersionCommand.VersionWithBuildInfoForCmd(rosetta_supplier)
        return VersionCommand.VersionInfoForCmd(rosetta_supplier)

    def clone(self) -> "VersionCommandImpl":
        return VersionCommandImpl(self.underlying_git)


class LsTreeCommandImpl(LsTreeCommand, GitSubcmdCommandImpl):
    def __init__(
        self,
        git_root_dir: Path,
        git: GitCommand,
        *,
        args_validator: LsTreeArgsValidator | None = None,
        cli_args_builder: LsTreeCLIArgsBuilder | None = None,
    ):
        """
        ``ls-tree`` cli command implementation using subprocess.

        :param git_root_dir: Path to the Git repository root.
        :param git: Underlying Git command interface.
        :param args_validator: Optional custom argument validator. If None, uses the default from superclass.
        :param cli_args_builder: Optional CLI args builder. If None, uses the default from superclass.
        """
        super().__init__(git)
        self._git_root_dir = git_root_dir
        self._args_validator = args_validator or super().args_validator
        self._cli_args_builder = cli_args_builder or super().cli_args_builder

    @override
    @property
    def root_dir(self) -> Path:
        return self._git_root_dir

    @override
    @property
    def args_validator(self) -> LsTreeArgsValidator:
        return self._args_validator

    @override
    @property
    def cli_args_builder(self) -> LsTreeCLIArgsBuilder:
        return self._cli_args_builder

    def clone(self) -> "LsTreeCommandImpl":
        return LsTreeCommandImpl(self.root_dir, self.underlying_git)


class AddCommandImpl(AddCommand, GitSubcmdCommandImpl):
    def __init__(
        self,
        root_dir: Path,
        git: GitCommand,
        *,
        args_validator: AddArgsValidator | None = None,
        cli_args_builder: AddCLIArgsBuilder | None = None,
    ):
        super().__init__(git)
        self._root_dir = root_dir
        self._args_validator = args_validator or super().args_validator
        self._cli_args_builder = cli_args_builder or super().cli_args_builder

    @override
    @property
    def root_dir(self) -> Path:
        return self._root_dir

    @override
    @property
    def args_validator(self) -> AddArgsValidator:
        return self._args_validator

    @override
    @property
    def cli_args_builder(self) -> AddCLIArgsBuilder:
        return self._cli_args_builder

    def clone(self) -> "AddCommandImpl":
        return AddCommandImpl(self.root_dir, self.underlying_git)


class UncheckedSubcmdImpl(UncheckedSubcmd, GitSubcmdCommandImpl):
    def __init__(self, root_dir: Path, git: GitCommand):
        super().__init__(git)
        self._root_dir = root_dir

    @override
    @property
    def root_dir(self) -> Path:
        return self._root_dir

    def clone(self) -> "UncheckedSubcmdImpl":
        return UncheckedSubcmdImpl(self.root_dir, self.underlying_git)


class SimpleGitCommand(GitCommand, RootDirOp):
    def __init__(
        self,
        git_root_dir: Path = Path.cwd(),
        runner: GitCommandRunner = SimpleGitCR(),
        *,
        version_subcmd: VersionCommand | None = None,
        ls_tree_subcmd: LsTreeCommand | None = None,
        add_subcmd: AddCommand | None = None,
        subcmd_unchecked: UncheckedSubcmd | None = None,
    ):
        super().__init__(runner)
        self.git_root_dir = git_root_dir
        self._version_subcmd = version_subcmd or VersionCommandImpl(self)
        self._ls_tree = ls_tree_subcmd or LsTreeCommandImpl(self.root_dir, self)
        self._add_subcmd = add_subcmd or AddCommandImpl(self.root_dir, self)
        self._subcmd_unchecked = subcmd_unchecked or UncheckedSubcmdImpl(
            self.root_dir, self
        )

    @override
    @property
    def version_subcmd(self) -> VersionCommand:
        # TODO: in all subcommand methods, find a better way to retain envs and opts rather than cloning each time
        #   and setting the underlying git.
        version_subcmd = self._version_subcmd.clone()
        version_subcmd._set_underlying_git(self)
        return version_subcmd

    @override
    @property
    def ls_tree_subcmd(self) -> LsTreeCommand:
        ls_tree_subcmd = self._ls_tree.clone()
        ls_tree_subcmd._set_underlying_git(self)
        return ls_tree_subcmd

    @override
    @property
    def add_subcmd(self) -> AddCommand:
        add_subcmd = self._add_subcmd.clone()
        add_subcmd._set_underlying_git(self)
        return add_subcmd

    @override
    def clone(self) -> SimpleGitCommand:
        # region obtain class instance
        cloned = self._subclass_clone()
        # endregion
        # region clone protected members
        cloned._main_cmd_opts = self._main_cmd_opts
        cloned._env_vars = self._env_vars
        # endregion
        return cloned

    def _subclass_clone(self) -> SimpleGitCommand:
        """
        :returns: clone as defined by the subclass.
        """
        return SimpleGitCommand(
            self.root_dir,
            self.runner,
            version_subcmd=self.version_subcmd,
            ls_tree_subcmd=self.ls_tree_subcmd,
            add_subcmd=self.add_subcmd,
            subcmd_unchecked=self.subcmd_unchecked,
        )

    @override
    @property
    def root_dir(self) -> Path:
        return self.git_root_dir

    @property
    def subcmd_unchecked(self) -> UncheckedSubcmd:
        subcmd_unchecked = self._subcmd_unchecked.clone()
        subcmd_unchecked._set_underlying_git(self)
        return subcmd_unchecked


class CLISimpleGitCommand(SimpleGitCommand):
    """
    A simple git command that can run using CLI params.
    """

    def __init__(
        self,
        git_root_dir: Path = Path.cwd(),
        runner: GitCommandRunner = SimpleGitCR(),
        *,
        opts: list[str] | None = None,
        envs: dict[str, str] | None = None,
        prefer_cli: bool = False,
        version_subcmd: VersionCommand | None = None,
        ls_tree_subcmd: LsTreeCommand | None = None,
        add_subcmd: AddCommand | None = None,
        subcmd_unchecked: UncheckedSubcmd | None = None,
    ):
        """
        :param opts: main git cli options.
        :param envs: main git cli env vars. Not supplying any env vars (default behavior: ``None``) simply supplies all
            the env vars to the underlying runner.
        :param prefer_cli: cli opts and envs will be given priority over programmatically set opts and envs. Setting
            this param to ``True`` will make cli opts and envs appear later in the opts and envs strings which will
            make them override previously programmatically set opts and envs.
        """
        super().__init__(
            git_root_dir,
            runner,
            version_subcmd=version_subcmd,
            ls_tree_subcmd=ls_tree_subcmd,
            add_subcmd=add_subcmd,
            subcmd_unchecked=subcmd_unchecked,
        )
        self._main_cmd_cli_opts = opts
        self._cmd_cli_envs = envs
        self.prefer_cli = prefer_cli

    @override
    def build_main_cmd_args(self) -> list[str]:
        if self._main_cmd_cli_opts:
            if self.prefer_cli:
                return super().build_main_cmd_args() + self._main_cmd_cli_opts
            else:
                return self._main_cmd_cli_opts + super().build_main_cmd_args()
        return super().build_main_cmd_args()

    @override
    def build_git_envs(self) -> dict[str, str] | None:
        if self._cmd_cli_envs is None:
            return super().build_git_envs()
        if self.prefer_cli:
            return (super().build_git_envs() or {}) | self._cmd_cli_envs
        else:
            return self._cmd_cli_envs | (super().build_git_envs() or {})

    @override
    def _subclass_clone(self) -> CLISimpleGitCommand:
        return CLISimpleGitCommand(
            self.root_dir,
            self.runner,
            opts=self._main_cmd_cli_opts,
            envs=self._cmd_cli_envs,
            prefer_cli=self.prefer_cli,
            version_subcmd=self.version_subcmd,
            ls_tree_subcmd=self.ls_tree_subcmd,
            add_subcmd=self.add_subcmd,
            subcmd_unchecked=self.subcmd_unchecked,
        )
