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

from vt.vcs.git.gitlib import Git, Version, LsTree, GitSubCommand, HasGitUnderneath, Add
from vt.vcs.git.gitlib.git_subprocess.constants import LS_TREE_CMD
from vt.vcs.git.gitlib.git_subprocess.runner import GitCommandRunner
from vt.vcs.git.gitlib.models import GitOpts, GitLsTreeOpts
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
    def git_opts_override(self, **overrides: Unpack[GitOpts]) -> Self:
        _git_cmd = self.clone()
        _main_cmd_opts = merge_git_opts(overrides, self._main_cmd_opts)
        _git_cmd._main_cmd_opts = _main_cmd_opts
        return _git_cmd

    def build_main_cmd_args(self) -> list[str]:
        """
        Terminal operation to build and return CLI args for git main cli command.

        For example, ``--no-pager --no-advice`` is the git main command in ``git --no-pager --no-advice log master -1``.

        :return: CLI args for git main cli command.
        """
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

    def _get_path(self, path_opt_str: str) -> Path:
        main_opts = self.build_main_cmd_args()
        main_opts.append(path_opt_str)
        _path_str = self.runner.run_git_command(main_opts, [], check=True, text=True,
                                    capture_output=True).stdout.strip()
        return Path(_path_str)

    @override
    @property
    @abstractmethod
    def version_subcmd(self) -> VersionCommand:
        ...

    @override
    @property
    @abstractmethod
    def ls_tree_subcmd(self) -> LsTreeCommand:
        ...

    @override
    @property
    @abstractmethod
    def add_subcmd(self) -> AddCommand:
        ...


class GitSubcmdCommand(GitSubCommand, HasGitUnderneath['GitCommand'], Protocol):
    """
    A ``GitSubCommand`` that holds a reference to ``git`` and provides ``git_opts_override`` by default.
    """

    @override
    def git_opts_override(self, **overrides: Unpack[GitOpts]) -> Self:
        overridden_git = self.underlying_git.git_opts_override(**overrides)
        self._set_underlying_git(overridden_git)
        return self

    @abstractmethod
    def _set_underlying_git(self, git: 'GitCommand') -> None:
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

    @classmethod
    def build_sub_cmd_args(cls, tree_ish: str, **ls_tree_opts: Unpack[GitLsTreeOpts]) -> list[str]:
        """
        Build the complete list of subcommand arguments to be passed to ``git ls-tree``.

        This method assembles the subcommand portion of the git command invocation, such as
        in ``git --no-pager ls-tree -r HEAD``, where ``-r HEAD`` is the subcommand argument list.

        It delegates the formation of each argument to protected helper methods to allow
        easier overriding and testing of individual components.

        Includes support for:

        - Boolean flags (e.g., -r, -t, --name-only)
        - Optional key-value arguments (e.g., --abbrev=N, --format=FMT)
        - Required tree-ish identifier
        - Optional file path list

        :param tree_ish: A tree-ish identifier (commit SHA, branch name, etc.).
        :param ls_tree_opts: Keyword arguments mapping to supported options for ``git ls-tree``.
        :return: Complete list of subcommand arguments.
        :raises GitExitingException: if undesired argument type or argument combination is supplied.


        Examples:

        >>> LsTreeCommand.build_sub_cmd_args("HEAD", r=True, abbrev=8)
        ['ls-tree', '-r', '--abbrev=8', 'HEAD']
        >>> LsTreeCommand.build_sub_cmd_args("HEAD", name_only=True, path=["src", "tests"])
        ['ls-tree', '--name-only', 'HEAD', 'src', 'tests']
        >>> LsTreeCommand.build_sub_cmd_args("HEAD")
        ['ls-tree', 'HEAD']
        >>> LsTreeCommand.build_sub_cmd_args("main", z=True, full_name=False, abbrev=0)
        ['ls-tree', '-z', '--abbrev=0', 'main']
        >>> LsTreeCommand.build_sub_cmd_args("main", z=True, full_name=False, abbrev=0, format_='%(objectname)')
        ['ls-tree', '-z', '--abbrev=0', '--format=%(objectname)', 'main']


        Exceptional input validation examples:

        >>> from vt.vcs.git.gitlib.exceptions import GitExitingException
        >>> try:
        ...     LsTreeCommand.build_sub_cmd_args(42)  # type: ignore[arg-type] # as tree_ish expects str and int is provided
        ... except GitExitingException as e:
        ...     print(e)
        TypeError: tree_ish should be a string.

        >>> try:
        ...     LsTreeCommand.build_sub_cmd_args("HEAD",
        ...         abbrev="abc")  # type: ignore[arg-type] # as abbrev expects int and str is provided
        ... except GitExitingException as e:
        ...     print(e)
        TypeError: abbrev must be an integer.

        >>> try:
        ...     LsTreeCommand.build_sub_cmd_args("HEAD",
        ...         path="src/")  # type: ignore[arg-type] # as path expects list[str] and str is provided.
        ... except GitExitingException as e:
        ...     print(e)
        TypeError: path must be a list of strings.

        >>> try:
        ...     LsTreeCommand.build_sub_cmd_args("HEAD",
        ...         z="yes")  # type: ignore[arg-type] # as z expects bool and str is provided.
        ... except GitExitingException as e:
        ...     print(e)
        TypeError: 'z' must be a boolean.
        """
        cls._require_valid_args(tree_ish, **ls_tree_opts)
        sub_cmd_args = [LS_TREE_CMD]

        sub_cmd_args.extend(cls._d_arg(ls_tree_opts.get("d")))
        sub_cmd_args.extend(cls._r_arg(ls_tree_opts.get("r")))
        sub_cmd_args.extend(cls._t_arg(ls_tree_opts.get("t")))
        sub_cmd_args.extend(cls._long_arg(ls_tree_opts.get("long")))
        sub_cmd_args.extend(cls._z_arg(ls_tree_opts.get("z")))
        sub_cmd_args.extend(cls._name_only_arg(ls_tree_opts.get("name_only")))
        sub_cmd_args.extend(cls._name_status_arg(ls_tree_opts.get("name_status")))
        sub_cmd_args.extend(cls._object_only_arg(ls_tree_opts.get("object_only")))
        sub_cmd_args.extend(cls._full_name_arg(ls_tree_opts.get("full_name")))
        sub_cmd_args.extend(cls._full_tree_arg(ls_tree_opts.get("full_tree")))

        sub_cmd_args.extend(cls._abbrev_arg(ls_tree_opts.get("abbrev")))
        sub_cmd_args.extend(cls._format_arg(ls_tree_opts.get("format_")))

        sub_cmd_args.extend(cls._tree_ish_arg(tree_ish))
        sub_cmd_args.extend(cls._path_args(ls_tree_opts.get("path")))

        return sub_cmd_args

    @classmethod
    def _d_arg(cls, d: bool | None) -> list[str]:
        """
        Return ``-d`` if `d` is True.

        :param d: Whether to include the ``-d`` option.
        :return: List containing ``-d`` if applicable.

        >>> LsTreeCommand._d_arg(True)
        ['-d']
        >>> LsTreeCommand._d_arg(False)
        []
        >>> LsTreeCommand._d_arg(None)
        []
        """
        return ['-d'] if d else []

    @classmethod
    def _r_arg(cls, r: bool | None) -> list[str]:
        """
        Return ``-r`` if `r` is True.

        :param r: Whether to include the ``-r`` option.
        :return: List containing ``-r`` if applicable.

        >>> LsTreeCommand._r_arg(True)
        ['-r']
        >>> LsTreeCommand._r_arg(False)
        []
        >>> LsTreeCommand._r_arg(None)
        []
        """
        return ['-r'] if r else []

    @classmethod
    def _t_arg(cls, t: bool | None) -> list[str]:
        """
        Return ``-t`` if `t` is True.

        :param t: Whether to include the ``-t`` option.
        :return: List containing ``-t`` if applicable.

        >>> LsTreeCommand._t_arg(True)
        ['-t']
        >>> LsTreeCommand._t_arg(False)
        []
        >>> LsTreeCommand._t_arg(None)
        []
        """
        return ['-t'] if t else []

    @classmethod
    def _long_arg(cls, long: bool | None) -> list[str]:
        """
        Return ``-l`` if `long` is True.

        :param long: Whether to include the ``-l`` option.
        :return: List containing ``-l`` if applicable.

        >>> LsTreeCommand._long_arg(True)
        ['-l']
        >>> LsTreeCommand._long_arg(False)
        []
        >>> LsTreeCommand._long_arg(None)
        []
        """
        return ['-l'] if long else []

    @classmethod
    def _z_arg(cls, z: bool | None) -> list[str]:
        """
        Return ``-z`` if `z` is True.

        :param z: Whether to include the ``-z`` option.
        :return: List containing ``-z`` if applicable.

        >>> LsTreeCommand._z_arg(True)
        ['-z']
        >>> LsTreeCommand._z_arg(False)
        []
        >>> LsTreeCommand._z_arg(None)
        []
        """
        return ['-z'] if z else []

    @classmethod
    def _name_only_arg(cls, name_only: bool | None) -> list[str]:
        """
        Return ``--name-only`` if applicable.

        >>> LsTreeCommand._name_only_arg(True)
        ['--name-only']
        >>> LsTreeCommand._name_only_arg(False)
        []
        >>> LsTreeCommand._name_only_arg(None)
        []
        """
        return ['--name-only'] if name_only else []

    @classmethod
    def _name_status_arg(cls, name_status: bool | None) -> list[str]:
        """
        Return ``--name-status`` if applicable.

        >>> LsTreeCommand._name_status_arg(True)
        ['--name-status']
        >>> LsTreeCommand._name_status_arg(False)
        []
        >>> LsTreeCommand._name_status_arg(None)
        []
        """
        return ['--name-status'] if name_status else []

    @classmethod
    def _object_only_arg(cls, object_only: bool | None) -> list[str]:
        """
        Return ``--object-only`` if applicable.

        >>> LsTreeCommand._object_only_arg(True)
        ['--object-only']
        >>> LsTreeCommand._object_only_arg(False)
        []
        >>> LsTreeCommand._object_only_arg(None)
        []
        """
        return ['--object-only'] if object_only else []

    @classmethod
    def _full_name_arg(cls, full_name: bool | None) -> list[str]:
        """
        Return ``--full-name`` if applicable.

        >>> LsTreeCommand._full_name_arg(True)
        ['--full-name']
        >>> LsTreeCommand._full_name_arg(False)
        []
        >>> LsTreeCommand._full_name_arg(None)
        []
        """
        return ['--full-name'] if full_name else []

    @classmethod
    def _full_tree_arg(cls, full_tree: bool | None) -> list[str]:
        """
        Return ``--full-tree`` if applicable.

        >>> LsTreeCommand._full_tree_arg(True)
        ['--full-tree']
        >>> LsTreeCommand._full_tree_arg(False)
        []
        >>> LsTreeCommand._full_tree_arg(None)
        []
        """
        return ['--full-tree'] if full_tree else []

    @classmethod
    def _abbrev_arg(cls, abbrev: int | None) -> list[str]:
        """
        Format ``--abbrev=N`` if `abbrev` is provided.

        :param abbrev: Abbreviation length (0-40 inclusive).
        :return: List containing formatted option or empty list.

        >>> LsTreeCommand._abbrev_arg(None)
        []
        >>> LsTreeCommand._abbrev_arg(7)
        ['--abbrev=7']
        >>> LsTreeCommand._abbrev_arg(0)
        ['--abbrev=0']
        >>> LsTreeCommand._abbrev_arg(40)
        ['--abbrev=40']
        """
        return [f'--abbrev={abbrev}'] if abbrev is not None else []

    @classmethod
    def _format_arg(cls, _format: str | None) -> list[str]:
        """
        Format ``--format=...`` if `_format` is provided.

        :param _format: A valid format string.
        :return: List containing formatted option or empty list.

        >>> LsTreeCommand._format_arg(None)
        []
        >>> LsTreeCommand._format_arg('%(objectname)')
        ['--format=%(objectname)']
        >>> LsTreeCommand._format_arg('')
        ['--format=']
        """
        return [f'--format={_format}'] if _format is not None else []

    @classmethod
    def _tree_ish_arg(cls, tree_ish: str) -> list[str]:
        """
        Return the required tree-ish identifier as a single-element list.

        This value is typically a commit SHA, branch name, tag, or other valid tree reference
        and is appended at the end of the formed git subcommand options, just before path(s).

        >>> LsTreeCommand._tree_ish_arg("HEAD")
        ['HEAD']
        >>> LsTreeCommand._tree_ish_arg("origin/main")
        ['origin/main']
        >>> LsTreeCommand._tree_ish_arg("a1b2c3d")
        ['a1b2c3d']
        >>> LsTreeCommand._tree_ish_arg("")
        ['']
        """
        return [tree_ish]

    @classmethod
    def _path_args(cls, path: list[str] | None) -> list[str]:
        """
        Return the list of paths (if any) passed to ``git ls-tree``.

        If `path` is None or an empty list, this returns an empty list.

        >>> LsTreeCommand._path_args(["src", "README.md"])
        ['src', 'README.md']
        >>> LsTreeCommand._path_args([])
        []
        >>> LsTreeCommand._path_args(None)
        []
        """
        return path if path else []


class AddCommand(Add, GitSubcmdCommand, Protocol):
    pass
