#!/usr/bin/env python3
# coding=utf-8

"""
Utility functions related to processors specific to git commands.
"""
from typing import Unpack

from vt.utils.commons.commons.core_py import strictly_int
from vt.utils.errors.error_specs import ERR_DATA_FORMAT_ERR, ERR_INVALID_USAGE

from vt.vcs.git.gitlib._internal_init import errmsg_creator
from vt.vcs.git.gitlib.exceptions import GitExitingException
from vt.vcs.git.gitlib.models import GitOpts, GitLsTreeOpts


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

        >>> try:
        ...     validate_ls_tree_args(42)  # noqa: as tree_ish expects str and int is provided
        ... except GitExitingException as e:
        ...     print(e)
        TypeError: tree_ish should be a string.

        >>> try:
        ...     validate_ls_tree_args("HEAD",
        ...                           abbrev="abc")  # noqa: as abbrev expects int and str is provided
        ... except GitExitingException as e:
        ...     print(e)
        TypeError: abbrev must be an integer.

        >>> try:
        ...     validate_ls_tree_args("HEAD",
        ...                           abbrev=True)  # noqa: as abbrev expects int and bool is provided
        ... except GitExitingException as e:
        ...     print(e)
        TypeError: abbrev must be an integer.

        >>> try:
        ...     validate_ls_tree_args("HEAD",
        ...                           abbrev=100)
        ... except GitExitingException as e:
        ...     print(e)
        ValueError: abbrev must be between 0 and 40.

        >>> try:
        ...     validate_ls_tree_args("HEAD",
        ...                           path="src/")  # noqa: as path expects list[str] and str is provided.
        ... except GitExitingException as e:
        ...     print(e)
        TypeError: path must be a list of strings.

        >>> try:
        ...     validate_ls_tree_args("HEAD",
        ...                           z="yes")  # noqa: as z expects bool and str is provided.
        ... except GitExitingException as e:
        ...     print(e)
        TypeError: 'z' must be a boolean.
    """
    if not isinstance(tree_ish, str):
        errmsg = "tree_ish should be a string."
        raise GitExitingException(errmsg, exit_code=ERR_DATA_FORMAT_ERR) from TypeError(errmsg)

    bool_keys = [
        'd', 'r', 't', 'long', 'z', 'name_only', 'object_only',
        'full_name', 'full_tree', 'name_status'
    ]
    for key in bool_keys:
        if key in ls_tree_opts and \
                not isinstance(ls_tree_opts[key], bool): # type: ignore # required as mypy thinks key is not str
            errmsg = f"'{key}' must be a boolean."
            raise GitExitingException(errmsg, exit_code=ERR_DATA_FORMAT_ERR) from TypeError(errmsg)

    if "abbrev" in ls_tree_opts:
        abbrev = ls_tree_opts["abbrev"]
        if not strictly_int(abbrev):
            errmsg = "abbrev must be an integer."
            raise GitExitingException(errmsg, exit_code=ERR_DATA_FORMAT_ERR) from TypeError(errmsg)
        if not (0 <= abbrev <= 40):
            errmsg = "abbrev must be between 0 and 40."
            raise GitExitingException(errmsg, exit_code=ERR_INVALID_USAGE) from ValueError(errmsg)

    if "format_" in ls_tree_opts and not isinstance(ls_tree_opts["format_"], str):
        errmsg = "format_ must be a string."
        raise GitExitingException(errmsg, exit_code=ERR_DATA_FORMAT_ERR) from TypeError(errmsg)

    if "path" in ls_tree_opts:
        path = ls_tree_opts["path"]
        if not isinstance(path, list) or not all(isinstance(p, str) for p in path):
            errmsg = "path must be a list of strings."
            raise GitExitingException(errmsg, exit_code=ERR_DATA_FORMAT_ERR) from TypeError(errmsg)
