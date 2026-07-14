#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces for ``git worktree`` subcommand with default implementation for subprocess calls.
"""
import abc
from pathlib import Path
from typing import Literal, Iterable

from vt.utils.commons.commons.core_py import Unset, UNSET


WORKTREE_SUBCMD_NAME = "worktree"
WORKTREE_LIST_SUBCMD_NAME = "list"
WORKTREE_LOCK_SUBCMD_NAME = "lock"
WORKTREE_UNLOCK_SUBCMD_NAME = "unlock"

def build_non_none_list(*vals: str | Unset | Iterable[str] | None) -> list[str]:
    ret_list = []
    for val in vals:
        if val is not None:
            if val != UNSET:
                if isinstance(val, Iterable):
                    ret_list.extend(val)
                else:
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


def handle_str_bool_opt(arg: bool | Unset | str, opt_str: str) -> list[str] | Unset:
    if arg is False:
        return [f"--no-{opt_str}"]
    elif arg == UNSET:
        return arg
    elif isinstance(arg, str):
        return [f"--{opt_str}", arg]
    else:
        raise ValueError(f"{opt_str} must either have a value, be False or remain Unset.")


class WorktreeCLIArgsBuilder(abc.ABC):
    def build_list_cli_args(self, *, verbose: bool | Unset, porcelain: Literal[True, False] | Unset,
                            z: bool | Unset) -> list[str]:
        return [WORKTREE_SUBCMD_NAME, WORKTREE_LIST_SUBCMD_NAME,
                *build_non_none_list(self._handle_verbose_option(verbose),
                                     self._handle_porcelain_option(porcelain),
                                     self._handle_z_option(z))]

    def build_lock_cli_args(self, worktree: Path, reason: str | Literal[False] | Unset) -> list[str]:
         return [WORKTREE_SUBCMD_NAME, WORKTREE_LOCK_SUBCMD_NAME, str(worktree),
                 *build_non_none_list(self._handle_reason_option(reason))]

    def build_unlock_cli_args(self, worktree) -> list[str]:
        return [WORKTREE_SUBCMD_NAME, WORKTREE_LOCK_SUBCMD_NAME, str(worktree)]

    def _handle_verbose_option(self, verbose: bool | Unset) -> str | Unset:
        return handle_bool_opt(verbose, "verbose")

    def _handle_porcelain_option(self, porcelain: Literal[True, False] | Unset) -> str | Unset:
        return handle_bool_opt(porcelain, "porcelain")

    def _handle_z_option(self, z: bool | Unset) -> str | Unset:
        return handle_bool_opt(z, "z")

    def _handle_reason_option(self, reason: str | Literal[False] | Unset):
        return handle_str_bool_opt(reason, "reason")

