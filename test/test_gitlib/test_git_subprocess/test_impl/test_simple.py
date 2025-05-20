#!/usr/bin/env python3
# coding=utf-8

"""
Tests for Git command interfaces with default implementation using subprocess calls.
"""
from vt.vcs.git.gitlib.git_subprocess import SimpleGitCR
from vt.vcs.git.gitlib.git_subprocess.impl.simple import SimpleGitCommand


def test_exec_path():
    git = SimpleGitCommand[str](SimpleGitCR())
    assert git.exec_path is None

def test_overrides_and_exec_path():
    git = SimpleGitCommand[str](SimpleGitCR())
    git.git(exec_path=None)
    assert git.exec_path is None
