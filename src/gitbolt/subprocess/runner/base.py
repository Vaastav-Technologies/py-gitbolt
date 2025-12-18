#!/usr/bin/env python3
# coding=utf-8

"""
Git command runner interfaces to run subprocess calls.
"""

from __future__ import annotations

from abc import abstractmethod
from subprocess import CompletedProcess
from typing import Protocol, overload, Any, Literal


class GitCommandRunner(Protocol):
    """
    Interface to facilitate running git commands in subprocess.
    """

    @overload
    @abstractmethod
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
    @abstractmethod
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
    @abstractmethod
    def run_git_command(
        self,
        main_cmd_args: list[str],
        subcommand_args: list[str],
        *subprocess_run_args: Any,
        text: Literal[True],
        **subprocess_run_kwargs: Any,
    ) -> CompletedProcess[str]: ...

    @overload
    @abstractmethod
    def run_git_command(
        self,
        main_cmd_args: list[str],
        subcommand_args: list[str],
        *subprocess_run_args: Any,
        text: Literal[False] = ...,
        **subprocess_run_kwargs: Any,
    ) -> CompletedProcess[bytes]: ...
