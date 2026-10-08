#!/usr/bin/env python3
# coding=utf-8

"""
Utility helpers for ``git commit-tree`` that do not belong on the command Protocol.
"""

from pathlib import Path
from typing import Literal


def commit_tree_stdin_input(
    *,
    F: Path | list[Path] | Literal["-"] | None,
    stdin: bytes | None,
) -> bytes | None:
    """
    Bytes piped to ``git commit-tree``.

    Git reads the log message from stdin when neither ``-m`` nor ``-F`` is given,
    and when ``-F -`` is given. Always return ``stdin`` in those cases, including
    ``None``.
    """
    if F == "-" or F is None:
        return stdin
    return None


def stripped_commit_hash(stdout: bytes) -> str:
    """
    Decode captured ``git commit-tree`` bytes and strip surrounding whitespace.
    """
    return stdout.decode().strip()
