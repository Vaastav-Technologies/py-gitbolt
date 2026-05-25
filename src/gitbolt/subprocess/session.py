#!/usr/bin/env python3
# coding=utf-8

"""
Git command sessions utilities for long-running commands.

Create sessions for long-running commands and communicate with them using their stdin/stdout.

Much faster that subprocess creation for each input/output pair.
"""
import subprocess

from vt.utils.commons.commons.core_py import read_exact


def cat_file_blob_content(cat_file_popen: subprocess.Popen[bytes], blob_hash: bytes) -> bytes:
    """
    Read git blob contents using a long-running batched cat-file process.

    Spawning new ``git show`` processes can be slower and resource consuming.

    :param cat_file_popen: long-running ``git cat-file --batch`` process in bytes mode.
    :param blob_hash: hash to be read from cat-file.
    :return: contents of blob hash in bytes.
    """
    write_obj = blob_hash + b"\n"
    cat_file_popen.stdin.write(write_obj)
    cat_file_popen.stdin.flush()
    header = cat_file_popen.stdout.readline()
    obj, typ, size = header.split()
    blob_content: bytes = read_exact(cat_file_popen.stdout, int(size))
    cat_file_popen.stdout.readline()
    return blob_content
