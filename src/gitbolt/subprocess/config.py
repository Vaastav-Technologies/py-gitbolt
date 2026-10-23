#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces for ``git config`` subcommand with default implementation for subprocess calls.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Protocol, override, Literal

from gitbolt.config import ConfigType
from gitbolt.subprocess.constants import (
    CONFIG_CMD,
    CONFIG_LIST_CMD,
    CONFIG_GET_CMD,
    CONFIG_SET_CMD,
    CONFIG_UNSET_CMD,
    CONFIG_RENAME_SECTION_CMD,
    CONFIG_REMOVE_SECTION_CMD,
)


class ConfigCLIArgsBuilder(Protocol):
    """
    Interface to facilitate building of cli arguments for ``git config`` subcommand.
    """

    @abstractmethod
    def build_list(
        self,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
        blob: str | None = None,
        includes: bool = False,
        no_includes: bool = False,
        type: ConfigType | None = None,
        no_type: bool = False,
        name_only: bool = False,
        show_origin: bool = False,
        show_scope: bool = False,
        z: bool = False,
    ) -> list[str]: ...

    @abstractmethod
    def build_get(
        self,
        name: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
        blob: str | None = None,
        includes: bool = False,
        no_includes: bool = False,
        all: bool = False,
        regexp: bool = False,
        value: str | None = None,
        no_value: bool = False,
        fixed_value: bool = False,
        default: str | None = None,
        url: str | None = None,
        type: ConfigType | None = None,
        no_type: bool = False,
        name_only: bool = False,
        show_names: bool = False,
        no_show_names: bool = False,
        show_origin: bool = False,
        show_scope: bool = False,
        z: bool = False,
    ) -> list[str]: ...

    @abstractmethod
    def build_set(
        self,
        name: str,
        value: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
        type: ConfigType | None = None,
        all: bool = False,
        append: bool = False,
        value_pattern: str | None = None,
        no_value: bool = False,
        fixed_value: bool = False,
        comment: str | None = None,
    ) -> list[str]: ...

    @abstractmethod
    def build_unset(
        self,
        name: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
        all: bool = False,
        value: str | None = None,
        no_value: bool = False,
        fixed_value: bool = False,
    ) -> list[str]: ...

    @abstractmethod
    def build_rename_section(
        self,
        old_name: str,
        new_name: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
    ) -> list[str]: ...

    @abstractmethod
    def build_remove_section(
        self,
        name: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
    ) -> list[str]: ...


class IndividuallyOverridableCCAB(ConfigCLIArgsBuilder):
    """
    Individually Overridable Config CLI Args Builder.

    Flags are emitted only when the caller sets them so Git keeps its own defaults
    (for example write-to-local, includes-on when searching all files).
    """

    @override
    def build_list(
        self,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
        blob: str | None = None,
        includes: bool = False,
        no_includes: bool = False,
        type: ConfigType | None = None,
        no_type: bool = False,
        name_only: bool = False,
        show_origin: bool = False,
        show_scope: bool = False,
        z: bool = False,
    ) -> list[str]:
        """
        >>> builder = IndividuallyOverridableCCAB()
        >>> builder.build_list()
        ['config', 'list']
        >>> builder.build_list(file=Path("cfg")) == ["config", "list", "--file", "cfg"]
        True
        >>> builder.build_list(name_only=True, z=True)
        ['config', 'list', '--name-only', '-z']
        """
        args = [CONFIG_CMD, CONFIG_LIST_CMD]
        args.extend(self.file_option_args(
            system=system, global_=global_, local=local, worktree=worktree, file=file, blob=blob
        ))
        args.extend(self.includes_args(includes=includes, no_includes=no_includes))
        args.extend(self.type_args(type=type, no_type=no_type))
        args.extend(self.true_flag(name_only, "--name-only"))
        args.extend(self.true_flag(show_origin, "--show-origin"))
        args.extend(self.true_flag(show_scope, "--show-scope"))
        args.extend(self.true_flag(z, "-z"))
        return args

    @override
    def build_get(
        self,
        name: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
        blob: str | None = None,
        includes: bool = False,
        no_includes: bool = False,
        all: bool = False,
        regexp: bool = False,
        value: str | None = None,
        no_value: bool = False,
        fixed_value: bool = False,
        default: str | None = None,
        url: str | None = None,
        type: ConfigType | None = None,
        no_type: bool = False,
        name_only: bool = False,
        show_names: bool = False,
        no_show_names: bool = False,
        show_origin: bool = False,
        show_scope: bool = False,
        z: bool = False,
    ) -> list[str]:
        """
        >>> builder = IndividuallyOverridableCCAB()
        >>> builder.build_get("core.filemode")
        ['config', 'get', 'core.filemode']
        >>> builder.build_get("core.gitproxy", all=True, show_names=True)
        ['config', 'get', '--all', '--show-names', 'core.gitproxy']
        >>> builder.build_get("color.diff.whitespace", type="color", default="blue reverse")
        ['config', 'get', '--default', 'blue reverse', '--type=color', 'color.diff.whitespace']
        """
        args = [CONFIG_CMD, CONFIG_GET_CMD]
        args.extend(self.file_option_args(
            system=system, global_=global_, local=local, worktree=worktree, file=file, blob=blob
        ))
        args.extend(self.includes_args(includes=includes, no_includes=no_includes))
        args.extend(self.true_flag(all, "--all"))
        args.extend(self.true_flag(regexp, "--regexp"))
        args.extend(self.value_match_args(
            value=value, no_value=no_value, fixed_value=fixed_value
        ))
        if default is not None:
            args.extend(["--default", default])
        if url is not None:
            args.extend([f"--url={url}"])
        args.extend(self.type_args(type=type, no_type=no_type))
        args.extend(self.true_flag(name_only, "--name-only"))
        args.extend(self.true_flag(show_names, "--show-names"))
        args.extend(self.true_flag(no_show_names, "--no-show-names"))
        args.extend(self.true_flag(show_origin, "--show-origin"))
        args.extend(self.true_flag(show_scope, "--show-scope"))
        args.extend(self.true_flag(z, "-z"))
        args.append(name)
        return args

    @override
    def build_set(
        self,
        name: str,
        value: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
        type: ConfigType | None = None,
        all: bool = False,
        append: bool = False,
        value_pattern: str | None = None,
        no_value: bool = False,
        fixed_value: bool = False,
        comment: str | None = None,
    ) -> list[str]:
        """
        >>> builder = IndividuallyOverridableCCAB()
        >>> builder.build_set("core.filemode", "true")
        ['config', 'set', 'core.filemode', 'true']
        >>> builder.build_set("core.gitproxy", "ssh", append=True)
        ['config', 'set', '--append', 'core.gitproxy', 'ssh']
        >>> builder.build_set("core.filemode", "true", file=Path("cfg")) == [
        ...     "config", "set", "--file", "cfg", "core.filemode", "true"
        ... ]
        True
        """
        args = [CONFIG_CMD, CONFIG_SET_CMD]
        args.extend(self.file_option_args(
            system=system, global_=global_, local=local, worktree=worktree, file=file, blob=None
        ))
        args.extend(self.type_args(type=type, no_type=False))
        args.extend(self.true_flag(all, "--all"))
        args.extend(self.true_flag(append, "--append"))
        args.extend(self.value_match_args(
            value=value_pattern, no_value=no_value, fixed_value=fixed_value
        ))
        if comment is not None:
            args.extend(["--comment", comment])
        args.extend([name, value])
        return args

    @override
    def build_unset(
        self,
        name: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
        all: bool = False,
        value: str | None = None,
        no_value: bool = False,
        fixed_value: bool = False,
    ) -> list[str]:
        """
        >>> IndividuallyOverridableCCAB().build_unset("diff.renames")
        ['config', 'unset', 'diff.renames']
        >>> IndividuallyOverridableCCAB().build_unset("core.gitproxy", all=True)
        ['config', 'unset', '--all', 'core.gitproxy']
        """
        args = [CONFIG_CMD, CONFIG_UNSET_CMD]
        args.extend(self.file_option_args(
            system=system, global_=global_, local=local, worktree=worktree, file=file, blob=None
        ))
        args.extend(self.true_flag(all, "--all"))
        args.extend(self.value_match_args(
            value=value, no_value=no_value, fixed_value=fixed_value
        ))
        args.append(name)
        return args

    @override
    def build_rename_section(
        self,
        old_name: str,
        new_name: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
    ) -> list[str]:
        """
        >>> IndividuallyOverridableCCAB().build_rename_section("section", "other")
        ['config', 'rename-section', 'section', 'other']
        """
        args = [CONFIG_CMD, CONFIG_RENAME_SECTION_CMD]
        args.extend(self.file_option_args(
            system=system, global_=global_, local=local, worktree=worktree, file=file, blob=None
        ))
        args.extend([old_name, new_name])
        return args

    @override
    def build_remove_section(
        self,
        name: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
    ) -> list[str]:
        """
        >>> IndividuallyOverridableCCAB().build_remove_section("section")
        ['config', 'remove-section', 'section']
        """
        args = [CONFIG_CMD, CONFIG_REMOVE_SECTION_CMD]
        args.extend(self.file_option_args(
            system=system, global_=global_, local=local, worktree=worktree, file=file, blob=None
        ))
        args.append(name)
        return args

    def file_option_args(
        self,
        *,
        system: bool,
        global_: bool,
        local: bool,
        worktree: bool,
        file: Path | None,
        blob: str | None,
    ) -> list[str]:
        """
        >>> IndividuallyOverridableCCAB().file_option_args(
        ...     system=False, global_=False, local=False, worktree=False, file=None, blob=None
        ... )
        []
        >>> IndividuallyOverridableCCAB().file_option_args(
        ...     system=False, global_=True, local=False, worktree=False, file=None, blob=None
        ... )
        ['--global']
        """
        if system:
            return ["--system"]
        if global_:
            return ["--global"]
        if local:
            return ["--local"]
        if worktree:
            return ["--worktree"]
        if file is not None:
            return ["--file", str(file)]
        if blob is not None:
            return ["--blob", blob]
        return []

    def includes_args(self, *, includes: bool, no_includes: bool) -> list[str]:
        if includes:
            return ["--includes"]
        if no_includes:
            return ["--no-includes"]
        return []

    def type_args(self, *, type: ConfigType | None, no_type: bool) -> list[str]:
        args: list[str] = []
        if type is not None:
            args.append(f"--type={type}")
        if no_type:
            args.append("--no-type")
        return args

    def value_match_args(
        self, *, value: str | None, no_value: bool, fixed_value: bool
    ) -> list[str]:
        args: list[str] = []
        if value is not None:
            args.append(f"--value={value}")
        if no_value:
            args.append("--no-value")
        if fixed_value:
            args.append("--fixed-value")
        return args

    def true_flag(self, flag: bool, opt: str) -> list[str]:
        return [opt] if flag else []
