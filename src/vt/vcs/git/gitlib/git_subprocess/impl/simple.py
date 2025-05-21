#!/usr/bin/env python3
# coding=utf-8

"""
Simple and naive implementations of git commands using subprocess.
"""
from __future__ import annotations

from pathlib import Path
from typing import override

from vt.utils.commons.commons.op import RootDirOp

from vt.vcs.git.gitlib import GitCommandRunner
from vt.vcs.git.gitlib.git_subprocess import GitSubcmdCommand, GitOptsOverriderCommand, GitCommand, VersionCommand, \
    LsTreeCommand


class SimpleGitOptsOverriderCommand[T](GitOptsOverriderCommand[T]):

    def __init__(self, git: GitCommand[T]):
        self._underlying_git = git

    @property
    def underlying_git(self) -> GitCommand[T]:
        return self._underlying_git


class GitSubcmdCommandImpl[T](GitSubcmdCommand[T]):

    def __init__(self, git: GitCommand[T], git_opts_overrider: GitOptsOverriderCommand[T] | None = None):
        self._underlying_git = git
        self._overrider_git_opts = git_opts_overrider or SimpleGitOptsOverriderCommand(self.underlying_git)

    @property
    def underlying_git(self) -> GitCommand[T]:
        return self._underlying_git

    @property
    def overrider_git_opts(self) -> GitOptsOverriderCommand[T]:
        return self._overrider_git_opts


class VersionCommandImpl[T](VersionCommand[T], GitSubcmdCommandImpl['VersionCommandImpl[T]']):
    @override
    def version(self, build_options: bool = False) -> T:
        main_cmd_args = self.underlying_git.compute_main_cmd_args()
        sub_cmd_args = [VersionCommand.VERSION_CMD]
        if build_options:
            sub_cmd_args.append('--build-options')
        return self.underlying_git.runner.run_git_command(main_cmd_args, sub_cmd_args, check=True, text=True,
                                                   capture_output=True)


class LsTreeCommandImpl[T](LsTreeCommand[T], GitSubcmdCommandImpl['LsTreeCommandImpl[T]']):
    def __init__(self, root_dir: Path, git: GitCommand[T],
                 git_opts_overrider: GitOptsOverriderCommand[T] | None = None):
        super().__init__(git, git_opts_overrider)
        self._root_dir = root_dir

    @override
    def ls_tree(self, tree_ish: str, *, d: bool = False, r: bool = False, t: bool = False, long: bool = False,
                z: bool = False, name_only: bool = False, object_only: bool = False, full_name: bool = False,
                full_tree: bool = False, abbrev: int | None = None, format_: str | None = None,
                path: list[str] | None = None) -> T:
        main_cmd_args = self.underlying_git.compute_main_cmd_args()
        sub_cmd_args = [LsTreeCommand.LS_TREE_CMD]
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


class SimpleGitCommand[T](GitCommand[T], RootDirOp):

    def __init__(self, runner: GitCommandRunner[T], git_root_dir: Path = RootDirOp.from_path(), *,
                 git_version_subcmd: VersionCommand[T] | None = None,
                 ls_tree: LsTreeCommand[T] | None = None):
        super().__init__(runner)
        self.git_root_dir = git_root_dir
        self._git_version_subcmd = git_version_subcmd or VersionCommandImpl(self)
        self._ls_tree = ls_tree or LsTreeCommandImpl(self.root_dir, self)

    @override
    @property
    def git_version_subcmd(self) -> VersionCommand[T]:
        return self._git_version_subcmd

    @override
    @property
    def ls_tree(self) -> LsTreeCommand[T]:
        return self._ls_tree

    @override
    def clone(self) -> SimpleGitCommand[T]:
        return SimpleGitCommand(self.runner, self.root_dir)

    @override
    @property
    def root_dir(self) -> Path:
        return self.git_root_dir

