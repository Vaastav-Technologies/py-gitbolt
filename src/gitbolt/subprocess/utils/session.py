#!/usr/bin/env python3
# coding=utf-8

"""
Git command sessions utilities for long-running commands.

Create sessions for long-running commands and communicate with them using their stdin/stdout.

Much faster that subprocess creation for each input/output pair.
"""

import subprocess
from typing import Iterable

from vt.utils.commons.commons.core_py import read_exact


def cat_file_blob_content(
    cat_file_popen: subprocess.Popen[bytes], blob_hash: bytes
) -> bytes:
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

def parse_tree(data: bytes) -> Iterable[tuple[bytes, bytes, bytes]]:
    """
    Parse bytes tree data.

    Typically best for parsing tree data from the stdout of a long-running cat-file query for tree.

    :param data: tree data in bytes format.
    :returns: iterable of (mode, sha, filename/filepath).
    """
    i = 0
    n = len(data)
    while i < n:
        # mode
        j = data.find(b' ', i)
        mode = data[i:j]
        # filename
        k = data.find(b'\x00', j)
        name = data[j + 1:k]
        # sha (20 bytes binary)
        sha = data[k + 1:k + 21]

        yield mode, sha.hex().encode(), name

        i = k + 21

def cat_file_tree_content(
    cat_file_popen: subprocess.Popen[bytes], tree_hash: bytes, recursive: bool = False,
    prefix: bytes = b"",
) -> list[tuple[bytes, bytes, bytes]]:
    """
    Get tree data from the stdout of a long-running cat-file query for tree hash.

    :param cat_file_popen: long-running ``git cat-file --batch`` process in bytes mode.
    :param tree_hash: tree hash to be read from cat-file.
    :param recursive: recursively query the full tree.
    :param prefix: prefix, useful when doing recursive tree query.
    :return: list of (mode, sha, filename).
    """
    tree_content = cat_file_blob_content(cat_file_popen, tree_hash)
    output: list[tuple[bytes, bytes, bytes]] = []
    if not recursive:
        for mode, sha, name in parse_tree(tree_content):
            # leaf node (blob, symlink, submodule)
            output.append((mode, sha, name,))
    else:
        for mode, sha, name in parse_tree(tree_content):
            full_name = prefix + name

            if mode == b"40000":  # directory (tree)
                # recurse into subtree
                sub_tree = cat_file_tree_content(
                    cat_file_popen,
                    sha,
                    recursive=True,
                    prefix=full_name + b"/",
                )
                output.extend(sub_tree)
            else:
                # leaf node (blob, symlink, submodule)
                output.append((mode, sha, full_name,))

    return output
