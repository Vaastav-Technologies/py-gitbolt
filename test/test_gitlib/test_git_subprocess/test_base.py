#!/usr/bin/env python3
# coding=utf-8

"""
Tests for Git command interfaces with default implementation using subprocess calls.
"""
from vt.vcs.git.gitlib.git_subprocess.base import GitCommand
from vt.vcs.git.gitlib.git_subprocess.impl.simple import SimpleGitCR


def test_exec_path():
    git = GitCommand[str](SimpleGitCR())
