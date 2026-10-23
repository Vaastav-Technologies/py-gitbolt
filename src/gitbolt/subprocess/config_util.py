#!/usr/bin/env python3
# coding=utf-8

"""
Utility helpers for ``git config`` that do not belong on the command Protocol.
"""


def config_stdout(stdout: str, *, z: bool = False) -> str:
    """
    Decode captured ``git config`` text.

    ``-z`` values end with NUL; do not strip those. Otherwise drop a trailing newline
    Git adds after the value, without stripping spaces inside the value.
    """
    if z:
        return stdout
    return stdout.rstrip("\n")
