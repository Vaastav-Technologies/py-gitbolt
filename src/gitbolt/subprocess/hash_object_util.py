#!/usr/bin/env python3
# coding=utf-8

"""
Utility helpers for ``git hash-object`` that do not belong on the command Protocol.

These functions have no instance state. Keep command Protocols free of loops and
conditionals; call these from the subprocess implementation instead.
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

_T = TypeVar("_T")


def hash_object_stdin_input(
    *,
    stdin: bytes | None,
    stdin_paths: list[Path] | None,
) -> bytes | None:
    """
    Bytes piped to ``git hash-object`` for ``--stdin`` or ``--stdin-paths``.
    """
    if stdin_paths is not None:
        return b"\n".join(str(p).encode() for p in stdin_paths) + b"\n"
    return stdin


def stdin_temp_file_paths(stdin: bytes, *stdins: bytes, tmpdir: Path) -> list[Path]:
    """
    Write each stdin payload to a file under ``tmpdir`` and return those paths.

    >>> from pathlib import Path
    >>> import tempfile
    >>> with tempfile.TemporaryDirectory() as created:
    ...     paths = stdin_temp_file_paths(b"a", b"b", tmpdir=Path(created))
    ...     assert [p.read_bytes() for p in paths] == [b"a", b"b"]
    """
    file_paths: list[Path] = []
    for index, data in enumerate((stdin, *stdins)):
        path = tmpdir / f"stdin-{index}"
        path.write_bytes(data)
        file_paths.append(path)
    return file_paths


def hashes_from_hash_object_stdout(
    stdout: str,
    *,
    file_path: Path | None,
    file_paths: tuple[Path, ...],
    stdin: bytes | None,
    stdin_paths: list[Path] | None,
) -> str | list[str]:
    """
    Turn ``git hash-object`` stdout into a single hash or a list of hashes.
    """
    hashes = stdout.splitlines() if stdout else []
    if stdin_paths is not None or file_paths or (file_path is not None and stdin is not None):
        return hashes
    return hashes[0]


def stripped_stdout_text(stdout: bytes) -> str:
    """
    Decode captured ``git hash-object`` bytes and strip surrounding whitespace.
    """
    return stdout.decode().strip()


def as_hash_list(hashed: str | list[str]) -> list[str]:
    """
    Normalize a single hash or a list of hashes to ``list[str]``.
    """
    return hashed if isinstance(hashed, list) else [hashed]


def run_in_tmpdir(tmpdir: Path | None, action: Callable[[Path], _T]) -> _T:
    """
    Run ``action`` with ``tmpdir``, or with a created temporary directory when omitted.
    """
    if tmpdir is None:
        with tempfile.TemporaryDirectory() as created:
            return action(Path(created))
    return action(tmpdir)
