#!/usr/bin/env python3
# coding=utf-8

"""
Git command interfaces with default implementation using subprocess calls.
"""

from pathlib import Path

# region imports
# region base related imports
from gitbolt.base import Git as Git
from gitbolt.base import CanOverrideGitOpts as CanOverrideGitOpts
from gitbolt.base import HasGitUnderneath as HasGitUnderneath
from gitbolt.base import GitSubCommand as GitSubCommand
from gitbolt.base import LsTree as LsTree
from gitbolt.base import Version as Version
from gitbolt.base import Add as Add
# endregion


from gitbolt.constants import GIT_DIR as GIT_DIR
# endregion


def get_git(git_root_dir: Path = Path.cwd()) -> Git:
    """
    Get operational and programmatic ``Git``.

    Examples:

    * Get git version:

    >>> import subprocess
    >>> import gitbolt
    >>> git = gitbolt.get_git()
    >>> assert git.version == subprocess.run(['git', 'version'], capture_output=True, text=True).stdout.strip()

    :param git_root_dir: Path to the git repo root directory. Defaults to current working directory.
    """
    from gitbolt.git_subprocess.impl.simple import SimpleGitCommand

    return SimpleGitCommand(git_root_dir)
