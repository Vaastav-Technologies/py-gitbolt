#!/usr/bin/env python3
# coding=utf-8

"""
Git command sessions utilities for long-running commands.

Create sessions for long-running commands and communicate with them using their stdin/stdout.

Much faster that subprocess creation for each input/output pair.
"""

import subprocess
from typing import Iterable, IO, cast

from vt.utils.errors.error_specs import ERR_INVALID_USAGE

from gitbolt.exceptions import GitExitingException


# region blob
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
    Read git contents using a long-running batched cat-file process. Best for programmatic use.

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
# endregion


# region tree
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


def cat_file_tree_data(
    cat_file_popen: subprocess.Popen[bytes], tree_hash: bytes, recursive: bool = False,
    _prefix: bytes = b"",
) -> Iterable[tuple[bytes, bytes, bytes]]:
    """
    Get tree data from the stdout of a long-running cat-file query for tree hash.

    Note: ``cat_file_popen`` must pipe its ``stdin`` and ``stdout`` and run in ``bytes`` mode.

    :param cat_file_popen: long-running ``git cat-file --batch`` process in bytes mode and pipes its stdin and stdout.
    :param tree_hash: tree hash to be read from cat-file.
    :param recursive: recursively query the full tree.
    :param _prefix: prefix, useful when doing recursive tree query (only for internal use).
    :return: iterable of (mode, sha, filename).
    :raises GitExitingException: when ``tree_hash`` is not the hash of a valid git tree.
    """
    _, typ, _, tree_content = cat_file_data(cat_file_popen, tree_hash)
    if typ != b"tree":
        raise GitExitingException(f"{tree_hash} is not a valid git tree.", exit_code=ERR_INVALID_USAGE) \
            from ValueError(tree_hash)
    if not recursive:
        for mode, sha, name in parse_cat_file_tree(tree_content):
            # leaf node (blob, symlink, submodule)
            yield mode, sha, name
    else:
        for mode, sha, name in parse_cat_file_tree(tree_content):
            full_name = _prefix + name

            if mode == b"40000":  # directory (tree)
                # recurse into subtree
                yield from cat_file_tree_data(
                    cat_file_popen,
                    sha,
                    recursive=True,
                    _prefix=full_name + b"/",
                )
            else:
                # leaf node (blob, symlink, submodule)
                yield mode, sha, full_name


def cat_file_tree_content(cat_file_popen: subprocess.Popen[bytes], tree_hash: bytes, recursive: bool = False,
                          format_: bytes = b"%(objmode)06o %(objtype)s %(objhash)s\x09%(objpath)s") -> Iterable[bytes]:
    """
    Get tree data from the stdout of a long-running cat-file query for tree hash in the format specified.

    Note: ``cat_file_popen`` must pipe its ``stdin`` and ``stdout`` and run in ``bytes`` mode.

    Query format:

    - objmode: `100644`, `100755`, `120000`, `040000`, `160000`.
    - objtype: `blob`, `tree`, `commit`.
    - objhash: sha hash of the object.
    - objpath: full path of the object from repo root.

    Default format usage and explanation:

    - %(objmode)06o: 06-show six-chars left-padded with 0 (zeros), o - octal number.

    :param cat_file_popen: long-running ``git cat-file --batch`` process in bytes mode and pipes its stdin and stdout.
    :param tree_hash: tree hash to be read from cat-file.
    :param recursive: recursively query the full tree.
    :param format_: the format in which the queried tree data will be formatted. Follows bytes ``%`` operator
        interpolation. Defaults to the typical ``git ls-tree`` format.
    :return: iterable of tree data in the queried ``format_``.
    :raises GitExitingException: when ``tree_hash`` is not the hash of a valid git tree.
    """
    for mode, sha, filename in cat_file_tree_data(cat_file_popen, tree_hash, recursive):
        if mode == b"40000":
            # directory
            objtype = b"tree"
        elif mode == b"160000":
            # submodule
            objtype = b"commit"
        elif mode in (b"100644", b"100755", b"120000"):
            # symlnk, executable, regular files
            objtype = b"blob"
        else:
            raise GitExitingException(f"Invalid object mode: {mode}") from ValueError(mode)
        objmode = int(mode, 8)
        yield format_ % {b"objmode": objmode, b"objtype": objtype, b"objhash": sha, b"objpath": filename}
# endregion

# region commit
def cat_file_commit_content(cat_file_popen: subprocess.Popen[bytes], commit_hash: bytes) -> bytes:
    """
    Get commit data as produced on stdout of a ``git cat-file --batch`` process for the querying of a particular
    commit hash.

    Spawning new ``git show`` processes can be slower and resource consuming.

    Note: ``cat_file_popen`` must pipe its ``stdin`` and ``stdout`` and run in ``bytes`` mode.

    :param cat_file_popen: long-running ``git cat-file --batch`` process in bytes mode and pipes its stdin and stdout.
    :param commit_hash: commit hash to be read from cat-file.
    :return: contents of blob hash in bytes.
    """
    return cat_file_blob_content(cat_file_popen, commit_hash)


def cat_file_commit_data(cat_file_popen: subprocess.Popen[bytes], commit_hash: bytes):
    """
    Get commit programmatic data as produced on stdout of a ``git cat-file --batch`` process for the querying
    of a particular commit hash.

    Spawning new ``git show`` processes can be slower and resource consuming.

    Note: ``cat_file_popen`` must pipe its ``stdin`` and ``stdout`` and run in ``bytes`` mode.

    :param cat_file_popen: long-running ``git cat-file --batch`` process in bytes mode and pipes its stdin and stdout.
    :param commit_hash: commit hash to be read from cat-file.
    :return: contents of blob hash in bytes.
    """
    commit_cat_file_content = cat_file_commit_content(cat_file_popen, commit_hash)
    query_aggregate: dict[bytes, bool] = {  # python3 dicts maintain order and cat-file maintains this order in
        # its output
        b"tree": False,
        b"parent": True,
        b"author": False,
        b"committer": False,
        # b"gpgsig": False,
    }
    commit_parents: list[bytes] = []
    curr_bytes_ptr = 0
    query_dict: dict[bytes, bytes | list[bytes]] = {}
    lines = commit_cat_file_content.splitlines()
    i = 0
    kv_delim = b" "
    while i < len(lines):
        for key, aggregate in query_aggregate.items():
            found, value = query_line(key, lines[i], kv_delim)
            if found:
                if aggregate:
                    if key in query_dict:
                        query_dict[key].append(value)
                    else:
                        query_dict[key] = [value]
                else:
                    query_dict[key] = value
                curr_bytes_ptr += len(key)
                curr_bytes_ptr += len(kv_delim)
                curr_bytes_ptr += len(lines[i])
                i += 1
            else:
                continue
    tree_found, tree_val, curr_bytes_ptr = query_bytes_range(commit_cat_file_content, curr_bytes_ptr, b"tree", b"", b"\n", False)
    parent_found: bool = True   # trying a do-while
    while parent_found:
        parent_found, parent_val, curr_bytes_ptr = query_bytes_range(commit_cat_file_content, curr_bytes_ptr, b"tree", b"", b"\n", False)
        commit_parents.append(parent_val)
    author_found, author_val, curr_bytes_ptr = query_bytes_range(commit_cat_file_content, curr_bytes_ptr, b"author", b"", b"\n", False)
    committer_found, committer_val, curr_bytes_ptr = query_bytes_range(commit_cat_file_content, curr_bytes_ptr, b"committer", b"", b"\n", False)
    sig_found, sig_val, curr_bytes_ptr = query_bytes_range(commit_cat_file_content, curr_bytes_ptr, b"gpgsig",
                                               b"-----BEGIN PGP SIGNATURE-----", b"-----END PGP SIGNATURE-----")
    curr_bytes_ptr += 1 # include \n as commit message starts after that.
    commit_message = commit_cat_file_content[curr_bytes_ptr:]




def query_bytes_range(commit_cat_file_content: bytes, curr_bytes_ptr: int, key_to_query: bytes,
                      val_begin: bytes, val_end: bytes, keep_ends: bool = True) -> tuple[bool, bytes | None, int]:
    interest_bytes = commit_cat_file_content[curr_bytes_ptr:]
    if not interest_bytes.startswith(key_to_query):
        return False, None, curr_bytes_ptr
    val_start_index = interest_bytes.find(val_begin) # including val start
    val_end_index = interest_bytes.find(val_end)    # including val end
    if not keep_ends:
        val_start_index += len(val_begin)   # excluding val start
        val_end_index += len(val_end)       # excluding val end
    value = interest_bytes[val_start_index: val_end_index]




def query_line(key: bytes, line: bytes, kv_delim: bytes = b" ") -> tuple[bool, bytes]:
    """
    Query a line from stream for a particular key and return the found value till the line ends.

    :param key: key to query.
    :param line: line to search key into.
    :param kv_delim: delimiter between the key and the value.
    :returns: (found, found-value) or (not-found, line)
    """
    if line.startswith(key):
        _, value = line.split(kv_delim, 1)
        return True, value
    else:
        return False, line
# endregion


if __name__ == "__main__":
    import gitbolt
    import time

    git = gitbolt.get_git_command()
    # region GitSession approach
    start = time.perf_counter()
    with git.session(
        cat_file1=["cat-file", "--batch"],
        cat_file2=["cat-file", "--batch"],
    ) as ses:
        for mode_, sha_, name_ in cat_file_tree_data(ses.commands.cat_file1, b"HEAD^{tree}", True):
            print(mode_, sha_, name_)
        print("+" * 40)
        print(cat_file_blob_content(ses.commands.cat_file2, b"9854cb4d432a881f59d38582791cf2636e7819d9"))

        print("*"*40)
        for tree_line in cat_file_tree_content(ses.commands.cat_file1, b"HEAD^{tree}"):
            print(tree_line.decode())
    end = time.perf_counter()
    print(f"Session Elapsed time: {end - start:0.4f} seconds")
    # endregion

    print("="*40)
    # region Per-process call approach
    start = time.perf_counter()
    head_tree_out = git.subcmd_unchecked.run(["cat-file", "-p", "HEAD^{tree}"], text=False).stdout.splitlines()
    for head_tree in head_tree_out:
        print(head_tree)
    print("+" * 40)
    print(git.subcmd_unchecked.run(["cat-file", "-p", "9854cb4d432a881f59d38582791cf2636e7819d9"], text=False).stdout)
    end = time.perf_counter()
    print(f"Subcmd Elapsed time: {end - start:0.4f} seconds")
    # endregion
