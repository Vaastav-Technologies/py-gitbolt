#!/usr/bin/env python3
# coding=utf-8

"""
Git command sessions utilities for long-running commands.

Create sessions for long-running commands and communicate with them using their stdin/stdout.

Much faster that subprocess creation for each input/output pair.
"""

import subprocess
from typing import Iterable, IO, cast

from vt.utils.commons.commons.core_py import read_exact


def cat_file_blob_content(
    cat_file_popen: subprocess.Popen[bytes], blob_hash: bytes
) -> bytes:
    """
    Read git blob contents using a long-running batched cat-file process.

    Spawning new ``git show`` processes can be slower and resource consuming.

    Note: ``cat_file_popen`` must pipe its ``stdin`` and ``stdout`` and run in ``bytes`` mode.

    :param cat_file_popen: long-running ``git cat-file --batch`` process in bytes mode and pipes its stdin and stdout.
    :param blob_hash: hash to be read from cat-file.
    :return: contents of blob hash in bytes.
    """
    write_obj = blob_hash + b"\n"
    cat_file_popen_stdin: IO[bytes] = cast(IO[bytes], cat_file_popen.stdin) # stdin is assumed to be piped
    cat_file_popen_stdout: IO[bytes] = cast(IO[bytes], cat_file_popen.stdout) # stdout is assumed to be piped
    cat_file_popen_stdin.write(write_obj)
    cat_file_popen_stdin.flush()
    header = cat_file_popen_stdout.readline()
    obj, typ, size = header.split()
    blob_content: bytes = cat_file_popen_stdout.read(int(size))
    cat_file_popen_stdout.read(1)
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

    Note: ``cat_file_popen`` must pipe its ``stdin`` and ``stdout`` and run in ``bytes`` mode.

    :param cat_file_popen: long-running ``git cat-file --batch`` process in bytes mode and pipes its stdin and stdout.
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


if __name__ == "__main__":
    import gitbolt
    git = gitbolt.get_git_command()
    # with git.session(cat_file=["cat-file", "--batch"]) as ses1, git.session(cat_file=["catfile", "--batch"]) as ses2:
    #     for mode_, sha_, name_ in cat_file_tree_content(ses1.commands.cat_file, b"HEAD^{tree}"):
    #         print(mode_, sha_, name_)
    with git.session(cat_file1=["catfile", "--batch"], cat_file2=["cat-file", "--batch"], cat_file3=["cat-file", "--batch"],
                     mktree=lambda: git.subcmd_unchecked.popen(["mktree"])) as ses:
        for mode_, sha_, name_ in cat_file_tree_content(ses.commands.cat_file2, b"HEAD^{tree}"):
            print(mode_, sha_, name_)
        print("+"*40)
        print(cat_file_blob_content(ses.commands.cat_file3, b"9854cb4d432a881f59d38582791cf2636e7819d9"))
    # cf_p_2 = git.subcmd_unchecked.popen(["catfile", "--batch"])
    # cf_p_1 = git.subcmd_unchecked.popen(["cat-file", "--batch"])
    # for mode_, sha_, name_ in cat_file_tree_content(cf_p_1, b"HEAD^{tree}"):
    #         print(mode_, sha_, name_)
    # sess = gitbolt.GitSession(git, cf_p_2=lambda: git.subcmd_unchecked.popen(["catfile", "--batch"]),
    #                           cf_p_1=lambda: git.subcmd_unchecked.popen(["cat-file", "--batch"]),
    #                           mktree=lambda: git.subcmd_unchecked.popen(["mktree", "--batch"]))
    # with sess:
    #     for mode_, sha_, name_ in cat_file_tree_content(sess.commands.cf_p_1, b"HEAD^{tree}"):
    #             print(mode_, sha_, name_)
