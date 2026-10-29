#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces specific to ``git switch`` subcommand.
"""

from abc import abstractmethod
from typing import Protocol, override, Literal

from gitbolt._internal_init import errmsg_creator
from gitbolt.exceptions import GitExitingException
from vt.utils.errors.error_specs import ERR_INVALID_USAGE
from vt.utils.errors.error_specs.utils import require_type

CONFLICT_STYLES = ("merge", "diff3", "zdiff3")
TRACK_MODES = ("direct", "inherit")
ConflictStyle = Literal["merge", "diff3", "zdiff3"]
TrackMode = Literal["direct", "inherit"]


class SwitchArgsValidator(Protocol):  # pragma: no cover
    """
    The argument validator for ``git switch`` subcommand.
    """

    @abstractmethod
    def validate(
        self,
        branch: str | None = None,
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
    ) -> None: ...


class UtilSwitchArgsValidator(SwitchArgsValidator):
    """
    Independent utility to perform ``git switch`` argument validation.

    Flags are omitted unless the caller sets them, so Git keeps its defaults
    (for example ``--guess`` is Git's default; we do not emit it unless asked).
    """

    @override
    def validate(
        self,
        branch: str | None = None,
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
    ) -> None:
        """
        >>> UtilSwitchArgsValidator().validate("master")
        >>> UtilSwitchArgsValidator().validate(create="fixup", start_point="HEAD~3")
        >>> UtilSwitchArgsValidator().validate(detach=True, start_point="HEAD")
        >>> UtilSwitchArgsValidator().validate()
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: Either branch, create, force_create, detach or orphan is required
        >>> UtilSwitchArgsValidator().validate("master", create="fixup")
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: branch and create are not allowed together
        """
        require_type(detach, "detach", bool, GitExitingException)
        require_type(discard_changes, "discard_changes", bool, GitExitingException)
        require_type(force, "force", bool, GitExitingException)
        require_type(merge, "merge", bool, GitExitingException)
        require_type(quiet, "quiet", bool, GitExitingException)
        require_type(no_track, "no_track", bool, GitExitingException)
        require_type(ignore_other_worktrees, "ignore_other_worktrees", bool, GitExitingException)
        self._optional_bool(guess, "guess")
        self._optional_bool(progress, "progress")
        self._optional_bool(recurse_submodules, "recurse_submodules")
        self._optional_non_empty(branch, "branch")
        self._optional_non_empty(start_point, "start_point")
        self._optional_non_empty(create, "create")
        self._optional_non_empty(force_create, "force_create")
        self._optional_non_empty(orphan, "orphan")
        self._validate_destination(
            branch=branch,
            create=create,
            force_create=force_create,
            detach=detach,
            orphan=orphan,
            start_point=start_point,
        )
        if create is not None and force_create is not None:
            self._exclusive("create", "force_create")
        if merge and (discard_changes or force):
            self._exclusive("merge", "discard_changes")
        if track is not None and no_track:
            self._exclusive("track", "no_track")
        if conflict is not None:
            if conflict not in CONFLICT_STYLES:
                errmsg = errmsg_creator.errmsg_for_choices(
                    emphasis="conflict", choices=list(CONFLICT_STYLES)
                )
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
        if track is not None:
            if track is True:
                pass
            elif track is False:
                errmsg = "track=False is invalid; use no_track=True"
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
            elif track not in TRACK_MODES:
                errmsg = errmsg_creator.errmsg_for_choices(
                    emphasis="track", choices=list(TRACK_MODES)
                )
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)

    def _validate_destination(
        self,
        *,
        branch: str | None,
        create: str | None,
        force_create: str | None,
        detach: bool,
        orphan: str | None,
        start_point: str | None,
    ) -> None:
        destinations = [
            name
            for name, selected in (
                ("branch", branch is not None),
                ("create", create is not None),
                ("force_create", force_create is not None),
                ("detach", detach),
                ("orphan", orphan is not None),
            )
            if selected
        ]
        if not destinations:
            errmsg = "Either branch, create, force_create, detach or orphan is required"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if len(destinations) > 1:
            self._exclusive(destinations[0], destinations[1])
        if start_point is not None and branch is not None:
            self._exclusive("branch", "start_point")
        if start_point is not None and orphan is not None:
            self._exclusive("orphan", "start_point")

    def _optional_non_empty(self, value: str | None, name: str) -> None:
        if value is None:
            return
        require_type(value, name, str, GitExitingException)
        if value == "":
            errmsg = f"'{name}' is required"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    def _optional_bool(self, value: bool | None, name: str) -> None:
        if value is not None:
            require_type(value, name, bool, GitExitingException)

    def _exclusive(self, left: str, right: str) -> None:
        errmsg = errmsg_creator.not_allowed_together(left, right)
        raise GitExitingException(
            errmsg, exit_code=ERR_INVALID_USAGE
        ) from ValueError(errmsg)
