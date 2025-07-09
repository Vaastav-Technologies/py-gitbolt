from typing import Literal, overload


def create_branch(branch_name: str,
                  start_point: str | None = None,
                  *,
                  force: bool | None = None,
                  track: bool | None = None,
                  recurse_submodules: bool | None = None) -> str:
    """
    Create a new Git branch.

    Equivalent to ``git branch <branch_name> [<start_point>]`` with additional options.

    :param branch_name:
        Name of the new branch to create.

    :param start_point:
        Optional starting point (commit, tag, branch, etc.). Defaults to HEAD.

    :param force:
        **Tri-state.**
        - If True, emits ``--force`` or ``-f`` to allow overwriting an existing branch.
        - If False, emits ``--no-force`` to explicitly avoid forced creation.
        - If None, the option is not passed.

    :param track:
        **Tri-state.**
        - If True, sets up the new branch to track a remote branch.
        - If False, emits ``--no-track`` to disable tracking explicitly.
        - If None, leaves tracking behavior to Git defaults.

    :param recurse_submodules:
        **Tri-state.**
        - If True, emits ``--recurse-submodules`` to apply the branch operation recursively into submodules.
        - If False, emits ``--no-recurse-submodules``.
        - If None, submodule behavior is not specified.

    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt---create
    """
    ...


def set_upstream(branch_name: str | None = None, *, set_upstream_to: str | Literal[False]) -> str:
    """
    Set the upstream branch for a local branch.

    Equivalent to ``git branch --set-upstream-to=<branch> [<branch_name>]``.

    :param branch_name:
        Local branch to configure. Defaults to the current branch if not specified.

    :param set_upstream_to:
        Target upstream branch.
        Use a remote-tracking branch name (e.g. origin/main).

        - If given a string, sets the upstream to that branch (emits ``--set-upstream-to=<branch>``).
        - If set to ``False``, emits ``--no-set-upstream``.

    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt---set-upstream-to
    """
    ...


def unset_upstream(branch_name: str | None = None, *, unset_upstream_: bool = True) -> str:
    """
    Unset the upstream branch for a local branch.

    Equivalent to ``git branch --unset-upstream [<branch_name>]``.

    :param branch_name:
        Local branch whose upstream configuration should be removed. Defaults to the current branch.

    :param unset_upstream_:
        **Bi-state.**
        - If True (default), emits ``--unset-upstream``.
        - If False, emits ``--no-unset-upstream``.

    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt---unset-upstream
    """
    ...


def rename_branch(new_branch: str, old_branch: str | None = None, *, force: bool | None = None) -> str:
    """
    Rename an existing branch.

    Equivalent to ``git branch -m|-M [<old_branch>] <new_branch>``.

    :param new_branch:
        The new name for the branch.

    :param old_branch:
        The current name of the branch to rename. If None, renames the current branch.

    :param force:
        **Tri-state.**
        - If True, performs forced rename using ``-M``.
        - If False, uses ``-m`` for safe rename.
        - If None, defers to Git’s default behavior.

    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt--m
    """
    ...


def copy_branch(new_branch: str, old_branch: str | None = None, *, force: bool | None = None) -> str:
    """
    Create a copy of an existing branch.

    Equivalent to ``git branch -c|-C [<old_branch>] <new_branch>``.

    :param new_branch:
        Name for the new (copied) branch.

    :param old_branch:
        Source branch to copy. If None, uses the current branch as the source.

    :param force:
        **Tri-state.**
        - If True, performs forced copy using ``-C``.
        - If False, uses ``-c`` for safe copy.
        - If None, leaves behavior to Git default.

    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt--c
    """
    ...


def delete_branch(branch_name: str, *branch_names: str, force: bool | None = None, remote: bool | None = None) -> str:
    """
    Delete one or more branches.

    Equivalent to ``git branch -d|-D [-r] <branch-name>...``

    :param branch_name:
        First branch to delete.

    :param branch_names:
        Additional branches to delete.

    :param force:
        **Tri-state.**
        - If True, forces delete using ``-D``.
        - If False, deletes safely using ``-d``.
        - If None, leaves deletion behavior to Git default.

    :param remote:
        **Tri-state.**
        - If True, deletes remote-tracking branches (``-r``).
        - If False, emits ``--no-remote`` (though Git has no exact flag, useful for internal logic).
        - If None, omits remote flag entirely.

    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt--d
    """
    ...


def edit_description(branch_name: str | None = None) -> str:
    """
    Edit a branch's description.

    Equivalent to ``git branch --edit-description [<branch-name>]``.

    :param branch_name:
        Branch whose description you want to edit. Defaults to current branch if omitted.

    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt---edit-description
    """
    ...


@overload
def list_branches(*patterns: str,
                  color: Literal["always", "never", "auto"] | bool = ...,
                  show_current: bool = ...,
                  verbose: Literal[1, 2] | bool = ...,
                  abbrev: int | Literal[False] = ...,
                  sort: str | Literal[False] = ...,
                  merged: str | None = ...,
                  no_merged: str | None = ...,
                  contains: str | None = ...,
                  no_contains: str | None = ...,
                  remotes: Literal[True] = ...,
                  all_: bool = ...,
                  points_at: str | Literal[False] = ...,
                  format_: str | Literal[False] = ...,
                  list_only: bool = ...,
                  ignore_case: bool = ...,
                  omit_empty: bool = ...) -> str: ...


@overload
def list_branches(*patterns: str,
                  color: Literal["always", "never", "auto"] | bool = ...,
                  show_current: bool = ...,
                  column: str | bool = ...,
                  abbrev: int | Literal[False] = ...,
                  sort: str | Literal[False] = ...,
                  merged: str | None = ...,
                  no_merged: str | None = ...,
                  contains: str | None = ...,
                  no_contains: str | None = ...,
                  remotes: Literal[True] = ...,
                  all_: bool = ...,
                  points_at: str | Literal[False] = ...,
                  format_: str | Literal[False] = ...,
                  list_only: bool = ...,
                  ignore_case: bool = ...,
                  omit_empty: bool = ...) -> str: ...


def list_branches(*patterns: str,
                  color: Literal["always", "never", "auto"] | bool | None = None,
                  show_current: bool | None = None,
                  verbose: Literal[1, 2] | bool | None = None,
                  column: str | bool | None = None,
                  abbrev: int | Literal[False] | None = None,
                  sort: str | Literal[False] | None = None,
                  merged: str | None = None,
                  no_merged: str | None = None,
                  contains: str | None = None,
                  no_contains: str | None = None,
                  points_at: str | Literal[False] | None = None,
                  format_: str | Literal[False] | None = None,
                  remotes: Literal[True] | None = None,
                  all_: bool | None = None,
                  list_only: bool | None = None,
                  ignore_case: bool | None = None,
                  omit_empty: bool | None = None) -> str:
    """
    List branches with advanced filtering, formatting, and display options.

    This is equivalent to the ``git branch`` command with various modifiers for sorting,
    verbosity, formatting, filtering by commit or pattern, and output customization.

    :param patterns: Shell-style glob patterns used to filter branch names.

    :param color: **Tri-state.**
        Controls coloring of the output.
        - If one of "always", "never", or "auto", passes ``--color=<value>``.
        - If True, emits ``--color``.
        - If False, emits ``--no-color``.
        - If None, does not pass any color option.

    :param show_current: If True, emits ``--show-current`` to print the current branch only.

    :param verbose: **Tri-state (with levels).**
        Controls the verbosity level.
        - 1: Emits ``-v`` for one-line verbose display.
        - 2: Emits ``-vv`` to show upstream info.
        - True: Emits ``--verbose``.
        - False: Emits ``--no-verbose``.
        - None: No verbosity flag passed.
        Note: Cannot be used with ``--column``.

    :param column: **Tri-state.**
        Controls multi-column layout.
        - If a string, uses ``--column=<layout>``.
        - If True, emits ``--column``.
        - If False, emits ``--no-column``.
        - If None, no column flag is passed.
        Note: Cannot be used with ``--verbose``.

    :param abbrev: Length of abbreviated commit hashes.
        - If an integer, emits ``--abbrev=<n>``.
        - If False, disables abbreviation using ``--no-abbrev``.
        - If None, abbreviation is not affected.

    :param sort: Sort branches using the given key.
        - If str, emits ``--sort=<key>``.
        - If False, disables sorting with ``--no-sort``.
        - If None, does not emit any sorting option.

    :param merged: Show branches merged into the specified commit.

    :param no_merged: Show branches not merged into the specified commit.

    :param contains: Show branches that contain the specified commit.

    :param no_contains: Show branches that do not contain the specified commit.

    :param points_at: **Tri-state.**
        - If a string, emits ``--points-at=<object>``.
        - If False, emits ``--no-points-at``.
        - If None, does not emit any points-at flag.

    :param format_: **Tri-state.**
        Customizes output formatting.
        - If str, emits ``--format=<fmt>``.
        - If False, emits ``--no-format``.
        - If None, uses default Git formatting.

    :param remotes: If True, shows only remote-tracking branches (``--remotes``).

    :param all_: If True, shows both local and remote branches (``--all``).

    :param list_only: If True, restricts the output to branch names only (``--list``).

    :param ignore_case: If True, pattern matching is case-insensitive (``--ignore-case``).

    :param omit_empty: If True, suppresses empty sections (``--omit-empty``).

    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#_listing_branches
    """
    ...
