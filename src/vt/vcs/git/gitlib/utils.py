#!/usr/bin/env python3
# coding=utf-8

"""
Utility functions related to processors specific to git commands.
"""
from vt.vcs.git.gitlib.models import GitOpts


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
