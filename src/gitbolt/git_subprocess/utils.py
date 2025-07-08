#!/usr/bin/env python3
# coding=utf-8

"""
Utility functions related to processors specific to git commands using subprocess.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from vt.utils.commons.commons.core_py import is_unset, not_none_not_unset, Unset


def git_main_cmd_repeating_flag_args(
    val: Sequence[Path] | Unset | None, cmd_flag: str
) -> list[str]:
    """
    Returns a flattened list of repeating flags and values.

    Used for flags like `-C` which may be repeated with multiple values.

    Args:
        val: A list of values to apply with the flag.
        cmd_flag: The flag to apply to each value.

    Returns:
        A flattened list like ['-C', 'repo1', '-C', 'repo2']

    Examples:
        >>> git_main_cmd_repeating_flag_args([Path("repo1"), Path("repo2")], "-C")
        ['-C', 'repo1', '-C', 'repo2']

        >>> git_main_cmd_repeating_flag_args([], "-C")
        []

        >>> from vt.utils.commons.commons.core_py import UNSET
        >>> git_main_cmd_repeating_flag_args([Path("repo1"), UNSET, Path("repo2")], "-C")
        ['-C', 'repo1', '-C', 'repo2']

        >>> git_main_cmd_repeating_flag_args(None, "-C")
        []

        >>> git_main_cmd_repeating_flag_args(UNSET, "-C")
        []
    """
    if not_none_not_unset(val):
        return [
            item
            for entry in val
            if not is_unset(entry)
            for item in [cmd_flag, str(entry)]
        ]
    return []


def git_main_cmd_dict_flag_args(
    val: dict[str, str | bool | None | Unset] | None | Unset, cmd_flag: str
) -> list[str]:
    """
    Converts a dictionary into flag pairs used by commands like `-c key=value`.

    - `True` or `None` => `-c key`
    - `False` => `-c key=`
    - `UNSET` keys are skipped

    Args:
        val: Dictionary of key-value pairs.
        cmd_flag: The flag to apply.

    Returns:
        A list of CLI arguments.

    Examples:
        >>> git_main_cmd_dict_flag_args({"foo.bar": "baz"}, "-c")
        ['-c', 'foo.bar=baz']

        >>> git_main_cmd_dict_flag_args({"foo.bar": ""}, "-c")
        ['-c', 'foo.bar=']

        >>> git_main_cmd_dict_flag_args({"foo.bar": True}, "-c")
        ['-c', 'foo.bar']

        >>> git_main_cmd_dict_flag_args({"foo.bar": False}, "-c")
        ['-c', 'foo.bar=']

        >>> git_main_cmd_dict_flag_args({"foo.bar": None}, "-c")
        ['-c', 'foo.bar']

        >>> from vt.utils.commons.commons.core_py import UNSET
        >>> git_main_cmd_dict_flag_args({"foo.bar": UNSET}, "-c")
        []

        >>> git_main_cmd_dict_flag_args({
        ...     "a.b": "x", "c.d": "", "e.f": True, "g.h": False, "i.j": None
        ... }, "-c")
        ['-c', 'a.b=x', '-c', 'c.d=', '-c', 'e.f', '-c', 'g.h=', '-c', 'i.j']

        >>> git_main_cmd_dict_flag_args(None, "-c")
        []

        >>> git_main_cmd_dict_flag_args(UNSET, "-c")
        []

        >>> git_main_cmd_dict_flag_args({}, "-c")
        []
    """
    if not_none_not_unset(val):
        args = []
        for k, v in val.items():
            if is_unset(v):
                continue
            if v is True or v is None:
                args += [cmd_flag, k]
            elif v is False:
                args += [cmd_flag, f"{k}="]
            else:
                args += [cmd_flag, f"{k}={v}"]
        return args
    return []


def git_main_cmd_simple_flag_args(val: bool | Unset | None, cmd_flag: str) -> list[str]:
    """
    Returns a single flag if the value is set and truthy.

    Args:
        val: A boolean-like value.
        cmd_flag: The flag to apply.

    Returns:
        A list with just the flag, or empty.

    Examples:
        >>> git_main_cmd_simple_flag_args(True, "--no-pager")
        ['--no-pager']

        >>> git_main_cmd_simple_flag_args(False, "--no-pager")
        []

        >>> git_main_cmd_simple_flag_args(None, "--no-pager")
        []

        >>> from vt.utils.commons.commons.core_py import UNSET
        >>> git_main_cmd_simple_flag_args(UNSET, "--no-pager")
        []
    """
    if not_none_not_unset(val):
        return [cmd_flag] if val else []
    else:
        return []


def git_main_cmd_pair_flag_args(val: Any, cmd_flag: str) -> list[str]:
    """
    Returns a flag and value pair, or nothing if not set.

    Args:
        val: The value to attach to the flag.
        cmd_flag: The flag name.

    Returns:
        A list like ['--exec-path', 'tmp'] or []

    Examples:
        >>> git_main_cmd_pair_flag_args("foo", "--namespace")
        ['--namespace', 'foo']

        >>> git_main_cmd_pair_flag_args(Path("repo"), "--namespace")
        ['--namespace', 'repo']

        >>> git_main_cmd_pair_flag_args(None, "--namespace")
        []

        >>> from vt.utils.commons.commons.core_py import UNSET
        >>> git_main_cmd_pair_flag_args(UNSET, "--namespace")
        []
    """
    return [cmd_flag, str(val)] if not_none_not_unset(val) else []
