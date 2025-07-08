#!/usr/bin/env python3
# coding=utf-8

"""
Utility functions related to processors specific to git commands.
"""

from __future__ import annotations


from gitbolt.models import GitOpts, GitEnvVars


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
    {}

    Partial fallback behavior:

    >>> merge_git_opts({"paginate": None}, {"paginate": True})["paginate"]
    True
    >>> 'paginate' in merge_git_opts({"paginate": None}, {"paginate": None})
    False
    >>> merge_git_opts({"paginate": False}, {"paginate": True})["paginate"]
    False

    :param primary: The first priority ``GitOpts`` object.
    :param fallback: the second priority or fallback ``GitOpts`` object.
    :return: A new ``GitOpts`` object that contains all the properties from the ``primary`` ``GitOpts`` object and
        fallbacks on the corresponding property from the ``fallback`` ``GitOpts`` object if that corresponding property
        is ``None`` in the ``primary`` ``GitOpts`` object.
    """
    return merge_typed_dicts(primary, fallback, GitOpts)


def merge_git_envs(primary: GitEnvVars, fallback: GitEnvVars) -> GitEnvVars:
    """
    Merge the ``primary`` and ``fallback`` ``GitEnvVars`` objects and return a new ``GitEnvVars`` object.

    Construction of the new ``GitEnvVars`` object is done such that:

    * values from ``primary`` are prioritized.
    * if a key exists in both, and the value in ``primary`` is explicitly ``None``, then the value from ``fallback`` is used.
    * if a value in ``primary`` is ``Unset``, it is retained and does not fall back.
    * any keys missing from ``primary`` but present in ``fallback`` are included.

    Example usage:

    >>> from pathlib import Path
    >>> from datetime import datetime
    >>> from typing import cast
    >>> _primary = cast(GitEnvVars, {
    ...     "GIT_AUTHOR_NAME": "Alice",
    ...     "GIT_AUTHOR_EMAIL": "alice@example.com",
    ...     "GIT_COMMITTER_DATE": None,
    ...     "GIT_EDITOR": None,
    ...     "GIT_TRACE": 2,
    ...     "GIT_SSH": Path("/usr/bin/ssh"),
    ... })
    >>> _fallback = cast(GitEnvVars, {
    ...     "GIT_AUTHOR_NAME": "Bob",
    ...     "GIT_AUTHOR_EMAIL": "bob@example.com",
    ...     "GIT_COMMITTER_DATE": datetime(2020, 1, 1),
    ...     "GIT_EDITOR": "vim",
    ...     "GIT_TRACE": Path("/tmp/trace.log"),
    ...     "GIT_SSH": None,
    ...     "GIT_CONFIG_GLOBAL": Path("/home/bob/.gitconfig"),
    ...     "GIT_REDACT_COOKIES": "sessionid"
    ... })
    >>> _merged = merge_git_envs(_primary, _fallback)
    >>> _merged["GIT_AUTHOR_NAME"]
    'Alice'
    >>> _merged["GIT_AUTHOR_EMAIL"]
    'alice@example.com'
    >>> _merged["GIT_COMMITTER_DATE"]
    datetime.datetime(2020, 1, 1, 0, 0)
    >>> _merged["GIT_EDITOR"]
    'vim'
    >>> _merged["GIT_TRACE"]
    2
    >>> _merged["GIT_SSH"]==Path('/usr/bin/ssh')
    True
    >>> _merged["GIT_CONFIG_GLOBAL"]==Path('/home/bob/.gitconfig')
    True

    Empty example:

    >>> empty = merge_git_envs({}, {})
    >>> isinstance(empty, dict)
    True

    Partial fallback behavior:

    >>> merge_git_envs({"GIT_EDITOR": None}, {"GIT_EDITOR": "nano"})["GIT_EDITOR"]
    'nano'
    >>> 'GIT_EDITOR' in merge_git_envs({"GIT_EDITOR": None}, {"GIT_EDITOR": None})
    False
    >>> merge_git_envs({"GIT_EDITOR": "code"}, {"GIT_EDITOR": "nano"})["GIT_EDITOR"]
    'code'

    >>> from vt.utils.commons.commons.core_py import Unset, UNSET
    >>> merge_git_envs({"GIT_EDITOR": UNSET}, {"GIT_EDITOR": "nano"})["GIT_EDITOR"] is UNSET
    True

    :param primary: The first priority ``GitEnvVars`` object.
    :param fallback: The second priority or fallback ``GitEnvVars`` object.
    :return: A new ``GitEnvVars`` object that contains all the properties from the ``primary`` ``GitEnvVars`` object and
        fallbacks on the corresponding property from the ``fallback`` ``GitEnvVars`` object if that corresponding property
        is explicitly ``None`` in the ``primary`` ``GitEnvVars`` object.
    """
    return merge_typed_dicts(primary, fallback, GitEnvVars)


# TODO: check for typing this function
def merge_typed_dicts(primary, fallback, the_typed_dict):
    merged = {}
    for k in the_typed_dict.__annotations__.keys():  # type: ignore
        val = primary.get(k)  # type: ignore # required as mypy thinks k is not str
        if val is None:
            val = fallback.get(k)  # type: ignore # required as mypy thinks k is not str
        if val is not None:
            merged[k] = val  # type: ignore # required as mypy thinks k is not str
    return merged
