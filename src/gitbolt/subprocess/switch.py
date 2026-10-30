#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces for ``git switch`` subcommand with default implementation for subprocess calls.
"""

from abc import abstractmethod
from typing import Protocol, override

from gitbolt.switch import ConflictStyle, TrackMode, SwitchBranch
from gitbolt.subprocess.constants import SWITCH_CMD


class SwitchCLIArgsBuilder(Protocol):  # pragma: no cover
    """
    Interface to facilitate building of cli arguments for ``git switch`` subcommand.
    """

    @abstractmethod
    def build(
        self,
        branch: SwitchBranch | None = None,
        *,
        start_point: str | None = None,
        create: str | None = None,
        force_create: str | None = None,
        detach: bool = False,
        orphan: str | None = None,
        guess: bool | None = None,
        discard_changes: bool = False,
        force: bool = False,
        merge: bool = False,
        conflict: ConflictStyle | None = None,
        quiet: bool = False,
        progress: bool | None = None,
        track: bool | TrackMode | None = None,
        no_track: bool = False,
        ignore_other_worktrees: bool = False,
        recurse_submodules: bool | None = None,
    ) -> list[str]: ...


class IndividuallyOverridableSCAB(SwitchCLIArgsBuilder):
    """
    Individually Overridable Switch CLI Args Builder.

    Flags are emitted only when the caller sets them so Git keeps its own defaults
    (for example ``--guess`` is on unless ``--no-guess`` is given).
    ``force`` is an alias of ``discard_changes`` and emits ``--discard-changes``.
    """

    @override
    def build(
        self,
        branch: SwitchBranch | None = None,
        *,
        start_point: str | None = None,
        create: str | None = None,
        force_create: str | None = None,
        detach: bool = False,
        orphan: str | None = None,
        guess: bool | None = None,
        discard_changes: bool = False,
        force: bool = False,
        merge: bool = False,
        conflict: ConflictStyle | None = None,
        quiet: bool = False,
        progress: bool | None = None,
        track: bool | TrackMode | None = None,
        no_track: bool = False,
        ignore_other_worktrees: bool = False,
        recurse_submodules: bool | None = None,
    ) -> list[str]:
        """
        >>> builder = IndividuallyOverridableSCAB()
        >>> builder.build("master")
        ['switch', 'master']
        >>> builder.build(create="fixup", start_point="HEAD~3")
        ['switch', '--create', 'fixup', 'HEAD~3']
        >>> builder.build(detach=True, start_point="HEAD")
        ['switch', '--detach', 'HEAD']
        >>> builder.build("topic", discard_changes=True)
        ['switch', '--discard-changes', 'topic']
        >>> builder.build("topic", force=True)
        ['switch', '--discard-changes', 'topic']
        """
        args = [SWITCH_CMD]
        args.extend(self.create_arg(create))
        args.extend(self.force_create_arg(force_create))
        args.extend(self.true_flag(detach, "--detach"))
        args.extend(self.orphan_arg(orphan))
        args.extend(self.optional_bool_flag(guess, "--guess", "--no-guess"))
        args.extend(self.true_flag(discard_changes or force, "--discard-changes"))
        args.extend(self.true_flag(merge, "--merge"))
        args.extend(self.conflict_arg(conflict))
        args.extend(self.true_flag(quiet, "--quiet"))
        args.extend(self.optional_bool_flag(progress, "--progress", "--no-progress"))
        args.extend(self.track_arg(track))
        args.extend(self.true_flag(no_track, "--no-track"))
        args.extend(self.true_flag(ignore_other_worktrees, "--ignore-other-worktrees"))
        args.extend(
            self.optional_bool_flag(
                recurse_submodules, "--recurse-submodules", "--no-recurse-submodules"
            )
        )
        if branch is not None:
            args.append(branch)
        if start_point is not None:
            args.append(start_point)
        return args

    def create_arg(self, create: str | None) -> list[str]:
        return ["--create", create] if create is not None else []

    def force_create_arg(self, force_create: str | None) -> list[str]:
        return ["--force-create", force_create] if force_create is not None else []

    def orphan_arg(self, orphan: str | None) -> list[str]:
        return ["--orphan", orphan] if orphan is not None else []

    def conflict_arg(self, conflict: ConflictStyle | None) -> list[str]:
        return [f"--conflict={conflict}"] if conflict is not None else []

    def track_arg(self, track: bool | TrackMode | None) -> list[str]:
        if track is True:
            return ["--track"]
        if isinstance(track, str):
            return [f"--track={track}"]
        return []

    def true_flag(self, flag: bool, opt: str) -> list[str]:
        return [opt] if flag else []

    def optional_bool_flag(
        self, flag: bool | None, yes: str, no: str
    ) -> list[str]:
        if flag is True:
            return [yes]
        if flag is False:
            return [no]
        return []
