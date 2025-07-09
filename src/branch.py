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

    :param branch_name: Name of the new branch to create.
    :param start_point: Optional starting point (commit, branch, etc.). Defaults to HEAD.
    :param force: If True, forces creation (-f/-F), allowing overwrite of existing branch.
    :param track: If True, sets up tracking of a remote branch.
    :param recurse_submodules: If True, recurse into submodules for the new branch.
    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt---create
    """
    ...

def set_upstream(branch_name: str | None = None, *, set_upstream_to: str | Literal[False]) -> str:
    """
    Set the upstream branch for a local branch.

    Equivalent to ``git branch --set-upstream-to=<branch> [<branch_name>]``.

    :param branch_name: Local branch to configure. Defaults to current branch if omitted.
    :param set_upstream_to: Remote branch to set as upstream. Use ``False`` to emit ``--no-set-upstream``.
    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt---set-upstream-to
    """
    ...

def unset_upstream(branch_name: str | None = None, *, unset_upstream_: bool = True) -> str:
    """
    Unset the upstream branch for a local branch.

    Equivalent to ``git branch --unset-upstream [<branch_name>]``.

    :param branch_name: Local branch to modify. Defaults to current branch.
    :param unset_upstream_: If False, emit ``--no-unset-upstream``.
    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt---unset-upstream
    """
    ...

def rename_branch(new_branch: str, old_branch: str | None = None, *, force: bool | None = None) -> str:
    """
    Rename an existing branch.

    Equivalent to ``git branch -m|-M [<old_branch>] <new_branch>``.

    :param new_branch: The new name for the branch.
    :param old_branch: The current branch name. Defaults to current branch if omitted.
    :param force: True to force rename (-M), False for safe rename (-m), or None for default behavior.
    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt--m
    """
    ...

def copy_branch(new_branch: str, old_branch: str | None = None, *, force: bool | None= None) -> str:
    """
    Create a copy of an existing branch.

    Equivalent to ``git branch -c|-C [<old_branch>] <new_branch>``.

    :param new_branch: Name for the new (copied) branch.
    :param old_branch: Source branch to copy. Defaults to current branch if omitted.
    :param force: True to force copy (-C), False for safe copy (-c), or None.
    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt--c
    """
    ...

def delete_branch(branch_name: str, *branch_names: str, force: bool | None = None, remote: bool | None = None) -> str:
    """
    Delete one or more branches.

    Equivalent to ``git branch -d|-D [-r] <branch-name>...``

    :param branch_name: First branch to delete.
    :param branch_names: Additional branches to delete.
    :param force: True to force delete (-D), False for safe delete (-d), or None.
    :param remote: If True, deletes remote-tracking branches.
    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#Documentation/git-branch.txt--d
    """
    ...

def edit_description(branch_name: str | None = None) -> str:
    """
    Edit a branch's description.

    Equivalent to ``git branch --edit-description [<branch-name>]``.

    :param branch_name: Branch to edit. Defaults to current branch.
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
                  remotes: Literal[True]  | None = None,
                  all_: bool | None = None,
                  list_only: bool | None = None,
                  ignore_case: bool | None = None,
                  omit_empty: bool | None = None) -> str:
    """
    List branches with filters, verbosity, and formatting options.

    Equivalent to ``git branch`` with extended support for listing and customization.

    :param patterns: Patterns to match branch names.
    :param color: Colorize output ('always', 'never', 'auto', or bool).
    :param show_current: Highlight the current branch.
    :param verbose: Verbosity level. 1 = -v, 2 = -vv, True = --verbose, False = --no-verbose.
    :param column: Output column layout. True/False or layout string.
    :param abbrev: Length of SHA abbreviations. Use False to disable.
    :param sort: Sort key for ordering branches. Use False to disable.
    :param merged: List branches merged into this commit.
    :param no_merged: List branches not merged into this commit.
    :param contains: Show branches containing the commit.
    :param no_contains: Show branches not containing the commit.
    :param points_at: Show branches pointing at an object.
    :param format_: Custom formatting. False disables format.
    :param remotes: Show remote-tracking branches.
    :param all_: Show both local and remote branches.
    :param list_only: Suppress headings/details.
    :param ignore_case: Ignore case in name patterns.
    :param omit_empty: Suppress output when no match.
    :return: Output of ``git branch``.

    See also: https://git-scm.com/docs/git-branch#_listing_branches
    """
    ...
