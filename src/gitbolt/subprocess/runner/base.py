#!/usr/bin/env python3
# coding=utf-8

"""
Git command runner interfaces to run subprocess calls.
"""

from __future__ import annotations

import pathlib
from abc import abstractmethod
from subprocess import CompletedProcess, Popen
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

    @overload
    @abstractmethod
    def popen_git_command(
        self,
        main_cmd_args: list[str],
        subcommand_args: list[str],
        *popen_run_args: Any,
        text: Literal[False],
        **popen_run_kwargs: Any,
    ) -> Popen[bytes]: ...

    @overload
    @abstractmethod
    def popen_git_command(
        self,
        main_cmd_args: list[str],
        subcommand_args: list[str],
        *popen_run_args: Any,
        text: Literal[True],
        **popen_run_kwargs: Any,
    ) -> Popen[str]: ...

    @abstractmethod
    def make_cmd(self, main_cmd_args: list[str], sub_cmd_args: list[str]) -> list[str]:
        """
        Make command for execution for use in an external subprocess.

        :param main_cmd_args: arguments for the main command.
        :param sub_cmd_args: arguments for subcommand.
        :returns: a fully made and runnable command for some external ``subprocess`` call.
        """
        ...

    @property
    @abstractmethod
    def git_prog(self) -> str | pathlib.Path:
        """
        :returns: git path location or git program name.
        """
        ...
