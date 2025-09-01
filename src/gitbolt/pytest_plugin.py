#!/usr/bin/env python3
# coding=utf-8

"""
Third-party importable pytest plugins for ``gitbolt``.
"""

import subprocess
from pathlib import Path

import pytest

REMOTE_DIR_NAME = "remote"
LOCAL_DIR_NAME = "local"


@pytest.fixture
def repo_root(tmpdir):
    """
    Create a test repo root to perform tests in.

    :param tmpdir: temporary directory for test.
    :return: temporary directory
    """
    return tmpdir


@pytest.fixture
def repo_remote(repo_root) -> Path:
    subprocess.run(
        ["git", "init", "--bare", REMOTE_DIR_NAME], cwd=repo_root, check=True
    )
    return repo_root / REMOTE_DIR_NAME


@pytest.fixture
def repo_local(repo_root, repo_remote) -> Path:
    subprocess.run(
        ["git", "clone", REMOTE_DIR_NAME, LOCAL_DIR_NAME], cwd=repo_root, check=True
    )
    return repo_root / LOCAL_DIR_NAME
