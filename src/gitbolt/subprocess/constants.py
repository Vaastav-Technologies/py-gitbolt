#!/usr/bin/env python3
# coding=utf-8

"""
constants wrt of git commands using subprocess.
"""

from typing import Final

GIT_CMD: Final[str] = "git"
VERSION_CMD: Final[str] = "version"
LS_TREE_CMD: Final[str] = "ls-tree"
ADD_CMD: Final[str] = "add"
WORKTREE_CMD: Final[str] = "worktree"
WORKTREE_LIST_CMD: Final[str] = "list"
WORKTREE_ADD_CMD: Final[str] = "add"
WORKTREE_MOVE_CMD: Final[str] = "move"
WORKTREE_REMOVE_CMD: Final[str] = "remove"
WORKTREE_REPAIR_CMD: Final[str] = "repair"
WORKTREE_PRUNE_CMD: Final[str] = "prune"
WORKTREE_LOCK_CMD: Final[str] = "lock"
WORKTREE_UNLOCK_CMD: Final[str] = "unlock"
