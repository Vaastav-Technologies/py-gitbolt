#!/usr/bin/env python3
# coding=utf-8

"""
Tests for ordered merge utilities (issue #2) and patch coverage of edge branches.
"""

from pathlib import Path
from typing import cast

from vt.utils.commons.commons.core_py import UNSET

from gitbolt.models import GitEnvVars, GitOpts
from gitbolt.subprocess.impl.simple import SimpleGitCommand
from gitbolt.utils import merge_git_envs, merge_git_opts


def test_merge_git_opts_preserves_primary_kwargs_order():
    merged = merge_git_opts(
        cast(
            GitOpts,
            {"exec_path": Path("some/path"), "C": [Path("path"), Path("to/repo")]},
        ),
        cast(GitOpts, {}),
    )
    assert list(merged.keys()) == ["exec_path", "C"]


def test_merge_git_opts_omits_unset_in_primary_when_omit_unset_keys():
    merged = merge_git_opts(
        cast(GitOpts, {"paginate": UNSET}),
        cast(GitOpts, {"paginate": True}),
    )
    assert "paginate" not in merged


def test_merge_git_opts_omits_unset_value_from_fallback():
    merged = merge_git_opts(cast(GitOpts, {}), cast(GitOpts, {"paginate": UNSET}))
    assert "paginate" not in merged


def test_merge_git_envs_retains_unset_from_primary():
    merged = merge_git_envs(
        cast(GitEnvVars, {"GIT_EDITOR": UNSET}),
        cast(GitEnvVars, {"GIT_EDITOR": "vim"}),
    )
    assert merged["GIT_EDITOR"] is UNSET


def test_main_cmd_args_for_opt_key_unknown_returns_empty():
    git = SimpleGitCommand()
    assert git._main_cmd_args_for_opt_key("not_a_git_opt_key") == []
