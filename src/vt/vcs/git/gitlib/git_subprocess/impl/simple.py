#!/usr/bin/env python3
# coding=utf-8

"""
Simple and direct implementations of git commands using subprocess calls.
"""
from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import override, Self

from vt.utils.commons.commons.op import RootDirOp

from vt.vcs.git.gitlib import GitSubCommand
from vt.vcs.git.gitlib.git_subprocess import GitCommand, VersionCommand, \
    LsTreeCommand, GitCommandRunner, VERSION_CMD, LS_TREE_CMD, GitOptsOverriderCommand
from vt.vcs.git.gitlib.git_subprocess.runner.simple_impl import SimpleGitCR


class SimpleGitOptsOverriderCommand[T: 'SimpleGitCommand'](GitOptsOverriderCommand[T]):

    def __init__(self, simple_git_command: T):
        self._underlying_git = simple_git_command

    @property
    def underlying_git(self) -> GitCommand:
        return self._underlying_git


class GitSubCommandImpl[T: 'SimpleGitCommand'](GitSubCommand[T], ABC):

    def __init__(self, git: T, git_opts_overrider: GitOptsOverriderCommand[T] | None = None):
        self._underlying_git = git
        self._overrider_git_opts = git_opts_overrider or SimpleGitOptsOverriderCommand(self.underlying_git)

    @property
    def underlying_git(self) -> T:
        return self._underlying_git

    @property
    def overrider_git_opts(self) -> GitOptsOverriderCommand[T]:
        return self._overrider_git_opts


class VersionCommandImpl[T: 'SimpleGitCommand'](VersionCommand[T], GitSubCommandImpl[T]):

    @override
    def version(self, build_options: bool = False) -> str:
        main_cmd_args = self.underlying_git.compute_main_cmd_args()
        sub_cmd_args = [VERSION_CMD]
        if build_options:
            sub_cmd_args.append('--build-options')
        return self.underlying_git.runner.run_git_command(main_cmd_args, sub_cmd_args, check=True, text=True,
                                                   capture_output=True).stdout.strip()

    @override
    def _subcmd_git_override(self, git: T) -> Self:
        self._underlying_git = git
        return self.underlying_git.version_subcmd


class LsTreeCommandImpl[T: 'SimpleGitCommand'](LsTreeCommand[T], GitSubCommandImpl[T]):
    def __init__(self, root_dir: Path, git: T,
                 git_opts_overrider: GitOptsOverriderCommand[T] | None = None):
        super().__init__(git, git_opts_overrider)
        self._root_dir = root_dir

    @override
    def ls_tree(self, tree_ish: str, *, d: bool = False, r: bool = False, t: bool = False, long: bool = False,
                z: bool = False, name_only: bool = False, object_only: bool = False, full_name: bool = False,
                full_tree: bool = False, abbrev: int | None = None, format_: str | None = None,
                path: list[str] | None = None) -> str:
        main_cmd_args = self.underlying_git.compute_main_cmd_args()
        sub_cmd_args = [LS_TREE_CMD]
        # Add boolean flags
        if d:
            sub_cmd_args.append('-d')
        if r:
            sub_cmd_args.append('-r')
        if t:
            sub_cmd_args.append('-t')
        if long:
            sub_cmd_args.append('-l')
        if z:
            sub_cmd_args.append('-z')
        if name_only:
            sub_cmd_args.append('--name-only')
        if object_only:
            sub_cmd_args.append('--object-only')
        if full_name:
            sub_cmd_args.append('--full-name')
        if full_tree:
            sub_cmd_args.append('--full-tree')

        # Add abbrev if specified
        if abbrev is not None:
            sub_cmd_args.append(f'--abbrev={abbrev}')

        # Add format if specified
        if format_:
            sub_cmd_args.append(f'--format={format_}')

        # Add the tree-ish argument
        sub_cmd_args.append(tree_ish)

        # Add paths if provided
        if path:
            sub_cmd_args.extend(path)

        # Run the git command
        result = self.underlying_git.runner.run_git_command(
            main_cmd_args,
            sub_cmd_args,
            check=True,
            text=True,
            capture_output=True,
            cwd=self.root_dir
        )

        # Return raw stdout; parsing can be handled upstream or in a separate method
        return result.stdout.strip()  # type: ignore

    @override
    @property
    def root_dir(self) -> Path:
        return self._root_dir

    @override
    def _subcmd_git_override(self, git: T) -> Self:
        self._underlying_git = git
        return self.underlying_git.ls_tree_subcmd


class SimpleGitCommand(GitCommand, RootDirOp):

    def __init__(self, git_root_dir: Path = Path.cwd(), runner: GitCommandRunner = SimpleGitCR(), *,
                 version_subcmd: VersionCommand[Self] | None = None,
                 ls_tree_subcmd: LsTreeCommand[Self] | None = None):
        super().__init__(runner)
        self.git_root_dir = git_root_dir
        self._version_subcmd = version_subcmd or VersionCommandImpl(self)
        self._ls_tree = ls_tree_subcmd or LsTreeCommandImpl(self.root_dir, self)

    @override
    @property
    def version_subcmd(self) -> VersionCommand[Self]:
        return self._version_subcmd

    @override
    @property
    def ls_tree_subcmd(self) -> LsTreeCommand[Self]:
        return self._ls_tree

    @override
    def clone(self) -> Self:
        return SimpleGitCommand(self.root_dir, self.runner,
                                version_subcmd=self.version_subcmd,
                                ls_tree_subcmd=self.ls_tree_subcmd)

    @override
    @property
    def root_dir(self) -> Path:
        return self.git_root_dir
