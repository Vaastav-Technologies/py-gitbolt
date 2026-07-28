#!/usr/bin/env python3
# coding=utf-8

"""
Simple and direct implementations of git commands using subprocess calls.
"""

from __future__ import annotations

from abc import ABC
from pathlib import Path
from subprocess import Popen
from typing import override, Literal, overload, Callable

from vt.utils.commons.commons.op import RootDirOp

from gitbolt.base import Version, Worktree
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
from gitbolt.subprocess.base import GitSession, WorktreeCommand
from gitbolt.subprocess.constants import VERSION_CMD
from gitbolt.subprocess.ls_tree import LsTreeCLIArgsBuilder
from gitbolt.subprocess.runner import GitCommandRunner
from gitbolt.subprocess.runner.simple import SimpleGitCR
from gitbolt.ls_tree import LsTreeArgsValidator
from gitbolt.subprocess.worktree import WorktreeCLIArgsBuilder


class GitSubcmdCommandImpl(GitSubcmdCommand, ABC):
    def __init__(self, git: GitCommand):
        self._underlying_git = git

    @property
    def git(self) -> GitCommand:
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
        main_cmd_args = self.git.build_main_cmd_args()
        sub_cmd_args = [VERSION_CMD]
        env_vars = self.git.build_git_envs()
        if build_options:
            sub_cmd_args.append("--build-options")

        def rosetta_supplier():
            return self.git.runner.run_git_command(
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
        return VersionCommandImpl(self.git)


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
        return LsTreeCommandImpl(self.root_dir, self.git)


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
        return AddCommandImpl(self.root_dir, self.git, args_validator=self.args_validator,
                              cli_args_builder=self.cli_args_builder)


class WorktreeSubcmdCommandImpl(WorktreeCommand.WorktreeSubcmdCommand):
    def __init__(self, worktree: WorktreeCommand,):
        self._underlying_worktree = worktree
        self._root_dir = self.underlying_worktree.root_dir
        self._underlying_git = worktree.git
        self._cli_args_builder = self.underlying_worktree.cli_args_builder

    @override
    @property
    def git(self) -> GitCommand:
        return self._underlying_git

    @override
    @property
    def underlying_worktree(self) -> WorktreeCommand:
        return self._underlying_worktree

    def _set_underlying_git(self, git: "GitCommand") -> None:
        self._underlying_git = git

    @property
    def root_dir(self) -> Path:
        return self._root_dir

    @property
    def cli_args_builder(self) -> WorktreeCLIArgsBuilder:
        return self._cli_args_builder


class WorktreeCommandImpl(WorktreeCommand, GitSubcmdCommandImpl):

    def __init__(
        self,
        root_dir: Path,
        git: GitCommand,
        *,
        list_subcmd: WorktreeCommand.ListCommand | None = None,
        lock_subcmd: WorktreeCommand.LockCommand | None = None,
        unlock_subcmd: WorktreeCommand.UnLockCommand | None = None,
        add_subcmd: WorktreeCommand.AddCommand | None = None,
        remove_subcmd: WorktreeCommand.RemoveCommand | None = None,
        move_subcmd: WorktreeCommand.MoveCommand | None = None,
        prune_subcmd: WorktreeCommand.PruneCommand | None = None,
        repair_subcmd: WorktreeCommand.RepairCommand | None = None,
        cli_args_builder: WorktreeCLIArgsBuilder | None = None,
    ):
        super().__init__(git)
        self._root_dir = root_dir
        self._cli_args_builder = cli_args_builder or super().cli_args_builder
        self._list_subcmd = list_subcmd or WorktreeCommandImpl.ListCommandImpl(self)
        self._lock_subcmd = lock_subcmd or WorktreeCommandImpl.LockCommandImpl(self)
        self._unlock_subcmd = unlock_subcmd or WorktreeCommandImpl.UnLockCommandImpl(self)
        self._add_subcmd = add_subcmd or WorktreeCommandImpl.AddCommandImpl(self)
        self._remove_subcmd = remove_subcmd or WorktreeCommandImpl.RemoveCommandImpl(self)
        self._move_subcmd = move_subcmd or WorktreeCommandImpl.MoveCommandImpl(self)
        self._prune_subcmd = prune_subcmd or WorktreeCommandImpl.PruneCommandImpl(self)
        self._repair_subcmd = repair_subcmd or WorktreeCommandImpl.RepairCommandImpl(self)

    class ListCommandImpl(WorktreeCommand.ListCommand, WorktreeSubcmdCommandImpl):
        pass

    class LockCommandImpl(WorktreeCommand.LockCommand, WorktreeSubcmdCommandImpl):
        pass

    class UnLockCommandImpl(WorktreeCommand.UnLockCommand, WorktreeSubcmdCommandImpl):
        pass

    class AddCommandImpl(WorktreeCommand.AddCommand, WorktreeSubcmdCommandImpl):
        pass

    class RemoveCommandImpl(WorktreeCommand.RemoveCommand, WorktreeSubcmdCommandImpl):
        pass

    class MoveCommandImpl(WorktreeCommand.MoveCommand, WorktreeSubcmdCommandImpl):
        pass

    class PruneCommandImpl(WorktreeCommand.PruneCommand, WorktreeSubcmdCommandImpl):
        pass

    class RepairCommandImpl(WorktreeCommand.RepairCommand, WorktreeSubcmdCommandImpl):
        pass

    @override
    @property
    def list_subcmd(self) -> WorktreeCommand.ListCommand:
        return self._list_subcmd

    @override
    @property
    def lock_subcmd(self) -> WorktreeCommand.LockCommand:
        return self._lock_subcmd

    @override
    @property
    def unlock_subcmd(self) -> WorktreeCommand.UnLockCommand:
        return self._unlock_subcmd

    @override
    @property
    def move_subcmd(self) -> WorktreeCommand.MoveCommand:
        return self._move_subcmd

    @override
    @property
    def prune_subcmd(self) -> WorktreeCommand.PruneCommand:
        return self._prune_subcmd

    @override
    @property
    def remove_subcmd(self) -> WorktreeCommand.RemoveCommand:
        return self._remove_subcmd

    @override
    @property
    def repair_subcmd(self) -> WorktreeCommand.RepairCommand:
        return self._repair_subcmd

    @override
    @property
    def add_subcmd(self) -> WorktreeCommand.AddCommand:
        return self._add_subcmd

    @override
    @property
    def root_dir(self) -> Path:
        return self._root_dir

    @override
    @property
    def cli_args_builder(self) -> WorktreeCLIArgsBuilder:
        return self._cli_args_builder

    def clone(self) -> "WorktreeCommandImpl":
        return WorktreeCommandImpl(self.root_dir, self.git)


class UncheckedSubcmdImpl(UncheckedSubcmd, GitSubcmdCommandImpl):
    def __init__(self, root_dir: Path, git: GitCommand):
        super().__init__(git)
        self._root_dir = root_dir

    @override
    @property
    def root_dir(self) -> Path:
        return self._root_dir

    def clone(self) -> "UncheckedSubcmdImpl":
        return UncheckedSubcmdImpl(self.root_dir, self.git)


class SimpleGitCommand(GitCommand, RootDirOp):

    def __init__(
        self,
        git_root_dir: Path = Path.cwd(),
        runner: GitCommandRunner = SimpleGitCR(),
        *,
        version_subcmd: VersionCommand | None = None,
        ls_tree_subcmd: LsTreeCommand | None = None,
        add_subcmd: AddCommand | None = None,
        worktree_subcmd: WorktreeCommand | None = None,
        subcmd_unchecked: UncheckedSubcmd | None = None,
    ):
        super().__init__(runner)
        self.git_root_dir = git_root_dir
        self._version_subcmd = version_subcmd or VersionCommandImpl(self)
        self._ls_tree = ls_tree_subcmd or LsTreeCommandImpl(self.root_dir, self)
        self._add_subcmd = add_subcmd or AddCommandImpl(self.root_dir, self)
        self._worktree_subcmd = worktree_subcmd or WorktreeCommandImpl(self.root_dir, self)
        self._subcmd_unchecked = subcmd_unchecked or UncheckedSubcmdImpl(self.root_dir, self)

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
    @property
    def worktree_subcmd(self) -> WorktreeCommand:
        worktree_subcmd = self._worktree_subcmd.clone()
        worktree_subcmd._set_underlying_git(self)
        return worktree_subcmd

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
            worktree_subcmd=self.worktree_subcmd,
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

    def session(self, **commands: list[str] | Callable[[], Popen[bytes]]) -> GitSession:
        cmds: dict[str, Callable[[], Popen[bytes]]] = {}

        # curb the lambda-late-binding-trap
        # resource: https://medium.com/skiller-whale/late-binding-variables-its-a-trap-c17af980164f
        def lambda_for_subcmd_popen(_runnable_cmd: list[str]):
            return lambda: self.subcmd_unchecked.popen(_runnable_cmd)

        for cmd_name, runnable_cmd in commands.items():
            if callable(runnable_cmd):
                cmds[cmd_name] = runnable_cmd
            else:
                cmds[cmd_name] = lambda_for_subcmd_popen(runnable_cmd)
        return GitSession(self, **cmds)


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
        worktree_subcmd: WorktreeCommand | None = None,
        subcmd_unchecked: UncheckedSubcmd | None = None,
    ):
        """
        :param opts: main git cli options.
        :param envs: main git cli environment variables (env vars). Not supplying any env
            vars (default behavior: ``None``) simply supplies all the env vars to the underlying runner.
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
            worktree_subcmd=worktree_subcmd,
            subcmd_unchecked=subcmd_unchecked,
        )
        self._main_cmd_cli_opts = opts
        self._cmd_cli_envs = envs
        self.prefer_cli = prefer_cli

    @override
    def build_main_cmd_args(self) -> list[str]:
        if self._main_cmd_cli_opts:
            if self.prefer_cli:
                return self.clean_cap_c(super().build_main_cmd_args()) + self._main_cmd_cli_opts
            else:
                return self._main_cmd_cli_opts + self.clean_cap_c(super().build_main_cmd_args())
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
            worktree_subcmd=self.worktree_subcmd,
            subcmd_unchecked=self.subcmd_unchecked,
        )

    def clean_cap_c(self, main_opts: list[str]) -> list[str]:
        """
        Clean the cap C of -C CLI options from the CLI command list.

        :param main_opts: git CLI command options.
        :returns: command line options with -C options and its values removed.
        """
        cap_c_indices: list[int] = []
        try:
            while found_index := main_opts.index("-C"):
                cap_c_indices.append(found_index)
            for cap_c_index in reversed(cap_c_indices):
                del main_opts[cap_c_index+1]
                del main_opts[cap_c_index]
        except ValueError:
            # didn't find -C or done finding -C
            pass
        return main_opts
