#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces for ``git replace`` subcommand with default implementation for subprocess calls.
"""

from abc import abstractmethod
from typing import Protocol, override

from gitbolt.replace import ReplaceFormat
from gitbolt.subprocess.constants import REPLACE_CMD


class ReplaceCLIArgsBuilder(Protocol):
    """
    Interface to facilitate building of cli arguments for ``git replace`` subcommand.
    """

    @abstractmethod
    def build_replace(
        self, object: str, replacement: str, *, force: bool = False
    ) -> list[str]: ...

    @abstractmethod
    def build_delete(self, object: str, *objects: str) -> list[str]: ...

    @abstractmethod
    def build_list(
        self, pattern: str | None = None, *, format_: ReplaceFormat | None = None
    ) -> list[str]: ...

    @abstractmethod
    def build_graft(
        self, commit: str, *parents: str, force: bool = False
    ) -> list[str]: ...

    @abstractmethod
    def build_convert_graft_file(self, *, force: bool = False) -> list[str]: ...


class IndividuallyOverridableRCAB(ReplaceCLIArgsBuilder):
    """
    Individually Overridable Replace CLI Args Builder.

    Flags are emitted only when the caller sets them so Git keeps its own defaults
    (for example fail when a replace ref already exists; list format ``short``).
    """

    @override
    def build_replace(
        self, object: str, replacement: str, *, force: bool = False
    ) -> list[str]:
        """
        >>> IndividuallyOverridableRCAB().build_replace("abc", "def")
        ['replace', 'abc', 'def']
        >>> IndividuallyOverridableRCAB().build_replace("abc", "def", force=True)
        ['replace', '--force', 'abc', 'def']
        """
        args = [REPLACE_CMD]
        args.extend(self.force_arg(force))
        args.extend([object, replacement])
        return args

    @override
    def build_delete(self, object: str, *objects: str) -> list[str]:
        """
        >>> IndividuallyOverridableRCAB().build_delete("abc")
        ['replace', '-d', 'abc']
        >>> IndividuallyOverridableRCAB().build_delete("abc", "def")
        ['replace', '-d', 'abc', 'def']
        """
        return [REPLACE_CMD, "-d", object, *objects]

    @override
    def build_list(
        self, pattern: str | None = None, *, format_: ReplaceFormat | None = None
    ) -> list[str]:
        """
        >>> IndividuallyOverridableRCAB().build_list()
        ['replace']
        >>> IndividuallyOverridableRCAB().build_list("abc*", format_="medium")
        ['replace', '--format=medium', '-l', 'abc*']
        """
        args = [REPLACE_CMD]
        if format_ is not None:
            args.append(f"--format={format_}")
        if pattern is not None:
            args.extend(["-l", pattern])
        return args

    @override
    def build_graft(
        self, commit: str, *parents: str, force: bool = False
    ) -> list[str]:
        """
        >>> IndividuallyOverridableRCAB().build_graft("abc")
        ['replace', '--graft', 'abc']
        >>> IndividuallyOverridableRCAB().build_graft("abc", "def", force=True)
        ['replace', '--force', '--graft', 'abc', 'def']
        """
        args = [REPLACE_CMD]
        args.extend(self.force_arg(force))
        args.extend(["--graft", commit, *parents])
        return args

    @override
    def build_convert_graft_file(self, *, force: bool = False) -> list[str]:
        """
        >>> IndividuallyOverridableRCAB().build_convert_graft_file()
        ['replace', '--convert-graft-file']
        >>> IndividuallyOverridableRCAB().build_convert_graft_file(force=True)
        ['replace', '--force', '--convert-graft-file']
        """
        args = [REPLACE_CMD]
        args.extend(self.force_arg(force))
        args.append("--convert-graft-file")
        return args

    def force_arg(self, force: bool) -> list[str]:
        """
        >>> IndividuallyOverridableRCAB().force_arg(True)
        ['--force']
        >>> IndividuallyOverridableRCAB().force_arg(False)
        []
        """
        return ["--force"] if force else []
