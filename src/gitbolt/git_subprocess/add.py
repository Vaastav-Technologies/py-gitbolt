#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces for ``git add`` subcommand with default implementation for subprocess calls.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Protocol, Unpack, override, Literal

from gitbolt.git_subprocess.constants import ADD_CMD
from gitbolt.models import GitAddOpts


class AddCLIArgsBuilder(Protocol):
    """
    Interface to facilitate building of cli arguments for ``git add`` subcommand.
    """

    @abstractmethod
    def build(
        self,
        pathspec: str | None = None,
        *pathspecs: str,
        pathspec_from_file: Path | Literal["-"] | None = None,
        pathspec_file_nul: bool = False,
        **add_opts: Unpack[GitAddOpts],
    ) -> list[str]:
        """
        Build the complete list of subcommand arguments to be passed to ``git add``.

        This method assembles the subcommand portion of the git command invocation, such as
        in ``git --no-pager add --ignore-missing add-file.py``, where ``--ignore-missing add-file.py`` is the
        subcommand argument list.

        It delegates the formation of each argument to protected helper methods to allow
        easier overriding and testing of individual components.

        Includes support for:

        - Boolean flags (e.g., --verbose, --dry-run, etc)
        - Optional key-value arguments (e.g., --chmod=+x)
        - Optional pathspecs
        - Optional pathspec-from-file

        See: `git add documentation <https://git-scm.com/docs/git-add>`_.

        :param pathspec: A direct file or directory to stage. Cannot be used with ``pathspec_from_file``.
        :type pathspec: str | None
        :param pathspecs: Additional pathspecs to stage.
        :type pathspecs: str
        :param pathspec_from_file: A file to read pathspecs from. Use ``'-'`` to read from stdin.
        :type pathspec_from_file: Path | Literal['-'] | None
        :param pathspec_stdin: Required if ``pathspec_from_file == '-'``. Denotes stdin content.
        :type pathspec_stdin: str | None
        :param pathspec_file_nul: Whether input lines in ``pathspec_from_file`` are NUL-separated.
        :type pathspec_file_nul: bool
        :param add_opts: Options accepted by the ``git add`` subcommand.
        :type add_opts: Unpack[GitAddOpts]
        :return: Complete list of subcommand arguments.
        :raises GitExitingException: if undesired argument type or argument combination is supplied.
        """
        ...


class IndividuallyOverridableACAB(AddCLIArgsBuilder):
    """
    Individually Overridable Add CLI Args Builder.

    Build CLI args to run ``git add`` subcommand in a subprocess. This class is independent in its working and
    provides interface to individually override each arg former for fine-grained control.
    """

    @override
    def build(
        self,
        pathspec: str | None = None,
        *pathspecs: str,
        pathspec_from_file: Path | Literal["-"] | None = None,
        pathspec_file_nul: bool = False,
        **add_opts: Unpack[GitAddOpts],
    ) -> list[str]:
        """
        Build the full list of arguments to be passed to ``git add``.

        This includes flags, optional arguments, pathspec identifier, and optional pathspecs etc.

        >>> builder = IndividuallyOverridableACAB()

        Example usage and expected results:

        >>> builder = IndividuallyOverridableACAB()

        Basic usage with one pathspec:

        >>> builder.build("file.txt")
        ['add', 'file.txt']

        Using boolean flags:

        >>> builder.build("file.txt", verbose=True, dry_run=True)
        ['add', '--verbose', '--dry-run', 'file.txt']

        Using tri-state options:

        >>> builder.build("file.txt", no_all=True, no_ignore_removal=False)
        ['add', '--no-all', '--ignore-removal', 'file.txt']

        Using optional value flag:

        >>> builder.build("file.txt", chmod='+x')
        ['add', '--chmod=+x', 'file.txt']

        Using multiple pathspecs:

        >>> builder.build("src", "tests", verbose=True)
        ['add', '--verbose', 'src', 'tests']

        With pathspec_from_file (as a file path):

        >>> builder.build(pathspec_from_file=Path("specs.txt"))
        ['add', '--pathspec-from-file=specs.txt']

        With pathspec_from_file from stdin:

        >>> builder.build(pathspec_from_file='-')
        ['add', '--pathspec-from-file=-']

        With pathspec_file_nul flag:

        >>> builder.build(pathspec_file_nul=True)
        ['add', '--pathspec-file-nul']

        All applicable flags and values:

        >>> builder.build("src/file.py", verbose=True, dry_run=True, force=True, interactive=True,
        ...               patch=True, edit=True, no_all=False, no_ignore_removal=True, sparse=True,
        ...               intent_to_add=True, refresh=True, ignore_errors=True, ignore_missing=True,
        ...               renormalize=True, chmod='-x')
        ['add', '--verbose', '--dry-run', '--force', '--interactive', '--patch', '--edit', '--all', '--no-ignore-removal', '--sparse', '--intent-to-add', '--refresh', '--ignore-errors', '--ignore-missing', '--renormalize', '--chmod=-x', 'src/file.py']
        """
        sub_cmd_args = [ADD_CMD]

        # region GitAddOpts members
        # region bool flags
        sub_cmd_args.extend(self.verbose_arg(add_opts.get("verbose")))
        sub_cmd_args.extend(self.dry_run_arg(add_opts.get("dry_run")))
        sub_cmd_args.extend(self.force_arg(add_opts.get("force")))
        sub_cmd_args.extend(self.interactive_arg(add_opts.get("interactive")))
        sub_cmd_args.extend(self.patch_arg(add_opts.get("patch")))
        sub_cmd_args.extend(self.edit_arg(add_opts.get("edit")))

        # region tri-state flags
        sub_cmd_args.extend(self.no_all(add_opts.get("no_all")))
        sub_cmd_args.extend(
            self.no_ignore_removal_arg(add_opts.get("no_ignore_removal"))
        )
        # endregion

        sub_cmd_args.extend(self.sparse_arg(add_opts.get("sparse")))
        sub_cmd_args.extend(self.intent_to_add_arg(add_opts.get("intent_to_add")))

        sub_cmd_args.extend(self.refresh_arg(add_opts.get("refresh")))
        sub_cmd_args.extend(self.ignore_errors_arg(add_opts.get("ignore_errors")))
        sub_cmd_args.extend(self.ignore_missing_arg(add_opts.get("ignore_missing")))
        sub_cmd_args.extend(self.renormalize_arg(add_opts.get("renormalize")))
        # endregion

        sub_cmd_args.extend(self.chmod_arg(add_opts.get("chmod")))
        # endregion

        # region non GitOpts members
        sub_cmd_args.extend(self.pathspec_file_nul_arg(pathspec_file_nul))
        sub_cmd_args.extend(self.pathspec_from_file_arg(pathspec_from_file))
        sub_cmd_args.extend(self.pathspec_arg(pathspec, *pathspecs))
        # endregion

        return sub_cmd_args

    def verbose_arg(self, verbose: bool | None) -> list[str]:
        """
        Return ``--verbose`` if `verbose` is True.

        :param verbose: Whether to include the ``--verbose`` option.
        :return: List containing ``--verbose`` if applicable.

        >>> IndividuallyOverridableACAB().verbose_arg(True)
        ['--verbose']
        >>> IndividuallyOverridableACAB().verbose_arg(False)
        []
        >>> IndividuallyOverridableACAB().verbose_arg(None)
        []
        """
        return ["--verbose"] if verbose else []

    def dry_run_arg(self, dry_run: bool | None) -> list[str]:
        """
        Return ``--dry-run`` if `dry_run` is True.

        :param dry_run: Whether to include the ``--dry-run`` option.
        :return: List containing ``--dry-run`` if applicable.

        >>> IndividuallyOverridableACAB().dry_run_arg(True)
        ['--dry-run']
        >>> IndividuallyOverridableACAB().dry_run_arg(False)
        []
        >>> IndividuallyOverridableACAB().dry_run_arg(None)
        []
        """
        return ["--dry-run"] if dry_run else []

    def force_arg(self, force: bool | None) -> list[str]:
        """
        Return ``--force`` if `force` is True.

        :param force: Whether to include the ``--force`` option.
        :return: List containing ``--force`` if applicable.

        >>> IndividuallyOverridableACAB().force_arg(True)
        ['--force']
        >>> IndividuallyOverridableACAB().force_arg(False)
        []
        >>> IndividuallyOverridableACAB().force_arg(None)
        []
        """
        return ["--force"] if force else []

    def interactive_arg(self, interactive: bool | None) -> list[str]:
        """
        Return ``--interactive`` if `interactive` is True.

        :param interactive: Whether to include the ``--interactive`` option.
        :return: List containing ``--interactive`` if applicable.

        >>> IndividuallyOverridableACAB().interactive_arg(True)
        ['--interactive']
        >>> IndividuallyOverridableACAB().interactive_arg(False)
        []
        >>> IndividuallyOverridableACAB().interactive_arg(None)
        []
        """
        return ["--interactive"] if interactive else []

    def patch_arg(self, patch: bool | None) -> list[str]:
        """
        Return ``--patch`` if `patch` is True.

        :param patch: Whether to include the ``--patch`` option.
        :return: List containing ``--patch`` if applicable.

        >>> IndividuallyOverridableACAB().patch_arg(True)
        ['--patch']
        >>> IndividuallyOverridableACAB().patch_arg(False)
        []
        >>> IndividuallyOverridableACAB().patch_arg(None)
        []
        """
        return ["--patch"] if patch else []

    def edit_arg(self, edit: bool | None) -> list[str]:
        """
        Return ``--edit`` if applicable.

        >>> IndividuallyOverridableACAB().edit_arg(True)
        ['--edit']
        >>> IndividuallyOverridableACAB().edit_arg(False)
        []
        >>> IndividuallyOverridableACAB().edit_arg(None)
        []
        """
        return ["--edit"] if edit else []

    def no_all(self, no_all: bool | None) -> list[str]:
        """
        Return ``--no-all`` or ``--all`` if applicable.

        >>> IndividuallyOverridableACAB().no_all(True)
        ['--no-all']
        >>> IndividuallyOverridableACAB().no_all(False)
        ['--all']
        >>> IndividuallyOverridableACAB().no_all(None)
        []
        """
        if no_all is None:
            return []
        return ["--no-all"] if no_all else ["--all"]

    def no_ignore_removal_arg(self, no_ignore_removal: bool | None) -> list[str]:
        """
        Return ``--no-ignore-removal`` or ``--ignore-removal`` if applicable.

        >>> IndividuallyOverridableACAB().no_ignore_removal_arg(True)
        ['--no-ignore-removal']
        >>> IndividuallyOverridableACAB().no_ignore_removal_arg(False)
        ['--ignore-removal']
        >>> IndividuallyOverridableACAB().no_ignore_removal_arg(None)
        []
        """
        if no_ignore_removal is None:
            return []
        return ["--no-ignore-removal"] if no_ignore_removal else ["--ignore-removal"]

    def sparse_arg(self, sparse: bool | None) -> list[str]:
        """
        Return ``--sparse`` if applicable.

        >>> IndividuallyOverridableACAB().sparse_arg(True)
        ['--sparse']
        >>> IndividuallyOverridableACAB().sparse_arg(False)
        []
        >>> IndividuallyOverridableACAB().sparse_arg(None)
        []
        """
        return ["--sparse"] if sparse else []

    def intent_to_add_arg(self, intent_to_add: bool | None) -> list[str]:
        """
        Return ``--intent-to-add`` if applicable.

        >>> IndividuallyOverridableACAB().intent_to_add_arg(True)
        ['--intent-to-add']
        >>> IndividuallyOverridableACAB().intent_to_add_arg(False)
        []
        >>> IndividuallyOverridableACAB().intent_to_add_arg(None)
        []
        """
        return ["--intent-to-add"] if intent_to_add else []

    def refresh_arg(self, refresh: bool | None) -> list[str]:
        """
        Returns ``--refresh`` if applicable.

        >>> IndividuallyOverridableACAB().refresh_arg(None)
        []
        >>> IndividuallyOverridableACAB().refresh_arg(True)
        ['--refresh']
        >>> IndividuallyOverridableACAB().refresh_arg(False)
        []
        """
        return ["--refresh"] if refresh else []

    def ignore_errors_arg(self, ignore_errors: bool | None) -> list[str]:
        """
        Returns ``--ignore-errors`` if applicable.

        >>> IndividuallyOverridableACAB().ignore_errors_arg(True)
        ['--ignore-errors']
        >>> IndividuallyOverridableACAB().ignore_errors_arg(None)
        []
        >>> IndividuallyOverridableACAB().ignore_errors_arg(False)
        []
        """
        return ["--ignore-errors"] if ignore_errors else []

    def ignore_missing_arg(self, ignore_missing: bool | None) -> list[str]:
        """
        Returns ``--ignore-missing`` if applicable.

        >>> IndividuallyOverridableACAB().ignore_missing_arg(True)
        ['--ignore-missing']
        >>> IndividuallyOverridableACAB().ignore_missing_arg(None)
        []
        >>> IndividuallyOverridableACAB().ignore_missing_arg(False)
        []
        """
        return ["--ignore-missing"] if ignore_missing else []

    def renormalize_arg(self, renormalize: bool | None) -> list[str]:
        """
        Returns ``--renormalize`` if applicable.

        >>> IndividuallyOverridableACAB().renormalize_arg(True)
        ['--renormalize']
        >>> IndividuallyOverridableACAB().renormalize_arg(None)
        []
        >>> IndividuallyOverridableACAB().renormalize_arg(False)
        []
        """
        return ["--renormalize"] if renormalize else []

    def chmod_arg(self, chmod: Literal["+x", "-x"] | None):
        """
        Return ``--chmod=+x`` or ``--chmod=-x`` if applicable.

        >>> IndividuallyOverridableACAB().chmod_arg('+x')
        ['--chmod=+x']
        >>> IndividuallyOverridableACAB().chmod_arg('-x')
        ['--chmod=-x']
        >>> IndividuallyOverridableACAB().chmod_arg(None)
        []
        """
        if chmod is None:
            return []
        return [f"--chmod={chmod}"]

    def tree_ish_arg(self, tree_ish: str) -> list[str]:
        """
        Return the required tree-ish identifier as a single-element list.

        This value is typically a commit SHA, branch name, tag, or other valid tree reference
        and is appended at the end of the formed git subcommand options, just before path(s).

        >>> IndividuallyOverridableACAB().tree_ish_arg("HEAD")
        ['HEAD']
        >>> IndividuallyOverridableACAB().tree_ish_arg("origin/main")
        ['origin/main']
        >>> IndividuallyOverridableACAB().tree_ish_arg("a1b2c3d")
        ['a1b2c3d']
        >>> IndividuallyOverridableACAB().tree_ish_arg("")
        ['']
        """
        return [tree_ish]

    def path_args(self, path: list[str] | None) -> list[str]:
        """
        Return the list of paths (if any) passed to ``git add``.

        If `path` is None or an empty list, this returns an empty list.

        >>> IndividuallyOverridableACAB().path_args(["src", "README.md"])
        ['src', 'README.md']
        >>> IndividuallyOverridableACAB().path_args([])
        []
        >>> IndividuallyOverridableACAB().path_args(None)
        []
        """
        return path if path else []

    def pathspec_file_nul_arg(self, pathspec_file_nul: bool | None) -> list[str]:
        """
        Returns ``--pathspec-file-nul`` if applicable.

        >>> IndividuallyOverridableACAB().pathspec_file_nul_arg(True)
        ['--pathspec-file-nul']
        >>> IndividuallyOverridableACAB().pathspec_file_nul_arg(None)
        []
        >>> IndividuallyOverridableACAB().pathspec_file_nul_arg(False)
        []
        """
        return ["--pathspec-file-nul"] if pathspec_file_nul else []

    def pathspec_from_file_arg(
        self, pathspec_from_file: Path | Literal["-"] | None
    ) -> list[str]:
        """
        Returns --pathspec-from-file=<pathspec-file> if applicable.

        >>> IndividuallyOverridableACAB().pathspec_from_file_arg(None)
        []
        >>> IndividuallyOverridableACAB().pathspec_from_file_arg(Path('a-file.txt'))
        ['--pathspec-from-file=a-file.txt']
        >>> IndividuallyOverridableACAB().pathspec_from_file_arg('-')
        ['--pathspec-from-file=-']
        """
        if pathspec_from_file is None:
            return []
        return [f"--pathspec-from-file={str(pathspec_from_file)}"]

    def pathspec_arg(self, *pathspecs: str | None) -> list[str]:
        """
        Examples::

        >>> IndividuallyOverridableACAB().pathspec_arg()
        []

        >>> IndividuallyOverridableACAB().pathspec_arg('ano', 'the-txt')
        ['ano', 'the-txt']

        >>> IndividuallyOverridableACAB().pathspec_arg('add.py')
        ['add.py']

        >>> IndividuallyOverridableACAB().pathspec_arg('.')
        ['.']

        >>> IndividuallyOverridableACAB().pathspec_arg('ad*', 'dir*/*8add')
        ['ad*', 'dir*/*8add']

        >>> IndividuallyOverridableACAB().pathspec_arg('ad*', 'dir*/*8add', 'dir/subdir/*')
        ['ad*', 'dir*/*8add', 'dir/subdir/*']

        :return: pathspecs in a list if supplied.
        """
        return [pathspec for pathspec in pathspecs if pathspec is not None]
