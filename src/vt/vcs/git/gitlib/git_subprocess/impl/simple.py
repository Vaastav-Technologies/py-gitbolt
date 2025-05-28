#!/usr/bin/env python3
# coding=utf-8

"""
Simple and direct implementations of git commands using subprocess calls.
"""
from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import override, Literal, overload, Unpack

from vt.utils.commons.commons.op import RootDirOp
from vt.utils.errors.error_specs import ERR_INVALID_USAGE

from vt.vcs.git.gitlib import errmsg_creator
from vt.vcs.git.gitlib.exceptions import GitExitingException
from vt.vcs.git.gitlib.git_subprocess import GitCommand, VersionCommand, \
    LsTreeCommand, VERSION_CMD, LS_TREE_CMD, GitSubcmdCommand, AddCommand, ADD_CMD
from vt.vcs.git.gitlib.git_subprocess.runner import GitCommandRunner
from vt.vcs.git.gitlib.git_subprocess.runner.simple_impl import SimpleGitCR
from vt.vcs.git.gitlib.models import GitAddOpts, GitLsTreeOpts


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
        self.require_valid_args(build_options)
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
    def ls_tree(self, tree_ish: str, **ls_tree_opts: Unpack[GitLsTreeOpts]) -> str:
        self._require_valid_args(tree_ish, **ls_tree_opts)
        main_cmd_args = self.underlying_git.compute_main_cmd_args()
        sub_cmd_args = [LS_TREE_CMD]

        # Boolean flags
        if ls_tree_opts.get('d'):
            sub_cmd_args.append('-d')
        if ls_tree_opts.get('r'):
            sub_cmd_args.append('-r')
        if ls_tree_opts.get('t'):
            sub_cmd_args.append('-t')
        if ls_tree_opts.get('long'):
            sub_cmd_args.append('-l')
        if ls_tree_opts.get('z'):
            sub_cmd_args.append('-z')
        if ls_tree_opts.get('name_only'):
            sub_cmd_args.append('--name-only')
        if ls_tree_opts.get('name_status'):
            sub_cmd_args.append('--name-status')
        if ls_tree_opts.get('object_only'):
            sub_cmd_args.append('--object-only')
        if ls_tree_opts.get('full_name'):
            sub_cmd_args.append('--full-name')
        if ls_tree_opts.get('full_tree'):
            sub_cmd_args.append('--full-tree')

        # Optional arguments with values
        abbrev = ls_tree_opts.get('abbrev')
        if abbrev is not None:
            sub_cmd_args.append(f'--abbrev={abbrev}')

        format_ = ls_tree_opts.get('format_')
        if format_ is not None:
            sub_cmd_args.append(f'--format={format_}')

        # Required positional argument
        sub_cmd_args.append(tree_ish)

        # Optional path list
        path = ls_tree_opts.get('path')
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

        return result.stdout.strip()

    @override
    @property
    def root_dir(self) -> Path:
        return self._root_dir

    def clone(self) -> 'LsTreeCommandImpl':
        return LsTreeCommandImpl(self.root_dir, self.underlying_git)


class AddCommandImpl(AddCommand, GitSubcmdCommandImpl):

    def __init__(self, root_dir: Path, git: GitCommand):
        super().__init__(git)
        self._root_dir = root_dir

    # TODO: check why PyCharm says that add() signature is incompatible with base class but mypy says okay.

    @override
    @overload
    def add(
        self,
        pathspec: list[str],
        **add_opts: Unpack[GitAddOpts]
    ) -> str:
        """
        Add files specified by a list of pathspec strings.
        `pathspec_from_file` and `pathspec_file_null` are disallowed here.

        Mirrors the parameters of ``git add`` CLI command
        from `git add documentation <https://git-scm.com/docs/git-add>`_.
        """

    @override
    @overload
    def add(
        self,
        *,
        pathspec_from_file: Path,
        pathspec_file_null: bool = False,
        **add_opts: Unpack[GitAddOpts]
    ) -> str:
        """
        Add files listed in a file (`pathspec_from_file`) to the index.
        `pathspec_file_null` indicates if the file is NUL terminated.
        No explicit pathspec list is allowed in this overload.

        Mirrors the parameters of ``git add`` CLI command
        from `git add documentation <https://git-scm.com/docs/git-add>`_.
        """

    @override
    @overload
    def add(
        self,
        *,
        pathspec_from_file: Literal["-"],
        pathspec_stdin: str,
        pathspec_file_null: bool = False,
        **add_opts: Unpack[GitAddOpts]
    ) -> str:
        """
        Add files listed from stdin (when `pathspec_from_file` is '-').
        The `pathspec_stdin` argument is the string content piped to stdin.

        Mirrors the parameters of ``git add`` CLI command
        from `git add documentation <https://git-scm.com/docs/git-add>`_.
        """

    @override
    def add(
            self,
            pathspec: list[str] | None = None,
            *,
            pathspec_from_file: Path | Literal["-"] | None = None,
            pathspec_stdin: str | None = None,
            pathspec_file_null: bool = False,
            **add_opts: Unpack[GitAddOpts]
    ) -> str:
        # Exclusive argument checks
        if pathspec is not None and pathspec_from_file is not None:
            errmsg = errmsg_creator.not_allowed_together('pathspec', 'pathspec_from_file')
            raise GitExitingException(errmsg, exit_code=ERR_INVALID_USAGE) from ValueError(errmsg)
        if pathspec is not None and pathspec_stdin is not None:
            errmsg = errmsg_creator.not_allowed_together('pathspec', 'pathspec_stdin')
            raise GitExitingException(errmsg, exit_code=ERR_INVALID_USAGE) from ValueError(errmsg)
        if pathspec_from_file == "-" and pathspec_stdin is None:
            errmsg = errmsg_creator.all_required('pathspec_stdin', 'pathspec_from_file',
                                                 suffix=" when pathspec_from_file is '-'.")
            raise GitExitingException(errmsg, exit_code=ERR_INVALID_USAGE) from ValueError(errmsg)
        if pathspec_from_file != '-' and pathspec_stdin is not None:
            errmsg = errmsg_creator.not_allowed_together('pathspec_form_file', 'pathspec_stdin',
                                                         suffix=" when pathspec_from_file is not equal to '-'.")
            raise GitExitingException(errmsg, exit_code=ERR_INVALID_USAGE) from ValueError(errmsg)

        main_cmd_args = self.underlying_git.compute_main_cmd_args()
        sub_cmd_args = [ADD_CMD]

        # Add flags based on truthy value
        if add_opts.get("verbose"):
            sub_cmd_args.append("--verbose")
        if add_opts.get("dry_run"):
            sub_cmd_args.append("--dry-run")
        if add_opts.get("force"):
            sub_cmd_args.append("--force")
        if add_opts.get("interactive"):
            sub_cmd_args.append("--interactive")
        if add_opts.get("patch"):
            sub_cmd_args.append("--patch")
        if add_opts.get("edit"):
            sub_cmd_args.append("--edit")
        if add_opts.get("sparse"):
            sub_cmd_args.append("--sparse")
        if add_opts.get("intent_to_add"):
            sub_cmd_args.append("--intent-to-add")
        if add_opts.get("refresh"):
            sub_cmd_args.append("--refresh")
        if add_opts.get("ignore_errors"):
            sub_cmd_args.append("--ignore-errors")
        if add_opts.get("ignore_missing"):
            sub_cmd_args.append("--ignore-missing")
        if add_opts.get("renormalize"):
            sub_cmd_args.append("--renormalize")

        # Handle conditional bool | None flags
        no_all = add_opts.get("no_all")
        if no_all is True:
            sub_cmd_args.append("--no-all")
        elif no_all is False:
            sub_cmd_args.append("--all")

        no_ignore_removal = add_opts.get("no_ignore_removal")
        if no_ignore_removal is True:
            sub_cmd_args.append("--no-ignore-removal")
        elif no_ignore_removal is False:
            sub_cmd_args.append("--ignore-removal")

        chmod = add_opts.get("chmod")
        if chmod is not None:
            sub_cmd_args.append(f"--chmod={chmod}")

        # Handle pathspec argument sets
        input_data = None
        if pathspec_from_file is not None:
            sub_cmd_args.append(f"--pathspec-from-file={str(pathspec_from_file)}")
            if pathspec_file_null:
                sub_cmd_args.append("--pathspec-file-nul")
            if pathspec_from_file == "-":
                input_data = pathspec_stdin
        elif pathspec is not None:
            sub_cmd_args.extend(pathspec)
        else:
            errmsg = errmsg_creator.at_least_one_required('pathspec', 'pathspec_from_file',
                                                 "'pathspec_stdin' when pathspec_from_file=-")
            raise GitExitingException(errmsg, exit_code=ERR_INVALID_USAGE) from ValueError(errmsg)

        result = self.underlying_git.runner.run_git_command(
            main_cmd_args,
            sub_cmd_args,
            _input=input_data,
            check=True,
            text=True,
            capture_output=True,
            cwd=self._root_dir,
        )

        return result.stdout.strip()

    @override
    @property
    def root_dir(self) -> Path:
        return self._root_dir

    def clone(self) -> 'AddCommandImpl':
        return AddCommandImpl(self.root_dir, self.underlying_git)


class SimpleGitCommand(GitCommand, RootDirOp):

    def __init__(self, git_root_dir: Path = Path.cwd(), runner: GitCommandRunner = SimpleGitCR(), *,
                 version_subcmd: VersionCommand | None = None,
                 ls_tree_subcmd: LsTreeCommand | None = None,
                 add_subcmd: AddCommand | None = None):
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
    def clone(self) -> 'SimpleGitCommand':
        return SimpleGitCommand(self.root_dir, self.runner,
                                version_subcmd=self.version_subcmd,
                                ls_tree_subcmd=self.ls_tree_subcmd,
                                add_subcmd=self.add_subcmd)

    @override
    @property
    def root_dir(self) -> Path:
        return self.git_root_dir
