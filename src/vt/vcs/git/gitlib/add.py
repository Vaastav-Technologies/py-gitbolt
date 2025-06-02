#!/usr/bin/env python3
# coding=utf-8

"""
Interfaces specific to ``git add`` subcommand.
"""
from abc import abstractmethod
from pathlib import Path
from typing import Protocol, Unpack, override, Literal

from vt.vcs.git.gitlib.models import GitAddOpts
from vt.vcs.git.gitlib.utils import validate_add_args


class AddArgsValidator(Protocol):
    """
    The argument validator for ``git add`` subcommand.
    """

    @abstractmethod
    def validate(self,
                 pathspec: str | None = None,
                 *pathspecs: str,
                 pathspec_from_file: Path | Literal["-"] | None = None,
                 pathspec_stdin: str | None = None,
                 pathspec_file_nul: bool = False,
                 **add_opts: Unpack[GitAddOpts]) -> None:
        """
            Validate the inputs provided to the ``git add`` command.

            This function ensures logical and type-safe usage of arguments that map to the
            ``git add`` subcommand, enforcing mutual exclusivity, argument completeness,
            and correct typing.

            Specifically, it validates:

            * That at least one of ``pathspec`` or ``pathspecs`` is provided unless using ``pathspec_from_file``.
            * That ``pathspec_from_file`` and ``pathspec_stdin`` are not used alongside direct pathspecs.
            * That if ``pathspec_from_file == '-'``, then ``pathspec_stdin`` must be provided.
            * That ``pathspec_stdin`` is not provided unless ``pathspec_from_file == '-'``.
            * That ``pathspec_file_nul`` is a boolean.
            * That each field in ``add_opts`` is correctly typed according to the GitAddOpts spec.

            All validations will raise a ``GitExitingException`` with a specific exit code depending
            on the nature of the failure:

            * ``TypeError`` leads to ``ERR_DATA_FORMAT_ERR``.
            * ``ValueError`` leads to ``ERR_INVALID_USAGE``.

            See: `git add documentation <https://git-scm.com/docs/git-add>`_.

            :param pathspec: A direct file or directory to stage. Cannot be used with ``pathspec_from_file``.
            :type pathspec: str | None
            :param pathspecs: Additional pathspecs to stage.
            :type pathspecs: str
            :param pathspec_from_file: A file to read pathspecs from. Use ``'-'`` to read from stdin.
            :type pathspec_from_file: Path | Literal['-'] | None
            :param pathspec_stdin: Required if ``pathspec_from_file == '-'``. Denotes stdin content.
            :type pathspec_stdin: str | None
            :param pathspec_file_nul: Whether input lines in ``pathspec_from_file`` are NUL-separated.
            :type pathspec_file_nul: bool
            :param add_opts: Options accepted by the ``git add`` subcommand.
            :type add_opts: Unpack[GitAddOpts]
            :raises GitExitingException: When validation fails.
            """
        ...


class UtilAddArgsValidator(AddArgsValidator):
    """
    Directly uses utility function ``validate_add_args()`` to perform add() arguments validation.
    """

    @override
    def validate(self,
                 pathspec: str | None = None,
                 *pathspecs: str,
                 pathspec_from_file: Path | Literal["-"] | None = None,
                 pathspec_stdin: str | None = None,
                 pathspec_file_nul: bool = False,
                 **add_opts: Unpack[GitAddOpts]) -> None:
        """
            Examples::

                >>> UtilAddArgsValidator().validate("README.md", verbose=True)
                >>> UtilAddArgsValidator().validate(pathspec_from_file='-', pathspec_stdin="README.md")
                >>> UtilAddArgsValidator().validate(pathspec_from_file=Path("list.txt"))
                >>> UtilAddArgsValidator().validate("foo/bar.txt", dry_run=True)
                >>> UtilAddArgsValidator().validate(pathspec_from_file=Path("paths.txt"), pathspec_file_nul=True)
                >>> UtilAddArgsValidator().validate("a.txt", "b.txt", force=True, chmod="+x")

            Invalid Examples::

                >>> UtilAddArgsValidator().validate("file.txt", pathspec_file_nul=True)
                Traceback (most recent call last):
                vt.vcs.git.gitlib.exceptions.GitExitingException: ValueError: pathspec_file_nul and pathspec are not allowed together

                >>> UtilAddArgsValidator().validate(pathspec_from_file='-', pathspec_stdin=None)
                Traceback (most recent call last):
                vt.vcs.git.gitlib.exceptions.GitExitingException: ValueError: Both pathspec_stdin and pathspec_from_file are required when pathspec_from_file is '-'.

                >>> UtilAddArgsValidator().validate(pathspec_from_file=Path("x.txt"), pathspec_stdin="foo")
                Traceback (most recent call last):
                vt.vcs.git.gitlib.exceptions.GitExitingException: ValueError: pathspec_stdin is not allowed unless pathspec_from_file is '-'.

                >>> UtilAddArgsValidator().validate(123)  # type: ignore[arg-type]
                Traceback (most recent call last):
                vt.vcs.git.gitlib.exceptions.GitExitingException: TypeError: pathspec must be a string.

                >>> UtilAddArgsValidator().validate("README.md", pathspec_from_file=Path("foo"))
                Traceback (most recent call last):
                vt.vcs.git.gitlib.exceptions.GitExitingException: ValueError: pathspec and pathspec_from_file are not allowed together

                >>> UtilAddArgsValidator().validate("README.md", chmod="bad")  # type: ignore[arg-type]
                Traceback (most recent call last):
                vt.vcs.git.gitlib.exceptions.GitExitingException: ValueError: 'chmod' must be either '+x', '-x', or None

                >>> UtilAddArgsValidator().validate("README.md", verbose="true")  # type: ignore[arg-type]
                Traceback (most recent call last):
                vt.vcs.git.gitlib.exceptions.GitExitingException: TypeError: 'verbose' must be a boolean

                >>> UtilAddArgsValidator().validate(pathspec_from_file="file.txt")  # type: ignore[arg-type]
                Traceback (most recent call last):
                vt.vcs.git.gitlib.exceptions.GitExitingException: TypeError: 'pathspec_from_file' must be a pathlib.Path or the string literal '-'.

                >>> UtilAddArgsValidator().validate(pathspec_stdin="README.md")
                Traceback (most recent call last):
                vt.vcs.git.gitlib.exceptions.GitExitingException: ValueError: pathspec_stdin is not allowed unless pathspec_from_file is '-'.

                >>> UtilAddArgsValidator().validate(pathspec="a.py",
                ...     chmod="777")  # type: ignore[arg-type] # expected +x, -x or None # provided int
                Traceback (most recent call last):
                vt.vcs.git.gitlib.exceptions.GitExitingException: ValueError: 'chmod' must be either '+x', '-x', or None

                >>> UtilAddArgsValidator().validate(pathspec="a.py",
                ...     no_all="yes")  # type: ignore[arg-type] # expected bool # provided int
                Traceback (most recent call last):
                vt.vcs.git.gitlib.exceptions.GitExitingException: ValueError: 'no_all' must be either True, False, or None

                >>> UtilAddArgsValidator().validate(pathspec="a.py",
                ...     renormalize="sometimes")  # type: ignore[arg-type] # expected bool # provided str
                Traceback (most recent call last):
                vt.vcs.git.gitlib.exceptions.GitExitingException: TypeError: 'renormalize' must be a boolean
            """
        validate_add_args(pathspec, *pathspecs, pathspec_from_file=pathspec_from_file,
                          pathspec_stdin=pathspec_stdin, pathspec_file_nul=pathspec_file_nul, **add_opts)
