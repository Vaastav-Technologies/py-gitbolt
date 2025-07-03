#!/usr/bin/env python3
# coding=utf-8

"""
Simple and direct implementations of git commands using subprocess calls.
"""

from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import override

from vt.utils.commons.commons.op import RootDirOp

from gitbolt.add import AddArgsValidator
from gitbolt.git_subprocess import (
    GitCommand,
    VersionCommand,
    LsTreeCommand,
    GitSubcmdCommand,
    AddCommand,
)
from gitbolt.git_subprocess.add import AddCLIArgsBuilder
from gitbolt.git_subprocess.constants import VERSION_CMD
from gitbolt.git_subprocess.ls_tree import LsTreeCLIArgsBuilder
from gitbolt.git_subprocess.runner import GitCommandRunner
from gitbolt.git_subprocess.runner.simple_impl import SimpleGitCR
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
    @override
    def version(self, build_options: bool = False) -> str:
        self._require_valid_args(build_options)
        main_cmd_args = self.underlying_git.build_main_cmd_args()
        sub_cmd_args = [VERSION_CMD]
        if build_options:
            sub_cmd_args.append("--build-options")
        return self.underlying_git.runner.run_git_command(
            main_cmd_args, sub_cmd_args, check=True, text=True, capture_output=True
        ).stdout.strip()

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


class SimpleGitCommand(GitCommand, RootDirOp):
    def __init__(
        self,
        git_root_dir: Path = Path.cwd(),
        runner: GitCommandRunner = SimpleGitCR(),
        *,
        version_subcmd: VersionCommand | None = None,
        ls_tree_subcmd: LsTreeCommand | None = None,
        add_subcmd: AddCommand | None = None,
    ):
        super().__init__(runner)
        self.git_root_dir = git_root_dir
        self._version_subcmd = version_subcmd or VersionCommandImpl(self)
        self._ls_tree = ls_tree_subcmd or LsTreeCommandImpl(self.root_dir, self)
        self._add_subcmd = add_subcmd or AddCommandImpl(self.root_dir, self)

    @override
    @property
    def version_subcmd(self) -> VersionCommand:
        return self._version_subcmd

    @override
    @property
    def ls_tree_subcmd(self) -> LsTreeCommand:
        return self._ls_tree

    @override
    @property
    def add_subcmd(self) -> AddCommand:
        return self._add_subcmd

    @override
    def clone(self) -> "SimpleGitCommand":
        # region obtain class instance
        cloned = SimpleGitCommand(
            self.root_dir,
            self.runner,
            version_subcmd=self.version_subcmd,
            ls_tree_subcmd=self.ls_tree_subcmd,
            add_subcmd=self.add_subcmd,
        )
        # endregion
        # region clone protected members
        cloned._main_cmd_opts = self._main_cmd_opts
        cloned._env_vars = self._env_vars
        # endregion
        return cloned

    @override
    @property
    def root_dir(self) -> Path:
        return self.git_root_dir
