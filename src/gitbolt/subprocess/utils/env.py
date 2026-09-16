#!/usr/bin/env python3
# coding=utf-8

"""
Environment helpers for git subprocess execution.
"""

import os


def subprocess_env_with_os(env: dict[str, str] | None) -> dict[str, str] | None:
    """
    Build the ``env`` argument for :func:`subprocess.run` / :class:`subprocess.Popen`.

    * ``None`` — inherit the process environment (subprocess default).
    * otherwise — start from ``os.environ`` and apply ``env`` on top (GitBolt / caller wins on conflicts).

    Examples:

    >>> assert subprocess_env_with_os(None) is None

    >>> _env = {"AUTH_NAME": "suhas"}
    >>> processed_envs = subprocess_env_with_os(_env)
    >>> assert os.environ | _env == processed_envs
    """
    if env is None:
        return None
    return os.environ | env
