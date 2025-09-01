#!/usr/bin/env python3
# coding=utf-8

"""
A simple and straight-forward git command subprocess runner implementation.
"""

from __future__ import annotations

import subprocess
from subprocess import CompletedProcess
from typing import overload, override, Any, Literal

from gitbolt.git_subprocess.constants import GIT_CMD
from gitbolt.git_subprocess.exceptions import GitCmdException
from gitbolt.git_subprocess.runner import GitCommandRunner


class SimpleGitCR(GitCommandRunner):
    """
    Simple git command runner that simply runs everything `as-is` in a subprocess.
    """

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
                [GIT_CMD, *main_cmd_args, *subcommand_args],
                *subprocess_run_args,
                input=_input,
                text=text,
                **subprocess_run_kwargs,
            )
        except subprocess.CalledProcessError as e:
            raise GitCmdException(
                e.stderr, called_process_error=e, exit_code=e.returncode
            ) from e
