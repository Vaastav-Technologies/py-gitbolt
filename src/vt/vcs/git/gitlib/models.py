#!/usr/bin/env python3
# coding=utf-8

"""
models and datatypes related to git and git subcommands.
"""
from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Sequence, Literal

from vt.utils.commons.commons.core_py import Unset


# git main command options
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


# git add subcommand options
class GitAddOpts(TypedDict, total=False):
    """
    All the parameters mirror the options for the ``git add`` subcommand as described in the
    official `git add documentation <https://git-scm.com/docs/git-add>`_.

    These options allow fine-grained control over how files are staged in the Git index.

    All options except:

    * ``pathspec_from_file``: mimics ``--pathspec-from-file``.
    * ``pathspec_file_nul``: mimics ``--pathspec-file-nul``
    * ``pathspec``: mimics the [<pathspec>...] in documentation.
    * ``pathspec_stdin``: stdin emulator, required when ``--pathspec-from-file`` is ``-`` (- is stdin).
    """

    verbose: bool
    """
    Mirror of ``--verbose``.

    Show files as they are added.

    Useful for tracking which files are being staged when using wildcard patterns or when adding many files.
    """

    dry_run: bool
    """
    Mirror of ``--dry-run``.

    Show what would be done without actually performing the add.

    No actual changes are made to the index.
    """

    force: bool
    """
    Mirror of ``--force`` or ``-f``.

    Allow adding otherwise ignored files.

    This is useful when a file is matched by `.gitignore` but still needs to be explicitly added.
    """

    interactive: bool
    """
    Mirror of ``--interactive`` or ``-i``.

    Interactively choose hunks or files to stage.

    Launches an interactive UI that allows selection of changes to be added.
    """

    patch: bool
    """
    Mirror of ``--patch`` or ``-p``.

    Interactively choose hunks to stage in a patch-like UI.

    Useful when you want to commit only parts of a file.
    """

    edit: bool
    """
    Mirror of ``--edit`` or ``-e``.

    Open an editor to manually edit the diff being added.

    Not commonly used outside specialized workflows.
    """

    no_all: bool | None
    """
    Mirror of ``--no-all`` or ``--all``.

    Controls whether changes to tracked files not explicitly listed are added.

    If ``True``, equivalent to ``--no-all`` (do not stage deletions).
    If ``False``, equivalent to ``--all`` (stage deletions and modifications).
    If ``None``, neither flag is passed.
    """

    no_ignore_removal: bool | None
    """
    Mirror of ``--no-ignore-removal`` or ``--ignore-removal``.

    Controls whether ignored files that are removed should be staged as deletions.

    If ``True``, equivalent to ``--no-ignore-removal``.
    If ``False``, equivalent to ``--ignore-removal``.
    If ``None``, neither flag is passed.
    """

    sparse: bool
    """
    Mirror of ``--sparse``.

    Allow updating entries outside of the sparse-checkout cone.

    Used with sparse checkouts to update entries not in the current working cone.
    """

    intent_to_add: bool
    """
    Mirror of ``--intent-to-add``.

    Record an intent-to-add entry for a file that does not yet exist in the index.

    Useful in partial clone scenarios or when you want to mark a file for future content.
    """

    refresh: bool
    """
    Mirror of ``--refresh``.

    Refresh the index without actually adding files.

    This updates the index's stat information to match the working tree.
    """

    ignore_errors: bool
    """
    Mirror of ``--ignore-errors``.

    Continue adding files even if some files cannot be added.

    Use with caution, as it may silently skip files with problems.
    """

    ignore_missing: bool
    """
    Mirror of ``--ignore-missing``.

    Silently skip missing files instead of reporting an error.

    Useful for scripting workflows where some files may not be present.
    """

    renormalize: bool
    """
    Mirror of ``--renormalize``.

    Apply the current content filters (e.g., line endings) to staged files.

    Useful after changing `.gitattributes` to ensure files are normalized properly.
    """

    chmod: Literal["+x", "-x"] | None
    """
    Mirror of ``--chmod={+x,-x}``.

    Apply executable permission changes to added files.

    ``+x`` makes the file executable, ``-x`` removes the executable bit.
    """

