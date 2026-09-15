#!/usr/bin/env python3
# coding=utf-8

"""
Tests for subprocess environment handling (issue #6: respect OS-passed env vars).
"""

from unittest.mock import MagicMock, patch

import pytest

from gitbolt.subprocess.impl.simple import SimpleGitCommand
from gitbolt.subprocess.runner.simple import SimpleGitCR
from gitbolt.subprocess.utils.env import subprocess_env_with_os

OS_MARKER = "GITBOLT_TEST_OS_MARKER"


class TestSubprocessEnvWithOs:
    def test_none_returns_none(self):
        assert subprocess_env_with_os(None) is None

    def test_merges_os_and_override(self, monkeypatch):
        monkeypatch.setenv(OS_MARKER, "from_os")
        result = subprocess_env_with_os({"GIT_AUTHOR_NAME": "from_gitbolt"})
        assert result is not None
        assert result[OS_MARKER] == "from_os"
        assert result["GIT_AUTHOR_NAME"] == "from_gitbolt"

    def test_override_wins_on_conflict(self, monkeypatch):
        monkeypatch.setenv("GIT_AUTHOR_NAME", "from_os")
        result = subprocess_env_with_os({"GIT_AUTHOR_NAME": "from_gitbolt"})
        assert result is not None
        assert result["GIT_AUTHOR_NAME"] == "from_gitbolt"


class TestSimpleGitCREnv:
    @patch("subprocess.run")
    def test_run_inherits_when_env_not_passed(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        SimpleGitCR().run_git_command([], ["version"], text=True)
        assert mock_run.call_args.kwargs.get("env") is None

    @patch("subprocess.run")
    def test_run_merges_os_env_when_override_passed(self, mock_run, monkeypatch):
        monkeypatch.setenv(OS_MARKER, "yes")
        mock_run.return_value = MagicMock(returncode=0)
        SimpleGitCR().run_git_command(
            [], ["version"], env={"GIT_AUTHOR_NAME": "a"}, text=True
        )
        env = mock_run.call_args.kwargs["env"]
        assert env[OS_MARKER] == "yes"
        assert env["GIT_AUTHOR_NAME"] == "a"

    @patch("subprocess.Popen")
    def test_popen_inherits_when_env_not_passed(self, mock_popen):
        mock_popen.return_value = MagicMock()
        SimpleGitCR().popen_git_command([], ["cat-file", "--batch"], text=False)
        assert mock_popen.call_args.kwargs.get("env") is None

    @patch("subprocess.Popen")
    def test_popen_merges_os_env_when_override_passed(self, mock_popen, monkeypatch):
        monkeypatch.setenv(OS_MARKER, "yes")
        mock_popen.return_value = MagicMock()
        SimpleGitCR().popen_git_command(
            [], ["cat-file", "--batch"], env={"GIT_TRACE": "1"}, text=False
        )
        env = mock_popen.call_args.kwargs["env"]
        assert env[OS_MARKER] == "yes"
        assert env["GIT_TRACE"] == "1"


class TestUncheckedSubcmdGitEnvs:
    def test_extra_env_without_programmatic_overrides(self, repo_local):
        git = SimpleGitCommand(repo_local)
        assert git.subcmd_unchecked().git_envs({"FOO": "bar"}) == {"FOO": "bar"}

    def test_extra_env_merged_with_programmatic_overrides(self, repo_local):
        git = SimpleGitCommand(repo_local).git_envs_override(GIT_AUTHOR_NAME="from_gitbolt")
        merged = git.subcmd_unchecked().git_envs({"FOO": "bar"})
        assert merged == {"GIT_AUTHOR_NAME": "from_gitbolt", "FOO": "bar"}

    def test_extra_env_overrides_on_key_conflict(self, repo_local):
        git = SimpleGitCommand(repo_local).git_envs_override(GIT_AUTHOR_NAME="from_gitbolt")
        merged = git.subcmd_unchecked().git_envs({"GIT_AUTHOR_NAME": "from_run"})
        assert merged["GIT_AUTHOR_NAME"] == "from_run"

    def test_no_extra_returns_none_without_overrides(self, repo_local):
        git = SimpleGitCommand(repo_local)
        assert git.subcmd_unchecked().git_envs() is None

    def test_no_extra_returns_programmatic_only(self, repo_local):
        git = SimpleGitCommand(repo_local).git_envs_override(GIT_TRACE=True)
        assert git.subcmd_unchecked().git_envs() == {"GIT_TRACE": "True"}


class TestIntegrationOsEnvRespected:
    def test_version_with_git_env_override(self, repo_local):
        git = SimpleGitCommand(repo_local).git_envs_override(GIT_AUTHOR_NAME="probe")
        out = git.subcmd_unchecked().run(["version"], text=True, check=True).stdout
        assert "git version" in out.lower()

    def test_rev_parse_with_run_env_only(self, repo_local):
        git = SimpleGitCommand(repo_local)
        git.subcmd_unchecked().run(
            ["rev-parse", "--is-inside-work-tree"],
            text=True,
            check=True,
            env={"GITBOLT_UNUSED": "1"},
        )
