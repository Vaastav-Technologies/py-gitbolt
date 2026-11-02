#!/usr/bin/env python3
# coding=utf-8

"""
Tests for the ``git worktree`` CLI args builder.
"""
from pathlib import Path

import pytest
from vt.utils.commons.commons.core_py import UNSET, Unset

from gitbolt.subprocess.worktree import WorktreeCLIArgsBuilder


def _add_args(
    commit_ish: str | None,
    *,
    new_branch: str | Unset = UNSET,
    new_branch_force: str | Unset = UNSET,
) -> list[str]:
    """
    Build ``git worktree add`` args for the path ``wt`` with every other option left unset.
    """
    return WorktreeCLIArgsBuilder().build_add_cli_args(
        Path("wt"),
        commit_ish,
        force=UNSET,
        reforce=UNSET,
        new_branch=new_branch,
        new_branch_force=new_branch_force,
        orphan=UNSET,
        detach=UNSET,
        checkout=UNSET,
        lock=UNSET,
        reason=UNSET,
        quiet=UNSET,
        track=UNSET,
        guess_remote=UNSET,
        relative_paths=UNSET,
    )


class TestBuildAddCliArgs:
    def test_path_only(self):
        assert _add_args(None) == ["worktree", "add", "wt"]

    def test_path_and_commit_ish(self):
        assert _add_args("main") == ["worktree", "add", "wt", "main"]

    @pytest.mark.parametrize(
        "kwarg, flag", [("new_branch", "-b"), ("new_branch_force", "-B")]
    )
    def test_new_branch_carries_branch_name(self, kwarg, flag):
        assert _add_args(None, **{kwarg: "feat"}) == ["worktree", "add", flag, "feat", "wt"]

    @pytest.mark.parametrize(
        "kwarg, flag", [("new_branch", "-b"), ("new_branch_force", "-B")]
    )
    def test_new_branch_with_commit_ish(self, kwarg, flag):
        """
        The branch name is the flag's value and the commit-ish appears once, after the path.
        """
        assert _add_args("main", **{kwarg: "feat"}) == [
            "worktree", "add", flag, "feat", "wt", "main",
        ]

    @pytest.mark.parametrize("kwarg", ["new_branch", "new_branch_force"])
    def test_new_branch_rejects_non_str(self, kwarg):
        with pytest.raises(ValueError, match="branch-name value"):
            _add_args(None, **{kwarg: True})
