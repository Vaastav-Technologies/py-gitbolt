#!/usr/bin/env python3
# coding=utf-8

"""
models and datatypes related to git and git subcommands.
"""
from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Sequence

from vt.utils.commons.commons.core_py import Unset


class GitOpts(TypedDict, total=False):
    """
    All the parameters are mirrors of the options of the ``git`` CLI command
    from `git documentation <https://git-scm.com/docs/git>`_.

    These options are applied before any git subcommand (like ``log``, ``commit``, etc.).

    For example, in ``git --no-pager log -1 master`` git command, ``--no-pager`` is the main command option.
    """

    C: Sequence[Path] | Unset | None
    """
    Mirror of ``-C <path>``.

    Run as if git was started in the specified path(s) instead of the current working directory.
    Can be specified multiple times.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt--Cltpathgt>`_.
    """

    c: dict[str, str | bool | None | Unset] | None | Unset
    """
    Mirror of ``-c <name>=<value>``.

    Sets a configuration variable for the duration of the git command.
    Equivalent to using ``git config`` temporarily.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt--cltnamegtltvaluegt>`_.
    """

    config_env: dict[str, str] | None | Unset
    """
    Mirror of ``--config-env=<name>=<env-var>``.

    Set configuration variables from environment variables, useful in environments where configuration is set externally.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---config-envltnamegtltenvvargt>`_.
    """

    exec_path: Path | None | Unset
    """
    Mirror of ``--exec-path[=<path>]``.

    Path to the directory where git-core executables are located.
    If not set, uses the default from the environment or compiled-in path.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---exec-pathltpathgt>`_.
    """

    paginate: bool | None | Unset
    """
    Mirror of ``--paginate``.

    Forces git to use a pager for output, even if stdout is not a terminal.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---paginate>`_.
    """

    no_pager: bool | None | Unset
    """
    Mirror of ``--no-pager``.

    Disables the use of a pager for output.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---no-pager>`_.
    """

    git_dir: Path | None | Unset
    """
    Mirror of ``--git-dir=<path>``.

    Sets the path to the git repository (i.e., the ``.git`` directory).

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---git-dirltpathgt>`_.
    """

    work_tree: Path | None | Unset
    """
    Mirror of ``--work-tree=<path>``.

    Sets the working tree root for the repository.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---work-treeltpathgt>`_.
    """

    namespace: str | None | Unset
    """
    Mirror of ``--namespace=<namespace>``.

    Sets the git namespace for refs, useful in server environments or special ref layouts.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---namespaceltpathgt>`_.
    """

    bare: bool | None | Unset
    """
    Mirror of ``--bare``.

    Treat the repository as a bare repository.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---bare>`_.
    """

    no_replace_objects: bool | None | Unset
    """
    Mirror of ``--no-replace-objects``.

    Disables use of replacement objects that might otherwise override objects in the repo.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---no-replace-objects>`_.
    """

    no_lazy_fetch: bool | None | Unset
    """
    Mirror of ``--no-lazy-fetch``.

    Prevents git from auto-fetching missing objects on demand.
    Introduced in newer git versions.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---no-lazy-fetch>`_.
    """

    no_optional_locks: bool | None | Unset
    """
    Mirror of ``--no-optional-locks``.

    Prevents git from taking optional locks (used for performance tuning).

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---no-optional-locks>`_.
    """

    no_advice: bool | None | Unset
    """
    Mirror of ``--no-advice``.

    Suppresses all advice messages that git might normally print.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---no-advice>`_.
    """

    literal_pathspecs: bool | None | Unset
    """
    Mirror of ``--literal-pathspecs``.

    Treat pathspecs literally (no wildcards, no globbing).

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---literal-pathspecs>`_.
    """

    glob_pathspecs: bool | None | Unset
    """
    Mirror of ``--glob-pathspecs``.

    Enable globbing in pathspecs.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---glob-pathspecs>`_.
    """

    noglob_pathspecs: bool | None | Unset
    """
    Mirror of ``--noglob-pathspecs``.

    Disable globbing for pathspecs.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---noglob-pathspecs>`_.
    """

    icase_pathspecs: bool | None | Unset
    """
    Mirror of ``--icase-pathspecs``.

    Makes pathspecs case-insensitive (useful on case-insensitive filesystems).

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---icase-pathspecs>`_.
    """

    list_cmds: Sequence[str] | None | Unset
    """
    Mirror of ``--list-cmds=<category>``.

    Used to list available commands grouped by category.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---list-cmdsltgroupgtltgroupgt82308203>`_.
    """

    attr_source: str | None | Unset
    """
    Mirror of ``--attr-source=<tree-ish>``.

    Specifies the source tree for attribute lookups.

    `Documented <https://git-scm.com/docs/git#Documentation/git.txt---attr-sourcelttree-ishgt>`_.
    """
