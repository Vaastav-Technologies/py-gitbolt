#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces for ``git worktree`` subcommand with default implementation for subprocess calls.
"""
import abc
from typing import Literal

from vt.utils.commons.commons.core_py import Unset, UNSET


def build_non_none_list(*vals: str | Unset | None) -> list[str]:
    ret_list = []
    for val in vals:
        if val is not None:
            if val != UNSET:
                ret_list.append(val)
    return ret_list


def handle_bool_opt(arg: bool | Unset, opt_str: str) -> str | Unset:
        if arg is True:
            return f"--{opt_str}"
        elif arg is False:
            return f"--no-{opt_str}"
        elif arg == UNSET:
            return arg
        else:
            raise ValueError(f"{opt_str} must either be a bool or remain Unset.")


class WorktreeCLIArgsBuilder(abc.ABC):
    def build_list_cli_args(self, *, verbose: bool | Unset, porcelain: Literal[True, False] | Unset,
                            z: bool | Unset) -> list[str]:
        return build_non_none_list(self._handle_verbose_option(verbose),
                                   self._handle_porcelain_option(porcelain),
                                   self._handle_z_option(z))

    def _handle_verbose_option(self, verbose: bool | Unset) -> str | Unset:
        return handle_bool_opt(verbose, "verbose")

    def _handle_porcelain_option(self, porcelain: Literal[True, False] | Unset) -> str | Unset:
        return handle_bool_opt(porcelain, "porcelain")

    def _handle_z_option(self, z: bool | Unset) -> str | Unset:
        return handle_bool_opt(z, "z")

