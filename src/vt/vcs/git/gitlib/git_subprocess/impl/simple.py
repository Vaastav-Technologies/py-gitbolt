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

from vt.vcs.git.gitlib.git_subprocess import GitCommand, VersionCommand, \
    LsTreeCommand, GitCommandRunner, VERSION_CMD, LS_TREE_CMD, GitSubcmdCommand
from vt.vcs.git.gitlib.git_subprocess.runner.simple_impl import SimpleGitCR


class GitSubcmdCommandImpl(GitSubcmdCommand, ABC):
    def __init__(self, git: GitCommand):
        self._underlying_git = git

    @property
    def underlying_git(self) -> GitCommand:
        return self._underlying_git

    def _set_underlying_git(self, git: 'GitCommand') -> None:
        self._underlying_git = git


class VersionCommandImpl(VersionCommand, GitSubcmdCommandImpl):

    @override
    def version(self, build_options: bool = False) -> str:
        main_cmd_args = self.underlying_git.compute_main_cmd_args()
        sub_cmd_args = [VERSION_CMD]
        if build_options:
            sub_cmd_args.append('--build-options')
        return self.underlying_git.runner.run_git_command(main_cmd_args, sub_cmd_args, check=True, text=True,
                                                   capture_output=True).stdout.strip()

    def clone(self) -> 'VersionCommandImpl':
        return VersionCommandImpl(self.underlying_git)


class LsTreeCommandImpl(LsTreeCommand, GitSubcmdCommandImpl):

    def __init__(self, root_dir: Path, git: GitCommand):
        super().__init__(git)
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

    def clone(self) -> 'LsTreeCommandImpl':
        return LsTreeCommandImpl(self.root_dir, self.underlying_git)


class SimpleGitCommand(GitCommand, RootDirOp):

    def __init__(self, git_root_dir: Path = Path.cwd(), runner: GitCommandRunner = SimpleGitCR(), *,
                 version_subcmd: VersionCommand | None = None,
                 ls_tree_subcmd: LsTreeCommand | None = None):
        super().__init__(runner)
        self.git_root_dir = git_root_dir
        self._version_subcmd = version_subcmd or VersionCommandImpl(self)
        self._ls_tree = ls_tree_subcmd or LsTreeCommandImpl(self.root_dir, self)

    @override
    @property
    def version_subcmd(self) -> VersionCommand:
        return self._version_subcmd

    @override
    @property
    def ls_tree_subcmd(self) -> LsTreeCommand:
        return self._ls_tree

    @override
    def clone(self) -> 'SimpleGitCommand':
        return SimpleGitCommand(self.root_dir, self.runner,
                                version_subcmd=self.version_subcmd,
                                ls_tree_subcmd=self.ls_tree_subcmd)

    @override
    @property
    def root_dir(self) -> Path:
        return self.git_root_dir
