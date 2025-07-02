#!/usr/bin/env python3
# coding=utf-8
import subprocess
from pathlib import Path

import pytest

from test_gitbolt.test_git_subprocess import REMOTE_DIR_NAME, LOCAL_DIR_NAME


@pytest.fixture
def enc_test_root(tmpdir):
    """
    Create a test repo root to perform tests in.

    :param tmpdir: temporary directory for test.
    :return: temporary directory
    """
    return tmpdir


@pytest.fixture
def enc_remote(enc_test_root) -> Path:
    subprocess.run(['git', "init", "--bare", REMOTE_DIR_NAME], cwd=enc_test_root, check=True)
    return enc_test_root / REMOTE_DIR_NAME


@pytest.fixture
def enc_local(enc_test_root, enc_remote) -> Path:
    subprocess.run(['git', "clone", REMOTE_DIR_NAME, LOCAL_DIR_NAME], cwd=enc_test_root, check=True)
    return enc_test_root / LOCAL_DIR_NAME
