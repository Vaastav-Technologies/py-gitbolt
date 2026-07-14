#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces for ``git worktree`` subcommand with default implementation for subprocess calls.
"""
import abc
from datetime import datetime
from pathlib import Path
from typing import Literal, Iterable

from vt.utils.commons.commons.core_py import Unset, UNSET


WORKTREE_SUBCMD_NAME = "worktree"
WORKTREE_LIST_SUBCMD_NAME = "list"
WORKTREE_ADD_SUBCMD_NAME = "add"
WORKTREE_MOVE_SUBCMD_NAME = "move"
WORKTREE_REMOVE_SUBCMD_NAME = "remove"
WORKTREE_REPAIR_SUBCMD_NAME = "repair"
WORKTREE_PRUNE_SUBCMD_NAME = "prune"
WORKTREE_LOCK_SUBCMD_NAME = "lock"
WORKTREE_UNLOCK_SUBCMD_NAME = "unlock"

def build_non_none_list(*vals: str | Unset | Iterable[str] | None) -> list[str]:
    ret_list: list[str] = []
    for val in vals:
        if val is not None:
            if not isinstance(val, Unset):
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


def handle_true_opt(arg: Literal[True] | Unset, opt_str: str, single_dash: bool = True) -> str | Unset:
        if arg is True:
            if single_dash:
                return f"-{opt_str}"
            return f"--{opt_str}"
        elif isinstance(arg, Unset):
            return arg
        else:
            raise ValueError(f"{opt_str} must either be true or remain Unset.")


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
                            z: Literal[True] | Unset) -> list[str]:
        return [WORKTREE_SUBCMD_NAME, WORKTREE_LIST_SUBCMD_NAME,
                *build_non_none_list(self._handle_verbose_option(verbose),
                                     self._handle_porcelain_option(porcelain),
                                     self._handle_z_option(z))]

    def build_lock_cli_args(self, worktree: Path, reason: str | Literal[False] | Unset) -> list[str]:
         return [WORKTREE_SUBCMD_NAME, WORKTREE_LOCK_SUBCMD_NAME, str(worktree),
                 *build_non_none_list(self._handle_reason_option(reason))]

    def build_unlock_cli_args(self, worktree) -> list[str]:
        return [WORKTREE_SUBCMD_NAME, WORKTREE_LOCK_SUBCMD_NAME, str(worktree)]

    def build_move_cli_args(self, worktree: Path, new_path: Path, *, force: bool | Unset,
                            reforce: bool | Unset, relative_paths: bool | Unset) -> list[str]:
        return [WORKTREE_SUBCMD_NAME, WORKTREE_MOVE_SUBCMD_NAME, str(worktree), str(new_path),
                *build_non_none_list(
                    self._handle_force_option(force),
                    self._handle_reforce_option(reforce),
                    self._handle_relative_paths_option(relative_paths),
        )]

    def build_prune_cli_args(self, dry_run: bool | Unset, verbose: bool | Unset,
                             expire: Literal[False] | int | datetime | Unset) -> list[str]:
        return [WORKTREE_SUBCMD_NAME, WORKTREE_MOVE_SUBCMD_NAME,
                *build_non_none_list(
                    self._handle_dry_run(dry_run),
                    self._handle_verbose_option(verbose),
                    self._handle_expire_option(expire))]

    def build_remove_cli_args(self, worktree: Path, *, force: bool | Unset, reforce: bool | Unset) -> list[str]:
        return [WORKTREE_SUBCMD_NAME, WORKTREE_REMOVE_SUBCMD_NAME, str(worktree),
                *build_non_none_list(
                    self._handle_force_option(force),
                    self._handle_reforce_option(reforce)
                )]

    def build_repair_cli_args(self, *worktrees: Path, relative_paths: bool | Unset) -> list[str]:
        return [WORKTREE_SUBCMD_NAME, WORKTREE_REMOVE_SUBCMD_NAME, *[str(worktree) for worktree in worktrees],
                *build_non_none_list(
                    self._handle_relative_paths_option(relative_paths)
                )]

    def build_add_cli_args(self, worktree: Path, commit_ish: str | None, *, force: bool | Unset,
                reforce: bool | Unset, new_branch: str | Unset, new_branch_force: str | Unset,
                orphan: Literal[True] | Unset, detach: Literal[True] | Unset,
                checkout: bool | Unset, lock: bool | Unset,
                reason: str | Literal[False] | Unset, quiet: bool | Unset,
                track: bool | Unset, guess_remote: bool | Unset,
                relative_paths: bool | Unset) -> list[str]:
        return [WORKTREE_SUBCMD_NAME, WORKTREE_ADD_SUBCMD_NAME, str(worktree),
                *build_non_none_list(
                    self._handle_force_option(force),
                    self._handle_reforce_option(reforce),
                    self._handle_new_branch_option(new_branch, commit_ish),
                    self._handle_new_branch_force_option(new_branch_force, commit_ish),
                    self._handle_orphan_option(orphan),
                    self._handle_detach_option(detach),
                    self._handle_checkout_option(checkout),
                    self._handle_lock_option(lock),
                    self._handle_reason_option(reason),
                    self._handle_quiet_option(quiet),
                    self._handle_track_option(track),
                    self._handle_guess_remote_option(guess_remote),
                    self._handle_relative_paths_option(relative_paths),
                )]

    def _handle_verbose_option(self, verbose: bool | Unset) -> str | Unset:
        return handle_bool_opt(verbose, "verbose")

    def _handle_porcelain_option(self, porcelain: Literal[True, False] | Unset) -> str | Unset:
        return handle_bool_opt(porcelain, "porcelain")

    def _handle_z_option(self, z: Literal[True] | Unset) -> str | Unset:
        return handle_true_opt(z, "z", True)

    def _handle_reason_option(self, reason: str | Literal[False] | Unset) -> list[str] | Unset:
        return handle_str_bool_opt(reason, "reason")

    def _handle_force_option(self, force: bool | Unset) -> str | Unset:
        return handle_bool_opt(force, "force")

    def _handle_reforce_option(self, reforce: bool | Unset) -> str | Unset:
        return self._handle_force_option(reforce)

    def _handle_relative_paths_option(self, relative_paths: bool | Unset) -> str | Unset:
        return handle_bool_opt(relative_paths, "relative-paths")

    def _handle_dry_run(self, dry_run: bool | Unset) -> str | Unset:
        return handle_bool_opt(dry_run, "dry-run")

    def _handle_expire_option(self, expire: Literal[False] | int | datetime | Unset) -> list[str]:
        expire_str = "expire"
        if expire is False:
            return [f"--no-{expire_str}"]
        elif isinstance(expire, datetime):
            return [f"--{expire_str}", expire.strftime("%d/%m/%Y, %H:%M:%S")]
        elif isinstance(expire, int):
            return [f"--{expire_str}", str(expire)]
        else:
            raise ValueError(f"{expire} must either have a datetime value, int value, be False or remain Unset.")

    def _handle_new_branch_option(self, new_branch: str | Unset, commit_ish: str | None) -> list[str] | Unset:
        return self._new_branch_option_helper(new_branch, commit_ish, "-b")

    def _handle_new_branch_force_option(self, new_branch_force: str | Unset,
                                        commit_ish: str | None) -> list[str] | Unset:
        return self._new_branch_option_helper(new_branch_force, commit_ish, "-B")

    def _handle_orphan_option(self, orphan: Literal[True] | Unset) -> str | Unset:
        return handle_true_opt(orphan, "orphan")

    def _handle_detach_option(self, detach: Literal[True] | Unset) -> str | Unset:
        return handle_true_opt(detach, "detach")

    def _handle_checkout_option(self, checkout: bool | Unset) -> str | Unset:
        return handle_bool_opt(checkout, "checkout")

    def _handle_lock_option(self, lock: bool | Unset) -> str | Unset:
        return handle_bool_opt(lock, "lock")

    def _handle_quiet_option(self, quiet: bool | Unset) -> str | Unset:
        return handle_bool_opt(quiet, "quiet")

    def _handle_track_option(self, track: bool | Unset) -> str | Unset:
        return handle_bool_opt(track, "track")

    def _handle_guess_remote_option(self, guess_remote: bool | Unset) -> str | Unset:
        return handle_bool_opt(guess_remote, "guess-remote")

    def _new_branch_option_helper(self, new_branch: str | Unset, commit_ish: str | None,
                                  opt_str: str) -> list[str] | Unset:
        if new_branch==UNSET:
            return new_branch
        elif isinstance(new_branch, str):
            if commit_ish is not None:
                return [opt_str, commit_ish]
            return [opt_str]
        else:
            raise ValueError(f"{opt_str} must either have a branch-name value or remain Unset.")
