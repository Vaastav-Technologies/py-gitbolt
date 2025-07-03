#!/usr/bin/env python3
# coding=utf-8

"""
models and datatypes related to git and git subcommands.
"""

from __future__ import annotations

from datetime import datetime
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


# region git env vars
class GitCommitEnvVars(TypedDict, total=False):
    """
    Env vars mirroring: https://git-scm.com/docs/git#_git_commits
    """

    GIT_AUTHOR_NAME: str | Unset
    GIT_AUTHOR_EMAIL: str | Unset
    GIT_AUTHOR_DATE: str | datetime | int | Unset
    GIT_COMMITTER_NAME: str | Unset
    GIT_COMMITTER_EMAIL: str | Unset
    GIT_COMMITTER_DATE: str | datetime | int | Unset


class GitSysEnvVars(TypedDict, total=False):
    """
    Env vars mirroring: https://git-scm.com/docs/git#_system
    """

    HOME: Path | Unset


class GitEditorEnvVars(TypedDict, total=False):
    """
    Env vars mirroring: https://git-scm.com/docs/git#_system
    """

    GIT_EDITOR: str | Unset
    GIT_PAGER: str | Unset


class GitSSHEnvVars(TypedDict, total=False):
    """
    Env vars mirroring: https://git-scm.com/docs/git#_system
    """

    GIT_SSH: Path | Unset
    GIT_SSH_COMMAND: str | Unset


class GitTraceEnvVars(TypedDict, total=False):
    """
    Env vars mirroring: https://git-scm.com/docs/git#_system
    """

    GIT_TRACE: Literal[1, 2] | bool | Path | Unset
    GIT_TRACE_SETUP: Literal[1, 2] | bool | Path | Unset
    GIT_TRACE_PERFORMANCE: Literal[1, 2] | bool | Path | Unset
    GIT_TRACE_PACKET: Literal[1, 2] | bool | Path | Unset


class GitConfigEnvVars(TypedDict, total=False):
    """
    Env vars mirroring: https://git-scm.com/docs/git#_system
    """

    GIT_CONFIG_NOSYSTEM: Literal[1] | bool | Unset
    GIT_CONFIG_GLOBAL: Path | Unset
    GIT_ADVICE: Literal[0] | bool | Unset


class GitRepoEnvVars(TypedDict, total=False):
    """
    Env vars mirroring: https://git-scm.com/docs/git#_the_git_repository
    """

    GIT_DIR: Path | Unset
    GIT_WORK_TREE: Path | Unset
    GIT_INDEX_FILE: Path | Unset
    GIT_OBJECT_DIRECTORY: Path | Unset
    GIT_ALTERNATE_OBJECT_DIRECTORIES: Path | Unset


class GitNetworkEnvVars(TypedDict, total=False):
    """
    Git network related env vars.
    """

    GIT_TERMINAL_PROMPT: Literal[0, 1] | bool | Unset
    GIT_HTTP_USER_AGENT: str | Unset
    GIT_HTTP_PROXY: str | Unset
    GIT_HTTPS_PROXY: str | Unset
    GIT_NO_REPLACE_OBJECTS: Literal[1] | bool | Unset


GIT_TRACE_TYPE = Literal[0] | bool | Literal[1, 2] | Path | Literal[3, 4, 5, 6, 7, 8, 9]
"""
Takes values as declared in https://git-scm.com/docs/git#Documentation/git.txt-codeGITTRACEcode
"""


class GitLogEnvVars(TypedDict, total=False):
    """
    Git environment variables related to git's internal debugging, logging, and performance tracing.

    These allow developers and advanced users to inspect Git's internal behavior.
    For details, see: https://git-scm.com/docs/git

    All variables support:
    - `False` or `0`: disabled
    - `True` or 1–9: write trace to stderr
    - `Path`: write trace to file
    """

    GIT_TRACE: GIT_TRACE_TYPE | Unset
    """
    General tracing facility.

    Traces command execution, arguments, and key internal operations.
    Docs: https://git-scm.com/docs/git#Documentation/git.txt-codeGITTRACEcode
    """

    GIT_TRACE_SETUP: GIT_TRACE_TYPE | Unset
    """
    Traces repository, environment, and config discovery setup.
    Docs: https://git-scm.com/docs/git#Documentation/git.txt-codeGITTRACESETUPcode
    """

    GIT_TRACE_PACKET: GIT_TRACE_TYPE | Unset
    """
    Traces Git protocol packet communication (push, fetch, etc.).
    Docs: https://git-scm.com/docs/git#Documentation/git.txt-codeGITTRACEPACKETcode
    """

    GIT_TRACE_PERFORMANCE: GIT_TRACE_TYPE | Unset
    """
    Logs performance data including timing metrics for Git operations.
    Docs: https://git-scm.com/docs/git#Documentation/git.txt-codeGITTRACEPERFORMANCEcode
    """

    GIT_TRACE_PACK_ACCESS: GIT_TRACE_TYPE | Unset
    """
    Traces accesses to objects inside packfiles.
    Docs: https://git-scm.com/docs/git#Documentation/git.txt-codeGITTRACEPACKACCESScode
    """

    GIT_TRACE_SHALLOW: GIT_TRACE_TYPE | Unset
    """
    Traces shallow clone logic and interaction with shallow files.
    Docs: https://git-scm.com/docs/git#Documentation/git.txt-codeGITTRACESHALLOWcode
    """

    GIT_TRACE_CURL: GIT_TRACE_TYPE | Unset
    """
    Traces all libcurl activity used for HTTP/HTTPS communication.
    Useful for diagnosing HTTPS issues.
    Docs: https://git-scm.com/docs/git#Documentation/git.txt-codeGITTRACECURLcode
    """

    GIT_REDACT_COOKIES: str | Unset
    """
    Comma-separated list of cookie names to redact in curl trace logs.

    Prevents sensitive information from appearing in trace logs.
    Docs: https://git-scm.com/docs/git#Documentation/git.txt-codeGITREDACTCOOKIEScode
    """


class GitEnvVars(
    GitCommitEnvVars,
    GitEditorEnvVars,
    GitSSHEnvVars,
    GitTraceEnvVars,
    GitConfigEnvVars,
    GitRepoEnvVars,
    GitNetworkEnvVars,
    GitSysEnvVars,
):
    """
    Environment variables that control Git's runtime behavior.

    These variables correspond to official Git environment variables
    described in the Git documentation:

    - General environment variables: https://git-scm.com/docs/git#_environment_variables
    - Git Trace variables: https://git-scm.com/book/en/v2/Git-Internals-Environment-Variables
    - Git configuration environment variables: https://git-scm.com/docs/git-config#Documentation/git-config.txt

    Each field corresponds to a known environment variable that influences
    Git's operation or configuration during execution.

    All variables are optional and can be set to control specific aspects
    of Git's behavior.
    """

    pass


# endregion


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

    chmod: Literal["+x", "-x"]
    """
    Mirror of ``--chmod={+x,-x}``.

    Apply executable permission changes to added files.

    ``+x`` makes the file executable, ``-x`` removes the executable bit.
    """


class GitLsTreeOpts(TypedDict, total=False):
    """
    All the parameters mirror the options for the ``git ls-tree`` subcommand as described in the
    official `git ls-tree documentation <https://git-scm.com/docs/git-ls-tree>`_.

    These options allow introspection into the contents of a tree object in Git, including filtering,
    formatting, and controlling recursion.

    The required positional argument ``tree_ish`` (e.g., a commit, branch, or tree hash) is excluded from this dict.
    """

    d: bool
    """
    Mirror of ``-d``.

    Show only the named tree entries themselves, not their children.

    Useful for showing just directory entries at the current level, rather than listing all contents recursively.
    """

    r: bool
    """
    Mirror of ``-r``.

    Recurse into sub-trees.

    Allows the command to descend recursively into directories to show nested files.
    """

    t: bool
    """
    Mirror of ``-t``.

    Show tree entries even when recursing.

    Without this, only blobs (files) are shown when ``-r`` is used. With ``-t``, directory entries are shown too.
    """

    long: bool
    """
    Mirror of ``-l``.

    Show object size and mode information (long listing format).

    Includes blob size and extended information similar to ``ls -l`` in Unix.
    """

    z: bool
    """
    Mirror of ``-z``.

    Output entries separated with NUL characters instead of newlines.

    Useful when paths may contain special characters or when scripting.
    """

    name_only: bool
    """
    Mirror of ``--name-only``.

    Show only the file names (without mode, type, object, or size).

    Useful for extracting just the file paths from the tree object.
    """

    name_status: bool
    """
    Mirror of ``--name-status``.

    Show the names and status of the objects in the tree (added, modified, deleted).

    Useful for understanding the changes represented by the tree entries.
    """

    object_only: bool
    """
    Mirror of ``--object-only``.

    Show only the object IDs (SHA1 hashes) of the tree entries.

    Excludes path names and other metadata from output.
    """

    full_name: bool
    """
    Mirror of ``--full-name``.

    Show full paths relative to the root of the tree.

    This overrides Git’s default behavior of printing paths relative to the current working directory.
    """

    full_tree: bool
    """
    Mirror of ``--full-tree``.

    Pretend as if the command is run from the root of the working tree.

    This affects path filtering and is often used in scripts for predictable output.
    """

    abbrev: int
    """
    Mirror of ``--abbrev=<n>``.

    Specify the number of digits for abbreviated object names (SHA1).

    Git typically shortens object hashes in output; this controls the length explicitly.
    """

    format_: str
    """
    Mirror of ``--format=<format>``.

    Customize the output format.

    This is useful for scripting or processing structured output.
    """

    path: list[str]
    """
    Mimics the optional ``[--] <path>...`` component of the command.

    Restrict the tree listing to specific paths or directories.

    Works similarly to pathspec in other Git commands.
    """
