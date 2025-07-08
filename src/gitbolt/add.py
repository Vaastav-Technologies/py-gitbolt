#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces specific to ``git add`` subcommand.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Protocol, Unpack, override, Literal

from gitbolt._internal_init import errmsg_creator
from gitbolt.exceptions import GitExitingException
from gitbolt.models import GitAddOpts
from vt.utils.commons.commons.core_py import has_atleast_one_arg, ensure_atleast_one_arg
from vt.utils.errors.error_specs import ERR_DATA_FORMAT_ERR, ERR_INVALID_USAGE
from vt.utils.errors.error_specs.utils import require_type


class AddArgsValidator(Protocol):
    """
    The argument validator for ``git add`` subcommand.
    """

    @abstractmethod
    def validate(
        self,
        pathspec: str | None = None,
        *pathspecs: str,
        pathspec_from_file: Path | Literal["-"] | None = None,
        pathspec_stdin: str | None = None,
        pathspec_file_nul: bool = False,
        **add_opts: Unpack[GitAddOpts],
    ) -> None:
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
    Independent utility function sort of interface to perform add() arguments validation.
    """

    @override
    def validate(
        self,
        pathspec: str | None = None,
        *pathspecs: str,
        pathspec_from_file: Path | Literal["-"] | None = None,
        pathspec_stdin: str | None = None,
        pathspec_file_nul: bool = False,
        **add_opts: Unpack[GitAddOpts],
    ) -> None:
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
            gitbolt.exceptions.GitExitingException: ValueError: pathspec_file_nul and pathspec are not allowed together

            >>> UtilAddArgsValidator().validate(pathspec_from_file='-', pathspec_stdin=None)
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: pathspec_stdin must be provided when pathspec_form_file is -

            >>> UtilAddArgsValidator().validate(pathspec_from_file=Path("x.txt"), pathspec_stdin="foo")
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: pathspec_stdin is not allowed unless pathspec_from_file is '-'.

            >>> UtilAddArgsValidator().validate(123)  # type: ignore[arg-type]
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: pathspec must be a string.

            >>> UtilAddArgsValidator().validate("README.md", pathspec_from_file=Path("foo"))
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: pathspec and pathspec_from_file are not allowed together

            >>> UtilAddArgsValidator().validate("README.md", chmod="bad")  # type: ignore[arg-type]
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: Unexpected chmod value. Choose from '+x' and '-x'.

            >>> UtilAddArgsValidator().validate("README.md", verbose="true")  # type: ignore[arg-type]
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'verbose' must be a boolean

            >>> UtilAddArgsValidator().validate(pathspec_from_file="file.txt")  # type: ignore[arg-type]
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'pathspec_from_file' must be a pathlib.Path or the string literal '-'.

            >>> UtilAddArgsValidator().validate(pathspec_stdin="README.md")
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: Either pathspec or pathspec_from_file is required

            >>> UtilAddArgsValidator().validate(pathspec="a.py",
            ...     chmod="777")  # type: ignore[arg-type] # expected +x, -x or None # provided int
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: Unexpected chmod value. Choose from '+x' and '-x'.

            >>> UtilAddArgsValidator().validate(pathspec="a.py",
            ...     no_all="yes")  # type: ignore[arg-type] # expected bool # provided int
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'no_all' must be either True, False, or None

            >>> UtilAddArgsValidator().validate(pathspec="a.py",
            ...     renormalize="sometimes")  # type: ignore[arg-type] # expected bool # provided str
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'renormalize' must be a boolean

            >>> UtilAddArgsValidator().validate(verbose=True)
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: Either pathspec or pathspec_from_file is required
        """
        self.mandate_required_arguments(
            pathspec,
            *pathspecs,
            pathspec_from_file=pathspec_from_file,
            pathspec_stdin=pathspec_stdin,
        )
        self.validate_exclusive_args(
            pathspec,
            *pathspecs,
            pathspec_from_file=pathspec_from_file,
            pathspec_stdin=pathspec_stdin,
            pathspec_file_nul=pathspec_file_nul,
        )
        self.validate_git_add_opts(**add_opts)
        self.validate_non_git_add_opts(
            pathspec_file_nul, pathspec_from_file, pathspec_stdin
        )

    def mandate_required_arguments(
        self,
        pathspec: str | None,
        *pathspecs: str,
        pathspec_from_file: Path | Literal["-"] | None,
        pathspec_stdin: str | None,
    ):
        """
        One of ``pathspec``, ``pathspec_from_file`` or ``pathspec_from_file=- pathspec_stdin`` must be provided.

        Examples:

        * All three provided, no issue:

        >>> UtilAddArgsValidator().mandate_required_arguments('add.py', 'more-add.py', 'even-more.txt',
        ...                 pathspec_from_file=Path('a-file.txt'), pathspec_stdin='a str')

        * Pairs provided, no issue:

        >>> UtilAddArgsValidator().mandate_required_arguments('add.py', 'more-add.py', 'even-more.txt',
        ...                 pathspec_from_file=Path('a-file.txt'), pathspec_stdin=None)
        >>> UtilAddArgsValidator().mandate_required_arguments('add.py', 'more-add.py', 'even-more.txt',
        ...                 pathspec_from_file=None, pathspec_stdin='a stdin str')
        >>> UtilAddArgsValidator().mandate_required_arguments(None, pathspec_from_file=Path('a-file.txt'),
        ...                 pathspec_stdin='a stdin str')

        * Provided single required, no issue:

        >>> UtilAddArgsValidator().mandate_required_arguments('add.py', pathspec_from_file=None, pathspec_stdin=None)
        >>> UtilAddArgsValidator().mandate_required_arguments('add.py', 'more-add.py', 'even-more.txt', pathspec_from_file=None, pathspec_stdin=None)
        >>> UtilAddArgsValidator().mandate_required_arguments(None, pathspec_from_file=Path('a-file.txt'), pathspec_stdin=None)

        * Provided ``pathspec_stdin`` with pathpec_from_file=-``, no issue:

        >>> UtilAddArgsValidator().mandate_required_arguments(None, pathspec_from_file='-', pathspec_stdin='stdin pathspec')

        Error examples:

        * No mandatory args provided:

        >>> UtilAddArgsValidator().mandate_required_arguments(None, pathspec_from_file=None, pathspec_stdin=None)
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: Either pathspec or pathspec_from_file is required

        * ``pathspec_stdin`` not provided when ``pathspec_from_file=-``:

        >>> UtilAddArgsValidator().mandate_required_arguments(None, pathspec_from_file='-', pathspec_stdin=None)
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: pathspec_stdin must be provided when pathspec_form_file is -

        :raises GitExitingException: if no mandatory args are provided.
        """
        if (
            not has_atleast_one_arg(pathspec, *pathspecs, enforce_type=False)
            and pathspec_from_file is None
        ):
            errmsg = errmsg_creator.at_least_one_required(
                "pathspec", "pathspec_from_file"
            )
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if pathspec_from_file == "-" and pathspec_stdin is None:
            errmsg = "pathspec_stdin must be provided when pathspec_form_file is -"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    def validate_exclusive_args(
        self,
        pathspec: str | None,
        *pathspecs: str,
        pathspec_from_file: Path | Literal["-"] | None,
        pathspec_stdin: str | None,
        pathspec_file_nul: bool | None,
    ) -> None:
        """
        Method added so that subclasses may override as they please.

        Check that exclusive args are not provided together.

        Examples::

            >>> UtilAddArgsValidator().validate("file.txt", pathspec_file_nul=True)
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: pathspec_file_nul and pathspec are not allowed together

            >>> UtilAddArgsValidator().validate(pathspec_from_file='-', pathspec_stdin=None)
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: pathspec_stdin must be provided when pathspec_form_file is -

            >>> UtilAddArgsValidator().validate(pathspec_from_file='-')
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: pathspec_stdin must be provided when pathspec_form_file is -

            >>> UtilAddArgsValidator().validate(pathspec_from_file=Path("x.txt"), pathspec_stdin="foo")
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: pathspec_stdin is not allowed unless pathspec_from_file is '-'.

            >>> UtilAddArgsValidator().validate("README.md", pathspec_from_file=Path("foo"))
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: pathspec and pathspec_from_file are not allowed together

            >>> UtilAddArgsValidator().validate(pathspec_from_file="file.txt")  # type: ignore[arg-type]
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: TypeError: 'pathspec_from_file' must be a pathlib.Path or the string literal '-'.

            >>> UtilAddArgsValidator().validate(pathspec_stdin="README.md")
            Traceback (most recent call last):
            gitbolt.exceptions.GitExitingException: ValueError: Either pathspec or pathspec_from_file is required

        :raises GitExitingException: if exclusive args are provided together.
        """
        if has_atleast_one_arg(pathspec, *pathspecs, enforce_type=False):
            try:
                ensure_atleast_one_arg(pathspec, *pathspecs, enforce_type=str)
            except TypeError as te:
                raise GitExitingException(
                    "pathspec must be a string.", exit_code=ERR_DATA_FORMAT_ERR
                ) from te

            if pathspec_from_file is not None:
                errmsg = errmsg_creator.not_allowed_together(
                    "pathspec", "pathspec_from_file"
                )
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
            if pathspec_stdin is not None:
                errmsg = errmsg_creator.not_allowed_together(
                    "pathspec", "pathspec_stdin"
                )
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
            if pathspec_file_nul:
                errmsg = errmsg_creator.not_allowed_together(
                    "pathspec_file_nul", "pathspec"
                )
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
        if pathspec_from_file == "-" and pathspec_stdin is None:
            errmsg = errmsg_creator.all_required(
                "pathspec_stdin",
                "pathspec_from_file",
                suffix=" when pathspec_from_file is '-'.",
            )
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if pathspec_from_file != "-" and pathspec_stdin is not None:
            errmsg = "pathspec_stdin is not allowed unless pathspec_from_file is '-'."
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    # region validate_git_add_opts
    def validate_git_add_opts(self, **add_opts: Unpack[GitAddOpts]) -> None:
        """
        Validate Git add command specific options.
        Delegates to specialized validation methods.

        >>> UtilAddArgsValidator().validate_git_add_opts(verbose=True, chmod='+x', no_all=False)
        >>> UtilAddArgsValidator().validate_git_add_opts(verbose='yes') # type: ignore[arg-type] # expected bool provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'verbose' must be a boolean
        """
        self.validate_bool_args(**add_opts)
        self.validate_tri_state_args(**add_opts)
        self.validate_chmod_arg(add_opts.get("chmod"))

    # region validate_bool_args
    def validate_bool_args(self, **bool_add_opts: Unpack[GitAddOpts]) -> None:
        """
        Validate boolean Git add options like 'verbose', 'dry_run', etc.

        >>> UtilAddArgsValidator().validate_bool_args(verbose=True)
        >>> UtilAddArgsValidator().validate_bool_args(verbose='true') # type: ignore[arg-type] # expected bool provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'verbose' must be a boolean
        """
        if "verbose" in bool_add_opts:
            self.validate_verbose_bool_arg(bool_add_opts["verbose"])
        if "dry_run" in bool_add_opts:
            self.validate_dry_run_bool_arg(bool_add_opts["dry_run"])
        if "force" in bool_add_opts:
            self.validate_force_bool_arg(bool_add_opts["force"])
        if "interactive" in bool_add_opts:
            self.validate_interactive_bool_arg(bool_add_opts["interactive"])
        if "patch" in bool_add_opts:
            self.validate_patch_bool_arg(bool_add_opts["patch"])
        if "edit" in bool_add_opts:
            self.validate_edit_bool_arg(bool_add_opts["edit"])
        if "sparse" in bool_add_opts:
            self.validate_sparse_bool_arg(bool_add_opts["sparse"])
        if "intent_to_add" in bool_add_opts:
            self.validate_intent_to_add_bool_arg(bool_add_opts["intent_to_add"])
        if "refresh" in bool_add_opts:
            self.validate_refresh_bool_arg(bool_add_opts["refresh"])
        if "ignore_errors" in bool_add_opts:
            self.validate_ignore_errors_bool_arg(bool_add_opts["ignore_errors"])
        if "ignore_missing" in bool_add_opts:
            self.validate_ignore_missing_bool_arg(bool_add_opts["ignore_missing"])
        if "renormalize" in bool_add_opts:
            self.validate_renormalize_bool_arg(bool_add_opts["renormalize"])

    def validate_verbose_bool_arg(self, verbose: bool) -> None:
        """Validate `verbose` argument.

        >>> UtilAddArgsValidator().validate_verbose_bool_arg(True)
        >>> UtilAddArgsValidator().validate_verbose_bool_arg('yes') # type: ignore[arg-type] # expected bool provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'verbose' must be a boolean
        """
        require_type(verbose, "verbose", bool, GitExitingException)

    def validate_dry_run_bool_arg(self, dry_run: bool) -> None:
        """Validate `dry_run` argument.

        >>> UtilAddArgsValidator().validate_dry_run_bool_arg(False)
        >>> UtilAddArgsValidator().validate_dry_run_bool_arg(1) # type: ignore[arg-type] # expected bool provided int
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'dry_run' must be a boolean
        """
        require_type(dry_run, "dry_run", bool, GitExitingException)

    def validate_force_bool_arg(self, force: bool) -> None:
        """Validate `force` argument.

        >>> UtilAddArgsValidator().validate_force_bool_arg(True)
        >>> UtilAddArgsValidator().validate_force_bool_arg('true') # type: ignore[arg-type] # expected bool provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'force' must be a boolean
        """
        require_type(force, "force", bool, GitExitingException)

    def validate_interactive_bool_arg(self, interactive: bool) -> None:
        """Validate `interactive` argument.

        >>> UtilAddArgsValidator().validate_interactive_bool_arg(False)
        >>> UtilAddArgsValidator().validate_interactive_bool_arg('false') # type: ignore[arg-type] # expected bool provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'interactive' must be a boolean
        """
        require_type(interactive, "interactive", bool, GitExitingException)

    def validate_patch_bool_arg(self, patch: bool) -> None:
        """Validate `patch` argument.

        >>> UtilAddArgsValidator().validate_patch_bool_arg(True)
        >>> UtilAddArgsValidator().validate_patch_bool_arg(0.1) # type: ignore[arg-type] # expected bool provided float
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'patch' must be a boolean
        """
        require_type(patch, "patch", bool, GitExitingException)

    def validate_edit_bool_arg(self, edit: bool) -> None:
        """Validate `edit` argument.

        >>> UtilAddArgsValidator().validate_edit_bool_arg(True)
        >>> UtilAddArgsValidator().validate_edit_bool_arg('no') # type: ignore[arg-type] # expected bool provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'edit' must be a boolean
        """
        require_type(edit, "edit", bool, GitExitingException)

    def validate_sparse_bool_arg(self, sparse: bool) -> None:
        """Validate `sparse` argument.

        >>> UtilAddArgsValidator().validate_sparse_bool_arg(True)
        >>> UtilAddArgsValidator().validate_sparse_bool_arg(None) # type: ignore[arg-type] # expected bool provided None
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'sparse' must be a boolean
        """
        require_type(sparse, "sparse", bool, GitExitingException)

    def validate_intent_to_add_bool_arg(self, intent_to_add: bool) -> None:
        """Validate `intent_to_add` argument.

        >>> UtilAddArgsValidator().validate_intent_to_add_bool_arg(False)
        >>> UtilAddArgsValidator().validate_intent_to_add_bool_arg('maybe') # type: ignore[arg-type] # expected bool provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'intent_to_add' must be a boolean
        """
        require_type(intent_to_add, "intent_to_add", bool, GitExitingException)

    def validate_refresh_bool_arg(self, refresh: bool) -> None:
        """Validate `refresh` argument.

        >>> UtilAddArgsValidator().validate_refresh_bool_arg(True)
        >>> UtilAddArgsValidator().validate_refresh_bool_arg([]) # type: ignore[arg-type] # expected bool provided list
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'refresh' must be a boolean
        """
        require_type(refresh, "refresh", bool, GitExitingException)

    def validate_ignore_errors_bool_arg(self, ignore_errors: bool) -> None:
        """Validate `ignore_errors` argument.

        >>> UtilAddArgsValidator().validate_ignore_errors_bool_arg(True)
        >>> UtilAddArgsValidator().validate_ignore_errors_bool_arg('error') # type: ignore[arg-type] # expected bool provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'ignore_errors' must be a boolean
        """
        require_type(ignore_errors, "ignore_errors", bool, GitExitingException)

    def validate_ignore_missing_bool_arg(self, ignore_missing: bool) -> None:
        """Validate `ignore_missing` argument.

        >>> UtilAddArgsValidator().validate_ignore_missing_bool_arg(False)
        >>> UtilAddArgsValidator().validate_ignore_missing_bool_arg('none') # type: ignore[arg-type] # expected bool provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'ignore_missing' must be a boolean
        """
        require_type(ignore_missing, "ignore_missing", bool, GitExitingException)

    def validate_renormalize_bool_arg(self, renormalize: bool) -> None:
        """
        Validate `renormalize` argument.

        >>> UtilAddArgsValidator().validate_renormalize_bool_arg(True)
        >>> UtilAddArgsValidator().validate_renormalize_bool_arg('false') # type: ignore[arg-type] # expected bool provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'renormalize' must be a boolean
        """
        require_type(renormalize, "renormalize", bool, GitExitingException)

    # endregion

    # region validate_tri_state_args
    def validate_tri_state_args(self, **tri_state_add_opts: Unpack[GitAddOpts]) -> None:
        """
        Validate tri-state arguments that accept True, False, or None.

        >>> UtilAddArgsValidator().validate_tri_state_args(no_all=None)
        >>> UtilAddArgsValidator().validate_tri_state_args(no_all='yes') # type: ignore[arg-type] # expected [bool | None] provided str
        Traceback (most recent call last):
        ...
        gitbolt.exceptions.GitExitingException: TypeError: 'no_all' must be either True, False, or None
        """
        if "no_all" in tri_state_add_opts:
            self.validate_no_all_tri_state_arg(tri_state_add_opts["no_all"])
        if "no_ignore_removal" in tri_state_add_opts:
            self.validate_no_ignore_removal_tri_state_arg(
                tri_state_add_opts["no_ignore_removal"]
            )

    def validate_no_all_tri_state_arg(self, no_all: bool | None) -> None:
        """
        Validate `no_all` tri-state argument.

        >>> UtilAddArgsValidator().validate_no_all_tri_state_arg(True)
        >>> UtilAddArgsValidator().validate_no_all_tri_state_arg(None)
        >>> UtilAddArgsValidator().validate_no_all_tri_state_arg('bad') # type: ignore[arg-type] # expected [bool | None] provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'no_all' must be either True, False, or None
        """
        if no_all not in (True, False, None):
            errmsg = "'no_all' must be either True, False, or None"
            raise GitExitingException(
                errmsg, exit_code=ERR_DATA_FORMAT_ERR
            ) from TypeError(errmsg)

    def validate_no_ignore_removal_tri_state_arg(
        self, no_ignore_removal: bool | None
    ) -> None:
        """
        Validate `no_ignore_removal` tri-state argument.

        >>> UtilAddArgsValidator().validate_no_ignore_removal_tri_state_arg(False)
        >>> UtilAddArgsValidator().validate_no_ignore_removal_tri_state_arg('nope') # type: ignore[arg-type] # expected [bool | None] provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'no_ignore_removal' must be either True, False, or None
        """
        if no_ignore_removal not in (True, False, None):
            errmsg = "'no_ignore_removal' must be either True, False, or None"
            raise GitExitingException(
                errmsg, exit_code=ERR_DATA_FORMAT_ERR
            ) from TypeError(errmsg)

    # endregion

    def validate_chmod_arg(self, chmod: Literal["+x", "-x"] | None) -> None:
        """
        Validate `chmod` argument.

        >>> UtilAddArgsValidator().validate_chmod_arg('+x')
        >>> UtilAddArgsValidator().validate_chmod_arg(None)
        >>> UtilAddArgsValidator().validate_chmod_arg('bad') # type: ignore[arg-type] # expected Literal[+x, -x] provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: Unexpected chmod value. Choose from '+x' and '-x'.
        """
        if chmod:
            if chmod not in ("+x", "-x"):
                errmsg = errmsg_creator.errmsg_for_choices(
                    emphasis="chmod", choices=["+x", "-x"]
                )
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)

    # endregion

    # region validate_non_git_add_opts
    def validate_non_git_add_opts(
        self,
        pathspec_file_nul: bool,
        pathspec_from_file: Path | Literal["-"] | None,
        pathspec_stdin: str | None,
    ) -> None:
        """
        Validate non-GitAddOpts arguments like pathspec_from_file and pathspec_stdin.

        >>> validator = UtilAddArgsValidator()
        >>> validator.validate_non_git_add_opts(False, None, None)
        >>> validator.validate_non_git_add_opts(True, '-', 'abc')
        >>> validator.validate_non_git_add_opts(True, '-', 123) # type: ignore[arg-type] # expected str # provided int
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'pathspec_stdin' must be a string
        """
        self.validate_pathspec_file_nul(pathspec_file_nul)
        self.validate_pathspec_from_file(pathspec_from_file)
        self.validate_pathspec_stdin(pathspec_stdin)

    def validate_pathspec_file_nul(self, pathspec_file_nul: bool) -> None:
        """
        Validate `pathspec_file_nul` argument.

        >>> UtilAddArgsValidator().validate_pathspec_file_nul(True)
        >>> UtilAddArgsValidator().validate_pathspec_file_nul('yes') # type: ignore[arg-type] # expected bool # provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'pathspec_file_nul' must be a boolean
        """
        require_type(pathspec_file_nul, "pathspec_file_nul", bool, GitExitingException)

    def validate_pathspec_from_file(
        self, pathspec_from_file: Path | Literal["-"] | None
    ) -> None:
        """
        Validate `pathspec_from_file` argument.

        >>> UtilAddArgsValidator().validate_pathspec_from_file(Path("foo.txt"))
        >>> UtilAddArgsValidator().validate_pathspec_from_file('-')
        >>> UtilAddArgsValidator().validate_pathspec_from_file(123) # type: ignore[arg-type] # expected Path | Literal['-'] # provided int
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'pathspec_from_file' must be a pathlib.Path or the string literal '-'.
        >>> UtilAddArgsValidator().validate_pathspec_from_file('file.txt') # type: ignore[arg-type] # expected Path | Literal['-'] # provided str
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'pathspec_from_file' must be a pathlib.Path or the string literal '-'.
        """
        if pathspec_from_file is not None:
            if (
                not isinstance(pathspec_from_file, (Path, str))
                or pathspec_from_file != "-"
                and not isinstance(pathspec_from_file, Path)
            ):
                errmsg = "'pathspec_from_file' must be a pathlib.Path or the string literal '-'."
                raise GitExitingException(
                    errmsg, exit_code=ERR_DATA_FORMAT_ERR
                ) from TypeError(errmsg)

    def validate_pathspec_stdin(self, pathspec_stdin: str | None):
        """

        Validate `pathspec_stdin` argument.

        >>> UtilAddArgsValidator().validate_pathspec_stdin('-')
        >>> UtilAddArgsValidator().validate_pathspec_stdin('some stdin')
        >>> UtilAddArgsValidator().validate_pathspec_stdin(123) # type: ignore[arg-type] # expected str # provided int
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: TypeError: 'pathspec_stdin' must be a string
        """
        if pathspec_stdin is not None:
            require_type(pathspec_stdin, "pathspec_stdin", str, GitExitingException)

    # endregion
