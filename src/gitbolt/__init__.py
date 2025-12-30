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
from gitbolt.subprocess.base import GitCommand
# endregion


from gitbolt.constants import GIT_DIR as GIT_DIR
from gitbolt.subprocess.constants import GIT_CMD
from gitbolt.subprocess.impl.simple import SimpleGitCommand as _SimpleGitCommand
from gitbolt.subprocess.impl.simple import CLISimpleGitCommand as _CLISimpleGitCommand
from gitbolt.subprocess.runner.simple import SimpleGitCR as _SimpleGitCR
# endregion


def get_git(git_root_dir: Path = Path.cwd()) -> Git:
    """
    Get operational and programmatic ``Git``.

    Examples:

    * Get git version:

    >>> import subprocess
    >>> import gitbolt
    >>> git = gitbolt.get_git()
    >>> assert git.version().version() == subprocess.run(['git', 'version'], capture_output=True, text=True).stdout.strip()

    :param git_root_dir: Path to the git repo root directory. Defaults to current working directory.
    :returns: The ``Git`` instance with all subcommands.
    """

    return _SimpleGitCommand(git_root_dir)


def get_git_command(
    git_root_dir: Path = Path.cwd(),
    *,
    git_prog: str | Path = GIT_CMD,
    main_cmd_opts: list[str] | None = None,
    main_cmd_envs: dict[str, str] | None = None,
    prefer_cli: bool = False,
) -> GitCommand:
    """
    Get operational and programmatic ``Git`` which runs as a subprocess.

    Examples:

    * Get git version, as base git:

    >>> import subprocess
    >>> import gitbolt
    >>> git = gitbolt.get_git_command()
    >>> assert git.version().version() == subprocess.run(['git', 'version'], capture_output=True, text=True).stdout.strip()

    * Get git version, as a git subcommand. Runs git in subprocess:

    >>> assert git.subcmd_unchecked.run(["version"], text=True).stdout.strip() == subprocess.run(['git', 'version'], capture_output=True, text=True).stdout.strip()

    :param git_root_dir: Path to the git repo root directory. Defaults to current working directory.
    :param git_prog: git program name/location. Useful when user wants to run a separate git version/git emulator.
    :param opts: main git cli options. The main git command options like ``--no-replace-objects``, ``--no-pager``, ``-C`` etc are git main command args.
    :param envs: main git cli env vars. Not supplying any env vars (default behavior: ``None``) simply supplies all
        the env vars to the underlying runner.
    :param prefer_cli: cli opts and envs will be given priority over programmatically set opts and envs. Setting
        this param to ``True`` will make cli opts and envs appear later in the opts and envs strings which will
        make them override previously programmatically set opts and envs.
    :returns: ``GitCommand`` instance with all the subcommands as well as ``unchecked_subcmd``. Runs git commands in a
        separate runner in subprocess.
    """
    runner = _SimpleGitCR(git_prog)
    if main_cmd_opts is None:
        return _SimpleGitCommand(git_root_dir, runner)
    else:
        return _CLISimpleGitCommand(
            git_root_dir,
            runner,
            opts=main_cmd_opts,
            envs=main_cmd_envs,
            prefer_cli=prefer_cli,
        )
