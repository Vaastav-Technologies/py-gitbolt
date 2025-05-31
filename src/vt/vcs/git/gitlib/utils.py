#!/usr/bin/env python3
# coding=utf-8

"""
Utility functions related to processors specific to git commands.
"""
from __future__ import annotations

from pathlib import Path
from typing import Unpack, Literal

from vt.utils.commons.commons.core_py import strictly_int, has_atleast_one_arg, ensure_atleast_one_arg
from vt.utils.errors.error_specs import ERR_DATA_FORMAT_ERR, ERR_INVALID_USAGE
from vt.utils.errors.error_specs.utils import require_type, require_iterable

from vt.vcs.git.gitlib._internal_init import errmsg_creator
from vt.vcs.git.gitlib.exceptions import GitExitingException
from vt.vcs.git.gitlib.models import GitOpts, GitLsTreeOpts, GitAddOpts


def merge_git_opts(primary: GitOpts, fallback: GitOpts) -> GitOpts:
    """
    Merge the ``primary`` and ``fallback`` ``GitOpts`` object and return a new ``GitOpts`` object.

    Construction of the new ``GitOpts`` object is done such that:

    * first prioritise picking up a property from the ``primary``.
    * if a property is ``None`` in the ``primary`` then that corresponding property is picked from the ``fallback``.

    Example usage:

    >>> from pathlib import Path
    >>> from typing import cast
    >>> _primary = cast(GitOpts, {
    ...     "C": [Path("/repo")],
    ...     "c": {"user.name": "Alice", "color.ui": None},
    ...     "paginate": True,
    ...     "no_pager": None,
    ...     "exec_path": None,
    ...     "git_dir": Path("/repo/.git"),
    ...     "work_tree": None,
    ...     "bare": None,
    ...     "namespace": None
    ... })
    >>> _fallback = cast(GitOpts, {
    ...     "C": [Path("/fallback")],
    ...     "c": {"user.name": "Bob", "core.editor": "vim"},
    ...     "paginate": False,
    ...     "no_pager": True,
    ...     "exec_path": Path("/usr/lib/git-core"),
    ...     "git_dir": None,
    ...     "work_tree": Path("/fallback"),
    ...     "bare": True,
    ...     "namespace": "fallback-ns"
    ... })
    >>> _merged = merge_git_opts(_primary, _fallback)
    >>> _merged["C"] == [Path("/repo")]
    True
    >>> _merged["c"]
    {'user.name': 'Alice', 'color.ui': None}
    >>> _merged["paginate"]
    True
    >>> _merged["no_pager"]
    True
    >>> _merged["exec_path"] == Path("/usr/lib/git-core")
    True
    >>> _merged["git_dir"] == Path("/repo/.git")
    True
    >>> _merged["work_tree"] == Path("/fallback")
    True
    >>> _merged["bare"]
    True
    >>> _merged["namespace"]
    'fallback-ns'

    Empty example:

    >>> merge_git_opts({}, {})
    {'C': None, 'c': None, 'config_env': None, 'exec_path': None, 'paginate': None, 'no_pager': None, 'git_dir': None, 'work_tree': None, 'namespace': None, 'bare': None, 'no_replace_objects': None, 'no_lazy_fetch': None, 'no_optional_locks': None, 'no_advice': None, 'literal_pathspecs': None, 'glob_pathspecs': None, 'noglob_pathspecs': None, 'icase_pathspecs': None, 'list_cmds': None, 'attr_source': None}

    Partial fallback behavior:

    >>> merge_git_opts({"paginate": None}, {"paginate": True})["paginate"]
    True
    >>> merge_git_opts({"paginate": None}, {"paginate": None})["paginate"] is None
    True
    >>> merge_git_opts({"paginate": False}, {"paginate": True})["paginate"]
    False

    :param primary: The first priority ``GitOpts`` object.
    :param fallback: the second priority or fallback ``GitOpts`` object.
    :return: A new ``GitOpts`` object that contains all the properties from the ``primary`` ``GitOpts`` object and
        fallbacks on the corresponding property from the ``fallback`` ``GitOpts`` object if that corresponding property
        is ``None`` in the ``primary`` ``GitOpts`` object.
    """
    merged: GitOpts = {}
    for k in GitOpts.__annotations__.keys(): # type: ignore
        val = primary.get(k) # type: ignore # required as mypy thinks k is not str
        if val is None:
            val = fallback.get(k) # type: ignore # required as mypy thinks k is not str
        merged[k] = val # type: ignore # required as mypy thinks k is not str
    return merged


def validate_ls_tree_args(tree_ish: str, **ls_tree_opts: Unpack[GitLsTreeOpts]) -> None:
    """
    Validate the inputs provided to the ``git ls-tree`` command.

    This utility ensures type safety and logical correctness of arguments
    passed to the ``git ls-tree`` subcommand.

    This includes:
    * Enforcing that ``tree_ish`` is a string.
    * Checking that each supported boolean flag (like ``d``, ``r``, ``z``, etc.)
      is a valid boolean if provided.
    * Validating that ``abbrev`` is an integer between 0 and 40 (inclusive).
    * Ensuring ``format_`` is a string if specified.
    * Checking that ``path`` is a list of strings if specified.

    All validations will raise a ``GitExitingException`` with a specific
    exit code depending on the nature of the failure:

    * ``TypeError`` leads to ``ERR_DATA_FORMAT_ERR``.
    * ``ValueError`` leads to ``ERR_INVALID_USAGE``.

    See: `git ls-tree documentation <https://git-scm.com/docs/git-ls-tree>`_.

    :param tree_ish: A valid Git tree-ish identifier (e.g., branch name, commit hash).
    :param ls_tree_opts: Keyword arguments that map to valid ls-tree options.
    :raises GitExitingException: When validation fails.

    Examples::

        >>> validate_ls_tree_args("HEAD", d=True, abbrev=10)
        >>> validate_ls_tree_args("abc123", format_="%(objectname)", path=["src/", "README.md"])
        >>> validate_ls_tree_args("main", name_only=False, z=True)


    Invalid Examples (will raise GitExitingException), printing these just for doctesting::

        >>> validate_ls_tree_args(42) # type: ignore[arg-type] # tree_ish expects str and int is provided
        Traceback (most recent call last):
        vt.vcs.git.gitlib.exceptions.GitExitingException: TypeError: 'tree_ish' must be of type str

        >>> validate_ls_tree_args("HEAD", abbrev="abc") # type: ignore[arg-type] # abbrev expects int and str is provided
        Traceback (most recent call last):
        vt.vcs.git.gitlib.exceptions.GitExitingException: TypeError: 'abbrev' must be of type int

        >>> validate_ls_tree_args("HEAD", abbrev=True) # type: ignore[arg-type] # abbrev expects int and bool is provided
        Traceback (most recent call last):
        vt.vcs.git.gitlib.exceptions.GitExitingException: TypeError: 'abbrev' must be of type int

        >>> validate_ls_tree_args("HEAD", abbrev=100)
        Traceback (most recent call last):
        vt.vcs.git.gitlib.exceptions.GitExitingException: ValueError: abbrev must be between 0 and 40.

        >>> validate_ls_tree_args("HEAD",
        ...                       path="src/")  # type: ignore[arg-type] as path expects list[str] and str is provided.
        Traceback (most recent call last):
        vt.vcs.git.gitlib.exceptions.GitExitingException: TypeError: 'path' must be a non-str iterable

        >>> validate_ls_tree_args("HEAD",
        ...                       path=1)  # type: ignore[arg-type] as path expects list[str] and str is provided.
        Traceback (most recent call last):
        vt.vcs.git.gitlib.exceptions.GitExitingException: TypeError: 'path' must be a non-str iterable

        >>> validate_ls_tree_args("HEAD",
        ...                         z="yes")  # type: ignore[arg-type] as z expects bool and str is provided.
        Traceback (most recent call last):
        vt.vcs.git.gitlib.exceptions.GitExitingException: TypeError: 'z' must be of type bool
    """
    require_type(tree_ish, 'tree_ish', str, GitExitingException)

    bool_keys = [
        'd', 'r', 't', 'long', 'z', 'name_only', 'object_only',
        'full_name', 'full_tree', 'name_status'
    ]
    for key in bool_keys:
        if key in ls_tree_opts:
            the_key = ls_tree_opts[key] # type: ignore[arg-type] # required as mypy thinks key is not str
            require_type(the_key, key, bool, GitExitingException)

    if "abbrev" in ls_tree_opts:
        abbrev = ls_tree_opts["abbrev"]
        require_type(abbrev, 'abbrev', int, GitExitingException)
        if not strictly_int(abbrev):
            errmsg = "'abbrev' must be of type int"
            raise GitExitingException(errmsg, exit_code=ERR_DATA_FORMAT_ERR) from TypeError(errmsg)
        if not (0 <= abbrev <= 40):
            errmsg = "abbrev must be between 0 and 40."
            raise GitExitingException(errmsg, exit_code=ERR_INVALID_USAGE) from ValueError(errmsg)

    if "format_" in ls_tree_opts:
        format_ = ls_tree_opts['format_']
        require_type(format_, 'format_', str, GitExitingException)

    if "path" in ls_tree_opts:
        path = ls_tree_opts["path"]
        require_iterable(path, 'path', str, list, GitExitingException)


def validate_add_args(pathspec: str | None = None,
                      *pathspecs: str,
                      pathspec_from_file: Path | Literal['-'] | None = None,
                      pathspec_stdin: str | None = None,
                      pathspec_file_nul: bool = False,
                      **add_opts: Unpack[GitAddOpts]):
    """

    :param pathspec:
    :param pathspecs:
    :param pathspec_from_file:
    :param pathspec_stdin:
    :param pathspec_file_nul:
    :param add_opts:
    :raises GitExitingException: if any validation fails.
    """
    # region Argument exclusivity checks
    if has_atleast_one_arg(pathspec, *pathspecs, enforce_type=False):
        try:
            ensure_atleast_one_arg(pathspec, *pathspecs)
        except TypeError as te:
            raise GitExitingException(exit_code=ERR_DATA_FORMAT_ERR) from te

        if pathspec_from_file is not None:
            errmsg = errmsg_creator.not_allowed_together('pathspec', 'pathspec_from_file')
            raise GitExitingException(errmsg, exit_code=ERR_INVALID_USAGE) from ValueError(errmsg)
        if pathspec_stdin is not None:
            errmsg = errmsg_creator.not_allowed_together('pathspec', 'pathspec_stdin')
            raise GitExitingException(errmsg, exit_code=ERR_INVALID_USAGE) from ValueError(errmsg)
        if pathspec_file_nul:
            errmsg = errmsg_creator.not_allowed_together('pathspec_file_null', 'pathspec')
            raise GitExitingException(errmsg, exit_code=ERR_INVALID_USAGE) from ValueError(errmsg)

    if pathspec_from_file == "-" and pathspec_stdin is None:
        errmsg = errmsg_creator.all_required('pathspec_stdin', 'pathspec_from_file',
                                             suffix=" when pathspec_from_file is '-'.")
        raise GitExitingException(errmsg, exit_code=ERR_INVALID_USAGE) from ValueError(errmsg)
    if pathspec_from_file != '-' and pathspec_stdin is not None:
        errmsg = errmsg_creator.not_allowed_together('pathspec_form_file', 'pathspec_stdin',
                                                     suffix=" when pathspec_from_file is not equal to '-'.")
        raise GitExitingException(errmsg, exit_code=ERR_INVALID_USAGE) from ValueError(errmsg)
    # endregion

    if verbose := add_opts.get('verbose'):
        require_type(verbose, 'verbose', bool)
