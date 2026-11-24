#!/usr/bin/env python3
# coding=utf-8

"""
Tests for making trees in a ``git mktree --batch -z`` session.
"""

from pathlib import Path

import pytest

from gitbolt.subprocess.impl.simple import SimpleGitCommand
from gitbolt.subprocess.utils.session import mktree_tree_data_make, mktree_tree_make

TREES: list[list[bytes]] = [
    [b""],
    [b"", b"f"],
    [b"f", b""],
    [b"", b"", b"f"],
    [b"", b"f", b"", b"f g"],
    [b"f", b"f g", b"f"],
]
"""Trees to make in one session, in order. Each one is its space-separated file names, and ``b""`` is the empty tree."""


def run(git: SimpleGitCommand, *args: str, stdin: bytes = b"") -> bytes:
    """Run a git subcommand that gitbolt does not provide and get its stripped stdout."""
    return git.subcmd_unchecked().run(list(args), _input=stdin, text=False).stdout.strip()


@pytest.fixture(params=["sha1", "sha256"])
def git(request: pytest.FixtureRequest, repo_root) -> SimpleGitCommand:
    """Git in an empty repository, once for each object format."""
    git = SimpleGitCommand(Path(repo_root))
    run(git, "init", "-q", f"--object-format={request.param}")
    return git


def _entries(git: SimpleGitCommand, tree: bytes) -> list[bytes]:
    """Get the mktree entries of a tree given as in ``TREES``."""
    blob = git.writing_hash_object_subcmd().hash_object(stdin=b"content", w=True).encode()
    return [b"100644 blob %s\t%s" % (blob, name) for name in tree.split()]


def _hash_from_separate_process(git: SimpleGitCommand, entries: list[bytes]) -> bytes:
    """Make the tree of ``entries`` in a git process of its own."""
    return run(git, "mktree", "-z", stdin=b"".join(entry + b"\0" for entry in entries))


@pytest.mark.parametrize("trees", TREES, ids=repr)
def test_tree_make_gives_each_tree_its_own_hash(git: SimpleGitCommand, trees: list[bytes]) -> None:
    entries = [_entries(git, tree) for tree in trees]
    expected = [_hash_from_separate_process(git, tree_entries) for tree_entries in entries]

    with git.session(mktree=["mktree", "--batch", "-z"]) as ses:
        made = [mktree_tree_make(ses.commands.mktree, b"\0".join(tree_entries)) for tree_entries in entries]
        ses.commands.mktree.stdin.close()
        unread = ses.commands.mktree.stdout.read()

    assert made == expected
    assert unread == b""


@pytest.mark.parametrize("trees", TREES, ids=repr)
def test_tree_data_make_gives_each_tree_its_own_hash(git: SimpleGitCommand, trees: list[bytes]) -> None:
    entries = [_entries(git, tree) for tree in trees]
    expected = [_hash_from_separate_process(git, tree_entries) for tree_entries in entries]

    with git.session(mktree=["mktree", "--batch", "-z"]) as ses:
        made = [mktree_tree_data_make(ses.commands.mktree, tree_entries) for tree_entries in entries]
        ses.commands.mktree.stdin.close()
        unread = ses.commands.mktree.stdout.read()

    assert made == expected
    assert unread == b""
