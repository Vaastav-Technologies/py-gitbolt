#!/usr/bin/env python3
# coding=utf-8

"""
A simple and straight-forward git command subprocess runner implementation.
"""

from __future__ import annotations

import pathlib
import subprocess
from subprocess import CompletedProcess
from typing import overload, override, Any, Literal

from gitbolt.subprocess.constants import GIT_CMD
from gitbolt.subprocess.exceptions import GitCmdException
from gitbolt.subprocess.runner import GitCommandRunner


class SimpleGitCR(GitCommandRunner):
    """
    Simple git command runner that simply runs everything `as-is` in a subprocess.
    """

    def __init__(self, git_prog: str | pathlib.Path = GIT_CMD):
        """
        :param git_prog: git program name/location. Useful when user wants to run a separate git version/git emulator.
        """
        self._git_prog = git_prog

    @overload
    @override
    def run_git_command(
        self,
        main_cmd_args: list[str],
        subcommand_args: list[str],
        *subprocess_run_args: Any,
        _input: str,
        text: Literal[True],
        **subprocess_run_kwargs: Any,
    ) -> CompletedProcess[str]: ...

    @overload
    @override
    def run_git_command(
        self,
        main_cmd_args: list[str],
        subcommand_args: list[str],
        *subprocess_run_args: Any,
        _input: bytes,
        text: Literal[False],
        **subprocess_run_kwargs: Any,
    ) -> CompletedProcess[bytes]: ...

    @overload
    @override
    def run_git_command(
        self,
        main_cmd_args: list[str],
        subcommand_args: list[str],
        *subprocess_run_args: Any,
        text: Literal[True],
        **subprocess_run_kwargs: Any,
    ) -> CompletedProcess[str]: ...

    @overload
    @override
    def run_git_command(
        self,
        main_cmd_args: list[str],
        subcommand_args: list[str],
        *subprocess_run_args: Any,
        text: Literal[False] = ...,
        **subprocess_run_kwargs: Any,
    ) -> CompletedProcess[bytes]: ...

    @override
    def run_git_command(
        self,
        main_cmd_args: list[str],
        subcommand_args: list[str],
        *subprocess_run_args: Any,
        _input: str | bytes | None = None,
        text: Literal[True, False] = False,
        **subprocess_run_kwargs: Any,
    ) -> CompletedProcess[str] | CompletedProcess[bytes]:
        try:
            return subprocess.run(
                [str(self.git_prog), *main_cmd_args, *subcommand_args],
                *subprocess_run_args,
                input=_input,
                text=text,
                **subprocess_run_kwargs,
            )
        except subprocess.CalledProcessError as e:
            raise GitCmdException(
                e.stderr, called_process_error=e, exit_code=e.returncode
            ) from e

    @override
    @property
    def git_prog(self) -> str | pathlib.Path:
        return self._git_prog
