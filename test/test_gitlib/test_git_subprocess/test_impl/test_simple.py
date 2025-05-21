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
    assert git.git(exec_path=None).exec_path is not None

def test_overrides():
    git = SimpleGitCommand[str](SimpleGitCR())
    assert not git.git(no_replace_objects=True).compute_main_cmd_args()

def test_ls_tree(enc_local):
    git = SimpleGitCommand[str](SimpleGitCR(), enc_local)
    git.ls_tree.ls_tree('HEAD')

def test_version():
    git = SimpleGitCommand(SimpleGitCR())
    assert 'git version 2' in git.version

def test_version_build_options():
    git = SimpleGitCommand(SimpleGitCR())
    version_build_info = git.git_version_subcmd.version(build_options=True)
    assert 'git version 2' in version_build_info
    assert 'cpu: ' in version_build_info
    assert 'built from commit: ' in version_build_info
