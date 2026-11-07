#!/usr/bin/env python3
# coding=utf-8

"""
Utility helpers for ``git update-ref`` that do not belong on the command Protocol.
"""


def update_ref_stdin_input(*, stdin: bytes | None) -> bytes | None:
    """
    Bytes piped to ``git update-ref``. Always return ``stdin``, including ``None``.
    """
    return stdin


def stripped_update_ref_stdout(stdout: bytes) -> str:
    """
    Decode captured ``git update-ref`` bytes and strip surrounding whitespace.
    """
    return stdout.decode().strip()
