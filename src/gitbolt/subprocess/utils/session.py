#!/usr/bin/env python3
# coding=utf-8

"""
Git command sessions utilities for long-running commands.

Create sessions for long-running commands and communicate with them using their stdin/stdout.

Much faster that subprocess creation for each input/output pair.
"""

import subprocess
from typing import Iterable, IO, cast


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
    _, _, _, blob_content = cat_file_data(cat_file_popen, blob_hash)
    return blob_content


def cat_file_data(cat_file_popen: subprocess.Popen[bytes], blob_hash: bytes) -> tuple[bytes, bytes, bytes, bytes]:
    """
    Read git contents using a long-running batched cat-file process.

    Spawning new ``git show`` processes can be slower and resource consuming.

    Note: ``cat_file_popen`` must pipe its ``stdin`` and ``stdout`` and run in ``bytes`` mode.

    :param cat_file_popen: long-running ``git cat-file --batch`` process in bytes mode and pipes its stdin and stdout.
    :param blob_hash: hash to be read from cat-file.
    :return: (hash, type, size, content) of the read stream.
    """
    write_obj = blob_hash + b"\n"
    cat_file_popen_stdin: IO[bytes] = cast(IO[bytes], cat_file_popen.stdin)  # stdin is assumed to be piped
    cat_file_popen_stdout: IO[bytes] = cast(IO[bytes], cat_file_popen.stdout)  # stdout is assumed to be piped
    cat_file_popen_stdin.write(write_obj)
    cat_file_popen_stdin.flush()
    header = cat_file_popen_stdout.readline()
    obj, typ, size, blob_content = cat_file_read(cat_file_popen_stdout, header)
    cat_file_popen_stdout.read(1)
    return obj, typ, size, blob_content


def cat_file_read(stream: IO[bytes], header: bytes) -> tuple[bytes, bytes, bytes, bytes]:
    """
    ``git cat-file`` produces contents by first giving a header that contains:

    - object hash.
    - type (commit, tree, blob, ..., etc.).
    - size - the actual content is next ``size`` bytes long.

    :param stream: stream to read ``git cat-file --batch`` bytes from.
    :param header: the header line of ``git cat-file --batch``.
    :returns: (hash, type, size, content) of the read stream.
    """
    obj, typ, size = header.split()
    blob_content: bytes = stream.read(int(size))
    return obj, typ, size, blob_content


def parse_cat_file_tree(git_cat_file_data: bytes) -> Iterable[tuple[bytes, bytes, bytes]]:
    """
    Parse bytes tree data.

    Typically best for parsing tree data from the stdout of a long-running cat-file query for tree.

    :param git_cat_file_data: tree data in bytes format as given by ``git cat-file --batch`` for a tree query.
    :returns: iterable of (mode, sha, filename/filepath).
    """
    i = 0
    n = len(git_cat_file_data)
    while i < n:
        # mode
        j = git_cat_file_data.find(b" ", i)
        mode = git_cat_file_data[i:j]
        # filename
        k = git_cat_file_data.find(b"\x00", j)
        name = git_cat_file_data[j + 1: k]
        # sha (20 bytes binary)
        sha = git_cat_file_data[k + 1: k + 21]

        yield mode, sha.hex().encode(), name
        i = k + 21


def cat_file_tree_content(
    cat_file_popen: subprocess.Popen[bytes], tree_hash: bytes, recursive: bool = False,
    prefix: bytes = b"",
) -> Iterable[tuple[bytes, bytes, bytes]]:
    """
    Get tree data from the stdout of a long-running cat-file query for tree hash.

    Note: ``cat_file_popen`` must pipe its ``stdin`` and ``stdout`` and run in ``bytes`` mode.

    :param cat_file_popen: long-running ``git cat-file --batch`` process in bytes mode and pipes its stdin and stdout.
    :param tree_hash: tree hash to be read from cat-file.
    :param recursive: recursively query the full tree.
    :param prefix: prefix, useful when doing recursive tree query.
    :return: iterable of (mode, sha, filename).
    """
    tree_content = cat_file_blob_content(cat_file_popen, tree_hash)
    if not recursive:
        for mode, sha, name in parse_cat_file_tree(tree_content):
            # leaf node (blob, symlink, submodule)
            yield mode, sha, name
    else:
        for mode, sha, name in parse_cat_file_tree(tree_content):
            full_name = prefix + name

            if mode == b"40000":  # directory (tree)
                # recurse into subtree
                yield from cat_file_tree_content(
                    cat_file_popen,
                    sha,
                    recursive=True,
                    prefix=full_name + b"/",
                )
            else:
                # leaf node (blob, symlink, submodule)
                yield mode, sha, full_name


if __name__ == "__main__":
    import gitbolt
    import time

    git = gitbolt.get_git_command()
    # with git.session(cat_file=["cat-file", "--batch"]) as ses1, git.session(cat_file=["catfile", "--batch"]) as ses2:
    #     for mode_, sha_, name_ in cat_file_tree_content(ses1.commands.cat_file, b"HEAD^{tree}"):
    #         print(mode_, sha_, name_)
    start = time.perf_counter()
    with git.session(
        cat_file1=["cat-file", "--batch"],
        cat_file2=["cat-file", "--batch"],
    ) as ses:
        for mode_, sha_, name_ in cat_file_tree_content(ses.commands.cat_file1, b"HEAD^{tree}", True):
            print(mode_, sha_, name_)
        print("+" * 40)
        print(cat_file_blob_content(ses.commands.cat_file2, b"9854cb4d432a881f59d38582791cf2636e7819d9"))
    end = time.perf_counter()
    print(f"Session Elapsed time: {end - start:0.4f} seconds")

    print("="*40)
    start = time.perf_counter()
    head_tree_out = git.subcmd_unchecked.run(["cat-file", "-p", "HEAD^{tree}"], text=False).stdout.splitlines()
    for head_tree in head_tree_out:
        print(head_tree)
    print("+" * 40)
    print(git.subcmd_unchecked.run(["cat-file", "-p", "9854cb4d432a881f59d38582791cf2636e7819d9"], text=False).stdout)
    end = time.perf_counter()
    print(f"Subcmd Elapsed time: {end - start:0.4f} seconds")

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
