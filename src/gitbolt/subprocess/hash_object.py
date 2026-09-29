#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces for ``git hash-object`` subcommand with default implementation for subprocess calls.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Protocol, override, Literal

from gitbolt.subprocess.constants import HASH_OBJECT_CMD


class HashObjectCLIArgsBuilder(Protocol):
    """
    Interface to facilitate building of cli arguments for ``git hash-object`` subcommand.
    """

    @abstractmethod
    def build(
        self,
        file_path: Path | None = None,
        *file_paths: Path,
        t: Literal["commit", "tree", "blob", "tag"] = "blob",
        path: Path | None = None,
        no_filters: bool = False,
        literally: bool = False,
        stdin: bytes | None = None,
        stdin_paths: list[Path] | None = None,
        w: bool = False,
    ) -> list[str]:
        """
        Build the complete list of subcommand arguments to be passed to ``git hash-object``.

        This method assembles the subcommand portion of the git command invocation, such as
        in ``git --no-pager hash-object -w file.txt``, where ``-w file.txt`` is the
        subcommand argument list.

        It delegates the formation of each argument to protected helper methods to allow
        easier overriding and testing of individual components.

        :return: Complete list of subcommand arguments.
        :raises GitExitingException: if undesired argument type or argument combination is supplied.
        """
        ...


class IndividuallyOverridableHOCAB(HashObjectCLIArgsBuilder):
    """
    Individually Overridable Hash Object CLI Args Builder.

    Build CLI args to run ``git hash-object`` subcommand in a subprocess. This class is independent in its working and
    provides interface to individually override each arg former for fine-grained control.
    """

    @override
    def build(
        self,
        file_path: Path | None = None,
        *file_paths: Path,
        t: Literal["commit", "tree", "blob", "tag"] = "blob",
        path: Path | None = None,
        no_filters: bool = False,
        literally: bool = False,
        stdin: bytes | None = None,
        stdin_paths: list[Path] | None = None,
        w: bool = False,
    ) -> list[str]:
        """
        Build the full list of arguments to be passed to ``git hash-object``.

        >>> builder = IndividuallyOverridableHOCAB()

        Basic usage with one file:

        >>> builder.build(Path("file.txt"))
        ['hash-object', '-t', 'blob', 'file.txt']

        Using boolean flags:

        >>> builder.build(Path("file.txt"), no_filters=True, literally=True)
        ['hash-object', '-t', 'blob', '--no-filters', '--literally', 'file.txt']

        Using type and write:

        >>> builder.build(Path("file.txt"), t="commit", w=True)
        ['hash-object', '-w', '-t', 'commit', 'file.txt']

        Using --path:

        >>> builder.build(Path("file.txt"), path=Path("filters/file.txt"))
        ['hash-object', '-t', 'blob', '--path=filters/file.txt', 'file.txt']

        Using multiple files:

        >>> builder.build(Path("a.txt"), Path("b.txt"))
        ['hash-object', '-t', 'blob', 'a.txt', 'b.txt']

        Using --stdin:

        >>> builder.build(Path("a.txt"), stdin=b"extra")
        ['hash-object', '-t', 'blob', '--stdin', 'a.txt']

        Using --stdin only:

        >>> builder.build(stdin=b"blob-bytes")
        ['hash-object', '-t', 'blob', '--stdin']

        Using --stdin-paths:

        >>> builder.build(stdin_paths=[Path("a.txt"), Path("b.txt")])
        ['hash-object', '-t', 'blob', '--stdin-paths']
        """
        sub_cmd_args = [HASH_OBJECT_CMD]
        sub_cmd_args.extend(self.w_arg(w))
        sub_cmd_args.extend(self.type_arg(t))
        sub_cmd_args.extend(self.path_arg(path))
        sub_cmd_args.extend(self.no_filters_arg(no_filters))
        sub_cmd_args.extend(self.literally_arg(literally))
        sub_cmd_args.extend(self.stdin_arg(stdin))
        sub_cmd_args.extend(self.stdin_paths_arg(stdin_paths))
        sub_cmd_args.extend(self.file_path_args(file_path, *file_paths))
        return sub_cmd_args

    def w_arg(self, w: bool | None) -> list[str]:
        """
        Return ``-w`` if `w` is True.

        >>> IndividuallyOverridableHOCAB().w_arg(True)
        ['-w']
        >>> IndividuallyOverridableHOCAB().w_arg(False)
        []
        >>> IndividuallyOverridableHOCAB().w_arg(None)
        []
        """
        return ["-w"] if w else []

    def type_arg(self, t: Literal["commit", "tree", "blob", "tag"] | None) -> list[str]:
        """
        Return ``-t <type>`` if `t` is provided.

        >>> IndividuallyOverridableHOCAB().type_arg("blob")
        ['-t', 'blob']
        >>> IndividuallyOverridableHOCAB().type_arg("commit")
        ['-t', 'commit']
        >>> IndividuallyOverridableHOCAB().type_arg(None)
        []
        """
        return ["-t", t] if t else []

    def path_arg(self, path: Path | None) -> list[str]:
        """
        Return ``--path=<path>`` if `path` is provided.

        >>> IndividuallyOverridableHOCAB().path_arg(Path("filters/file.txt"))
        ['--path=filters/file.txt']
        >>> IndividuallyOverridableHOCAB().path_arg(None)
        []
        """
        return [f"--path={path}"] if path is not None else []

    def no_filters_arg(self, no_filters: bool | None) -> list[str]:
        """
        Return ``--no-filters`` if `no_filters` is True.

        >>> IndividuallyOverridableHOCAB().no_filters_arg(True)
        ['--no-filters']
        >>> IndividuallyOverridableHOCAB().no_filters_arg(False)
        []
        >>> IndividuallyOverridableHOCAB().no_filters_arg(None)
        []
        """
        return ["--no-filters"] if no_filters else []

    def literally_arg(self, literally: bool | None) -> list[str]:
        """
        Return ``--literally`` if `literally` is True.

        >>> IndividuallyOverridableHOCAB().literally_arg(True)
        ['--literally']
        >>> IndividuallyOverridableHOCAB().literally_arg(False)
        []
        >>> IndividuallyOverridableHOCAB().literally_arg(None)
        []
        """
        return ["--literally"] if literally else []

    def stdin_arg(self, stdin: bytes | None) -> list[str]:
        """
        Return ``--stdin`` if stdin bytes are provided.

        >>> IndividuallyOverridableHOCAB().stdin_arg(b"blob")
        ['--stdin']
        >>> IndividuallyOverridableHOCAB().stdin_arg(None)
        []
        """
        return ["--stdin"] if stdin is not None else []

    def stdin_paths_arg(self, stdin_paths: list[Path] | None) -> list[str]:
        """
        Return ``--stdin-paths`` if `stdin_paths` is provided.

        >>> IndividuallyOverridableHOCAB().stdin_paths_arg([Path("a.txt")])
        ['--stdin-paths']
        >>> IndividuallyOverridableHOCAB().stdin_paths_arg(None)
        []
        """
        return ["--stdin-paths"] if stdin_paths is not None else []

    def file_path_args(self, file_path: Path | None, *file_paths: Path) -> list[str]:
        """
        Return file path operands.

        >>> IndividuallyOverridableHOCAB().file_path_args(Path("a.txt"), Path("b.txt"))
        ['a.txt', 'b.txt']
        >>> IndividuallyOverridableHOCAB().file_path_args(None)
        []
        """
        paths: list[str] = []
        if file_path is not None:
            paths.append(str(file_path))
        paths.extend(str(p) for p in file_paths)
        return paths
