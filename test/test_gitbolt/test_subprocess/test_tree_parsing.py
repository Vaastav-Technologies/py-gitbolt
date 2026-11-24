#!/usr/bin/env python3
# coding=utf-8

"""
Tests for reading trees in a ``git cat-file --batch`` session, in sha1 and sha256 repositories.
"""

from collections.abc import Iterator
from itertools import islice
from pathlib import Path
from typing import Literal

import pytest
from vt.utils.errors.error_specs import ERR_DATA_FORMAT_ERR

from gitbolt.exceptions import GitExitingException
from gitbolt.subprocess.base import GitSession
from gitbolt.subprocess.impl.simple import SimpleGitCommand
from gitbolt.subprocess.utils.session import cat_file_blob_content, cat_file_commit_data, cat_file_tree_content, \
    cat_file_tree_data, mktree_tree_data_make, parse_cat_file_tree

MAX_ENTRIES = 10
"""More entries than any tree here has, so that a parser that never ends fails its test rather than hang it."""


def run(git: SimpleGitCommand, *args: str, stdin: bytes = b"") -> bytes:
    """Run a git subcommand that gitbolt does not provide and get its stripped stdout."""
    return git.subcmd_unchecked().run(list(args), _input=stdin, text=False).stdout.strip()


def write(git: SimpleGitCommand, content: bytes, t: Literal["blob", "commit"] = "blob") -> bytes:
    """Write an object and get its id."""
    return git.writing_hash_object_subcmd().hash_object(stdin=content, t=t, w=True).encode()


def ls_tree(git: SimpleGitCommand, tree: bytes, *, r: bool = False) -> list[bytes]:
    """Get the lines of ``git ls-tree`` for a tree."""
    return git.ls_tree_subcmd().ls_tree(tree.decode(), r=r).encode().splitlines()


@pytest.fixture(params=["sha1", "sha256"])
def git(request: pytest.FixtureRequest, repo_root) -> SimpleGitCommand:
    """Git in an empty repository, once for each object format."""
    git = SimpleGitCommand(Path(repo_root))
    run(git, "init", "-q", f"--object-format={request.param}")
    return git


@pytest.fixture
def tree(git: SimpleGitCommand) -> bytes:
    """The id of a tree with every kind of entry: file, executable, symlink, submodule and a subtree."""
    blob = write(git, b"content")
    subtree = run(git, "mktree", stdin=b"100644 blob %s\tin sub\n" % blob)
    return run(git, "mktree", "--missing", stdin=b"".join([
        b"100644 blob %s\ta file\n" % blob,
        b"100755 blob %s\texec\n" % blob,
        b"120000 blob %s\tlink\n" % blob,
        b"160000 commit %s\tsubmodule\n" % (b"1" * len(blob)),
        b"040000 tree %s\tsubtree\n" % subtree,
    ]))


@pytest.fixture
def ses(git: SimpleGitCommand) -> Iterator[GitSession]:
    """A started session that reads objects and makes trees."""
    with git.session(cat_file=["cat-file", "--batch"], mktree=["mktree", "--batch", "-z", "--missing"]) as session:
        yield session


@pytest.mark.parametrize("digits, suffix", [
    pytest.param(None, b"", id="full id"),
    pytest.param(10, b"", id="abbreviated id"),
    pytest.param(None, b"^{tree}", id="peeled"),
])
def test_tree_content_is_as_ls_tree_gives_it(git: SimpleGitCommand, ses: GitSession, tree: bytes,
                                             digits: int | None, suffix: bytes) -> None:
    content = list(islice(cat_file_tree_content(ses.commands.cat_file, tree[:digits] + suffix), MAX_ENTRIES))

    assert content == ls_tree(git, tree)


def test_recursive_tree_data_is_as_ls_tree_gives_it(git: SimpleGitCommand, ses: GitSession, tree: bytes) -> None:
    content = list(islice(cat_file_tree_content(ses.commands.cat_file, tree, recursive=True), MAX_ENTRIES))

    assert content == ls_tree(git, tree, r=True)


def test_tree_content_makes_the_same_tree(ses: GitSession, tree: bytes) -> None:
    content = list(islice(cat_file_tree_content(ses.commands.cat_file, tree), MAX_ENTRIES))

    assert mktree_tree_data_make(ses.commands.mktree, content) == tree


def test_empty_tree_has_no_entries(git: SimpleGitCommand, ses: GitSession) -> None:
    assert list(cat_file_tree_data(ses.commands.cat_file, run(git, "mktree"))) == []


def test_session_is_in_step_after_reading_a_tree(git: SimpleGitCommand, ses: GitSession, tree: bytes) -> None:
    blob = write(git, b"other content")
    list(islice(cat_file_tree_data(ses.commands.cat_file, tree, recursive=True), MAX_ENTRIES))

    assert cat_file_blob_content(ses.commands.cat_file, blob, b"blob") == b"other content"


def test_blob_and_commit_are_read(git: SimpleGitCommand, ses: GitSession, tree: bytes) -> None:
    blob = write(git, b"content")
    who = b"A U Thor <author@example.com> 1700000000 +0530"
    root_content = b"tree %s\nauthor %s\ncommitter %s\n\nroot\n" % (tree, who, who)
    root = write(git, root_content, "commit")
    child_content = b"tree %s\nparent %s\nauthor %s\ncommitter %s\n\nchild\n" % (tree, root, who, who)
    child = write(git, child_content, "commit")

    assert cat_file_blob_content(ses.commands.cat_file, blob, b"blob") == b"content"
    commit = cat_file_commit_data(ses.commands.cat_file, child)
    assert (commit.commit_hash, commit.tree_hash, commit.parents) == (child, tree, [root])
    assert commit.message == b"child\n"


@pytest.mark.parametrize("id_size", [20, 32])
@pytest.mark.parametrize("malformed", [
    pytest.param(b"100644 f\0" + b"\x11" * 19, id="id cut short"),
    pytest.param(b"100644 f\0", id="no id"),
    pytest.param(b"100644 f", id="name not ended"),
    pytest.param(b"100644 \0" + b"\x11" * 32, id="empty name"),
    pytest.param(b"100644", id="no name"),
    pytest.param(b" f\0" + b"\x11" * 32, id="empty mode"),
    pytest.param(b"100648 f\0" + b"\x11" * 32, id="mode not octal"),
])
def test_malformed_tree_is_refused(malformed: bytes, id_size: int) -> None:
    with pytest.raises(GitExitingException) as raised:
        list(islice(parse_cat_file_tree(malformed, id_size), MAX_ENTRIES))
    assert raised.value.exit_code == ERR_DATA_FORMAT_ERR


def test_entries_before_the_malformed_one_are_given() -> None:
    entries = iter(parse_cat_file_tree(b"100644 f\0" + b"\x11" * 20 + b"junk"))

    assert next(entries) == (b"100644", b"11" * 20, b"f")
    with pytest.raises(GitExitingException):
        next(entries)


@pytest.mark.parametrize("id_size", [-1, 0, 19, 21, 40, 64])
def test_unknown_id_size_is_refused_at_the_call(id_size: int) -> None:
    with pytest.raises(ValueError, match=str(id_size)):
        parse_cat_file_tree(b"", id_size)


def test_id_size_is_of_sha1_by_default() -> None:
    assert list(parse_cat_file_tree(b"100644 f\0" + b"\x11" * 20)) == [(b"100644", b"11" * 20, b"f")]
