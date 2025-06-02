#!/usr/bin/env python3
# coding=utf-8

"""
Interfaces specific to ``git ls-tree`` subcommand.
"""
from abc import abstractmethod
from typing import Protocol, Unpack, override

from vt.vcs.git.gitlib.models import GitLsTreeOpts
from vt.vcs.git.gitlib.utils import validate_ls_tree_args


class LsTreeArgsValidator(Protocol):
    """
    The argument validator for ``git ls-tree`` subcommand.
    """

    @abstractmethod
    def validate(self, tree_ish: str, **ls_tree_opts: Unpack[GitLsTreeOpts]) -> None:
        """
        Validate arguments passed to the ls-tree() method.

        :param tree_ish: A tree-ish identifier (commit SHA, branch name, etc.).
        :param ls_tree_opts: Keyword arguments mapping to supported options for ``git ls-tree``.
        """
        ...

class UtilLsTreeArgsValidator(LsTreeArgsValidator):
    """
    Directly uses utility function ``validate_ls_tree_args()`` to perform ls_tree() arguments validation.
    """

    @override
    def validate(self, tree_ish: str, **ls_tree_opts: Unpack[GitLsTreeOpts]) -> None:
        validate_ls_tree_args(tree_ish, **ls_tree_opts)
