#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces for ``git ls-tree`` subcommand with default implementation for subprocess calls.
"""
from abc import abstractmethod
from typing import Protocol, Unpack, override

from vt.vcs.git.gitlib.git_subprocess.constants import LS_TREE_CMD
from vt.vcs.git.gitlib.models import GitLsTreeOpts


class LsTreeCLIArgsBuilder(Protocol):
    """
    Interface to facilitate building of cli arguments for ``git ls-tree`` subcommand.
    """

    @abstractmethod
    def build(self, tree_ish: str, **ls_tree_opts: Unpack[GitLsTreeOpts]) -> list[str]:
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
        """
        ...


class IndividuallyOverridableLTCAB(LsTreeCLIArgsBuilder):
    """
    Individually Overridable Ls Tree CLI Args Builder.

    Build CLI args to run ``git ls-tree`` subcommand in a subprocess. This class is independent in its working and
    provides interface to individually override each arg former for fine-grained control.
    """

    @override
    def build(self, tree_ish: str, **ls_tree_opts: Unpack[GitLsTreeOpts]) -> list[str]:
        sub_cmd_args = [LS_TREE_CMD]

        sub_cmd_args.extend(self.d_arg(ls_tree_opts.get("d")))
        sub_cmd_args.extend(self.r_arg(ls_tree_opts.get("r")))
        sub_cmd_args.extend(self.t_arg(ls_tree_opts.get("t")))
        sub_cmd_args.extend(self.long_arg(ls_tree_opts.get("long")))
        sub_cmd_args.extend(self.z_arg(ls_tree_opts.get("z")))
        sub_cmd_args.extend(self.name_only_arg(ls_tree_opts.get("name_only")))
        sub_cmd_args.extend(self.name_status_arg(ls_tree_opts.get("name_status")))
        sub_cmd_args.extend(self.object_only_arg(ls_tree_opts.get("object_only")))
        sub_cmd_args.extend(self.full_name_arg(ls_tree_opts.get("full_name")))
        sub_cmd_args.extend(self.full_tree_arg(ls_tree_opts.get("full_tree")))

        sub_cmd_args.extend(self.abbrev_arg(ls_tree_opts.get("abbrev")))
        sub_cmd_args.extend(self.format_arg(ls_tree_opts.get("format_")))

        sub_cmd_args.extend(self.tree_ish_arg(tree_ish))
        sub_cmd_args.extend(self.path_args(ls_tree_opts.get("path")))

        return sub_cmd_args

    def d_arg(self, d: bool | None) -> list[str]:
        """
        Return ``-d`` if `d` is True.

        :param d: Whether to include the ``-d`` option.
        :return: List containing ``-d`` if applicable.

        >>> IndividuallyOverridableLTCAB().d_arg(True)
        ['-d']
        >>> IndividuallyOverridableLTCAB().d_arg(False)
        []
        >>> IndividuallyOverridableLTCAB().d_arg(None)
        []
        """
        return ['-d'] if d else []

    def r_arg(self, r: bool | None) -> list[str]:
        """
        Return ``-r`` if `r` is True.

        :param r: Whether to include the ``-r`` option.
        :return: List containing ``-r`` if applicable.

        >>> IndividuallyOverridableLTCAB().r_arg(True)
        ['-r']
        >>> IndividuallyOverridableLTCAB().r_arg(False)
        []
        >>> IndividuallyOverridableLTCAB().r_arg(None)
        []
        """
        return ['-r'] if r else []

    def t_arg(self, t: bool | None) -> list[str]:
        """
        Return ``-t`` if `t` is True.

        :param t: Whether to include the ``-t`` option.
        :return: List containing ``-t`` if applicable.

        >>> IndividuallyOverridableLTCAB().t_arg(True)
        ['-t']
        >>> IndividuallyOverridableLTCAB().t_arg(False)
        []
        >>> IndividuallyOverridableLTCAB().t_arg(None)
        []
        """
        return ['-t'] if t else []

    def long_arg(self, long: bool | None) -> list[str]:
        """
        Return ``-l`` if `long` is True.

        :param long: Whether to include the ``-l`` option.
        :return: List containing ``-l`` if applicable.

        >>> IndividuallyOverridableLTCAB().long_arg(True)
        ['-l']
        >>> IndividuallyOverridableLTCAB().long_arg(False)
        []
        >>> IndividuallyOverridableLTCAB().long_arg(None)
        []
        """
        return ['-l'] if long else []

    def z_arg(self, z: bool | None) -> list[str]:
        """
        Return ``-z`` if `z` is True.

        :param z: Whether to include the ``-z`` option.
        :return: List containing ``-z`` if applicable.

        >>> IndividuallyOverridableLTCAB().z_arg(True)
        ['-z']
        >>> IndividuallyOverridableLTCAB().z_arg(False)
        []
        >>> IndividuallyOverridableLTCAB().z_arg(None)
        []
        """
        return ['-z'] if z else []

    def name_only_arg(self, name_only: bool | None) -> list[str]:
        """
        Return ``--name-only`` if applicable.

        >>> IndividuallyOverridableLTCAB().name_only_arg(True)
        ['--name-only']
        >>> IndividuallyOverridableLTCAB().name_only_arg(False)
        []
        >>> IndividuallyOverridableLTCAB().name_only_arg(None)
        []
        """
        return ['--name-only'] if name_only else []

    def name_status_arg(self, name_status: bool | None) -> list[str]:
        """
        Return ``--name-status`` if applicable.

        >>> IndividuallyOverridableLTCAB().name_status_arg(True)
        ['--name-status']
        >>> IndividuallyOverridableLTCAB().name_status_arg(False)
        []
        >>> IndividuallyOverridableLTCAB().name_status_arg(None)
        []
        """
        return ['--name-status'] if name_status else []

    def object_only_arg(self, object_only: bool | None) -> list[str]:
        """
        Return ``--object-only`` if applicable.

        >>> IndividuallyOverridableLTCAB().object_only_arg(True)
        ['--object-only']
        >>> IndividuallyOverridableLTCAB().object_only_arg(False)
        []
        >>> IndividuallyOverridableLTCAB().object_only_arg(None)
        []
        """
        return ['--object-only'] if object_only else []

    def full_name_arg(self, full_name: bool | None) -> list[str]:
        """
        Return ``--full-name`` if applicable.

        >>> IndividuallyOverridableLTCAB().full_name_arg(True)
        ['--full-name']
        >>> IndividuallyOverridableLTCAB().full_name_arg(False)
        []
        >>> IndividuallyOverridableLTCAB().full_name_arg(None)
        []
        """
        return ['--full-name'] if full_name else []

    def full_tree_arg(self, full_tree: bool | None) -> list[str]:
        """
        Return ``--full-tree`` if applicable.

        >>> IndividuallyOverridableLTCAB().full_tree_arg(True)
        ['--full-tree']
        >>> IndividuallyOverridableLTCAB().full_tree_arg(False)
        []
        >>> IndividuallyOverridableLTCAB().full_tree_arg(None)
        []
        """
        return ['--full-tree'] if full_tree else []

    def abbrev_arg(self, abbrev: int | None) -> list[str]:
        """
        Format ``--abbrev=N`` if `abbrev` is provided.

        :param abbrev: Abbreviation length (0-40 inclusive).
        :return: List containing formatted option or empty list.

        >>> IndividuallyOverridableLTCAB().abbrev_arg(None)
        []
        >>> IndividuallyOverridableLTCAB().abbrev_arg(7)
        ['--abbrev=7']
        >>> IndividuallyOverridableLTCAB().abbrev_arg(0)
        ['--abbrev=0']
        >>> IndividuallyOverridableLTCAB().abbrev_arg(40)
        ['--abbrev=40']
        """
        return [f'--abbrev={abbrev}'] if abbrev is not None else []

    def format_arg(self, _format: str | None) -> list[str]:
        """
        Format ``--format=...`` if `_format` is provided.

        :param _format: A valid format string.
        :return: List containing formatted option or empty list.

        >>> IndividuallyOverridableLTCAB().format_arg(None)
        []
        >>> IndividuallyOverridableLTCAB().format_arg('%(objectname)')
        ['--format=%(objectname)']
        >>> IndividuallyOverridableLTCAB().format_arg('')
        ['--format=']
        """
        return [f'--format={_format}'] if _format is not None else []

    def tree_ish_arg(self, tree_ish: str) -> list[str]:
        """
        Return the required tree-ish identifier as a single-element list.

        This value is typically a commit SHA, branch name, tag, or other valid tree reference
        and is appended at the end of the formed git subcommand options, just before path(s).

        >>> IndividuallyOverridableLTCAB().tree_ish_arg("HEAD")
        ['HEAD']
        >>> IndividuallyOverridableLTCAB().tree_ish_arg("origin/main")
        ['origin/main']
        >>> IndividuallyOverridableLTCAB().tree_ish_arg("a1b2c3d")
        ['a1b2c3d']
        >>> IndividuallyOverridableLTCAB().tree_ish_arg("")
        ['']
        """
        return [tree_ish]

    def path_args(self, path: list[str] | None) -> list[str]:
        """
        Return the list of paths (if any) passed to ``git ls-tree``.

        If `path` is None or an empty list, this returns an empty list.

        >>> IndividuallyOverridableLTCAB().path_args(["src", "README.md"])
        ['src', 'README.md']
        >>> IndividuallyOverridableLTCAB().path_args([])
        []
        >>> IndividuallyOverridableLTCAB().path_args(None)
        []
        """
        return path if path else []
