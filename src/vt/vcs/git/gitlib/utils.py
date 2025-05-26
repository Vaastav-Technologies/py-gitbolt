#!/usr/bin/env python3
# coding=utf-8

"""
Utility functions related to processors specific to git commands.
"""
from vt.vcs.git.gitlib import GitOpts


def merge_git_opts(primary: GitOpts, fallback: GitOpts) -> GitOpts:
    """
    Merge the ``primary`` and ``fallback`` ``GitOpts`` object and return a new ``GitOpts`` object.

    Construction of the new ``GitOpts`` object is done such that:

    * first prioritise picking up a property from the ``primary``.
    * if a property is ``None`` in the ``primary`` then that corresponding property is picked from the ``fallback``.

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
