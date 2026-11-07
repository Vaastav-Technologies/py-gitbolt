#!/usr/bin/env python3
# coding=utf-8

"""
Helper interfaces specific to ``git config`` subcommand.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Protocol, override, Literal

from gitbolt._internal_init import errmsg_creator
from gitbolt.exceptions import GitExitingException
from vt.utils.errors.error_specs import ERR_DATA_FORMAT_ERR, ERR_INVALID_USAGE
from vt.utils.errors.error_specs.utils import require_type

CONFIG_TYPES = ("bool", "int", "bool-or-int", "path", "expiry-date", "color")
ConfigType = Literal["bool", "int", "bool-or-int", "path", "expiry-date", "color"]


class ConfigArgsValidator(Protocol):  # pragma: no cover
    """
    The argument validator for ``git config`` subcommand.
    """

    @abstractmethod
    def validate_list(
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
    ) -> None: ...

    @abstractmethod
    def validate_get(
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
    ) -> None: ...

    @abstractmethod
    def validate_set(
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
    ) -> None: ...

    @abstractmethod
    def validate_unset(
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
    ) -> None: ...

    @abstractmethod
    def validate_rename_section(
        self,
        old_name: str,
        new_name: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
    ) -> None: ...

    @abstractmethod
    def validate_remove_section(
        self,
        name: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
    ) -> None: ...


class UtilConfigArgsValidator(ConfigArgsValidator):
    """
    Independent utility to perform ``git config`` argument validation.

    File-option flags are exclusive. Flags are omitted unless the caller sets them,
    so GitBolt does not change Git's default read/write scopes.
    """

    @override
    def validate_list(
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
    ) -> None:
        """
        >>> UtilConfigArgsValidator().validate_list()
        >>> UtilConfigArgsValidator().validate_list(file=Path("cfg"))
        >>> UtilConfigArgsValidator().validate_list(system=True, global_=True)
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: system and global are not allowed together
        """
        self._validate_file_options(
            system=system,
            global_=global_,
            local=local,
            worktree=worktree,
            file=file,
            blob=blob,
        )
        self._validate_includes(includes=includes, no_includes=no_includes)
        self._validate_type(type=type, no_type=no_type)
        require_type(name_only, "name_only", bool, GitExitingException)
        require_type(show_origin, "show_origin", bool, GitExitingException)
        require_type(show_scope, "show_scope", bool, GitExitingException)
        require_type(z, "z", bool, GitExitingException)

    @override
    def validate_get(
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
    ) -> None:
        """
        >>> UtilConfigArgsValidator().validate_get("core.filemode")
        >>> UtilConfigArgsValidator().validate_get("core.filemode", file=Path("cfg"), all=True)
        >>> UtilConfigArgsValidator().validate_get("")
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: 'name' is required
        """
        self._require_non_empty_str(name, "name")
        self._validate_file_options(
            system=system,
            global_=global_,
            local=local,
            worktree=worktree,
            file=file,
            blob=blob,
        )
        self._validate_includes(includes=includes, no_includes=no_includes)
        self._validate_value_match(
            value=value, no_value=no_value, fixed_value=fixed_value
        )
        self._validate_type(type=type, no_type=no_type)
        if show_names and no_show_names:
            errmsg = errmsg_creator.not_allowed_together("show_names", "no_show_names")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        require_type(all, "all", bool, GitExitingException)
        require_type(regexp, "regexp", bool, GitExitingException)
        require_type(name_only, "name_only", bool, GitExitingException)
        require_type(show_names, "show_names", bool, GitExitingException)
        require_type(no_show_names, "no_show_names", bool, GitExitingException)
        require_type(show_origin, "show_origin", bool, GitExitingException)
        require_type(show_scope, "show_scope", bool, GitExitingException)
        require_type(z, "z", bool, GitExitingException)
        if default is not None:
            require_type(default, "default", str, GitExitingException)
        if url is not None:
            require_type(url, "url", str, GitExitingException)

    @override
    def validate_set(
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
    ) -> None:
        """
        >>> UtilConfigArgsValidator().validate_set("core.filemode", "true")
        >>> UtilConfigArgsValidator().validate_set("core.filemode", "true", file=Path("cfg"))
        >>> UtilConfigArgsValidator().validate_set("core.filemode", "true", all=True, append=True)
        Traceback (most recent call last):
        gitbolt.exceptions.GitExitingException: ValueError: all and append are not allowed together
        """
        self._require_non_empty_str(name, "name")
        require_type(value, "value", str, GitExitingException)
        self._validate_file_options(
            system=system,
            global_=global_,
            local=local,
            worktree=worktree,
            file=file,
            blob=None,
            allow_blob=False,
        )
        self._validate_type(type=type, no_type=False)
        self._validate_value_match(
            value=value_pattern, no_value=no_value, fixed_value=fixed_value
        )
        require_type(all, "all", bool, GitExitingException)
        require_type(append, "append", bool, GitExitingException)
        if all and append:
            errmsg = errmsg_creator.not_allowed_together("all", "append")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if comment is not None:
            require_type(comment, "comment", str, GitExitingException)
            if "\n" in comment:
                errmsg = "'comment' must not contain linefeed characters"
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)

    @override
    def validate_unset(
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
    ) -> None:
        """
        >>> UtilConfigArgsValidator().validate_unset("diff.renames")
        >>> UtilConfigArgsValidator().validate_unset("diff.renames", file=Path("cfg"), all=True)
        """
        self._require_non_empty_str(name, "name")
        self._validate_file_options(
            system=system,
            global_=global_,
            local=local,
            worktree=worktree,
            file=file,
            blob=None,
            allow_blob=False,
        )
        self._validate_value_match(
            value=value, no_value=no_value, fixed_value=fixed_value
        )
        require_type(all, "all", bool, GitExitingException)

    @override
    def validate_rename_section(
        self,
        old_name: str,
        new_name: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
    ) -> None:
        """
        >>> UtilConfigArgsValidator().validate_rename_section("section", "other", file=Path("cfg"))
        """
        self._require_non_empty_str(old_name, "old_name")
        self._require_non_empty_str(new_name, "new_name")
        self._validate_file_options(
            system=system,
            global_=global_,
            local=local,
            worktree=worktree,
            file=file,
            blob=None,
            allow_blob=False,
        )

    @override
    def validate_remove_section(
        self,
        name: str,
        *,
        system: bool = False,
        global_: bool = False,
        local: bool = False,
        worktree: bool = False,
        file: Path | None = None,
    ) -> None:
        """
        >>> UtilConfigArgsValidator().validate_remove_section("section", file=Path("cfg"))
        """
        self._require_non_empty_str(name, "name")
        self._validate_file_options(
            system=system,
            global_=global_,
            local=local,
            worktree=worktree,
            file=file,
            blob=None,
            allow_blob=False,
        )

    def _validate_file_options(
        self,
        *,
        system: bool,
        global_: bool,
        local: bool,
        worktree: bool,
        file: Path | None,
        blob: str | None,
        allow_blob: bool = True,
    ) -> None:
        require_type(system, "system", bool, GitExitingException)
        require_type(global_, "global_", bool, GitExitingException)
        require_type(local, "local", bool, GitExitingException)
        require_type(worktree, "worktree", bool, GitExitingException)
        if not allow_blob and blob is not None:
            errmsg = errmsg_creator.not_allowed_together("blob", "write")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        selected: list[str] = []
        if system:
            selected.append("system")
        if global_:
            selected.append("global")
        if local:
            selected.append("local")
        if worktree:
            selected.append("worktree")
        if file is not None:
            selected.append("file")
            self._require_path(file, "file")
        if blob is not None:
            selected.append("blob")
            require_type(blob, "blob", str, GitExitingException)
            if blob == "":
                errmsg = "'blob' must not be empty"
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
        if len(selected) > 1:
            errmsg = errmsg_creator.not_allowed_together(selected[0], selected[1])
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    def _validate_includes(self, *, includes: bool, no_includes: bool) -> None:
        require_type(includes, "includes", bool, GitExitingException)
        require_type(no_includes, "no_includes", bool, GitExitingException)
        if includes and no_includes:
            errmsg = errmsg_creator.not_allowed_together("includes", "no_includes")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    def _validate_type(self, *, type: ConfigType | None, no_type: bool) -> None:
        require_type(no_type, "no_type", bool, GitExitingException)
        if type is not None:
            if type not in CONFIG_TYPES:
                errmsg = errmsg_creator.errmsg_for_choices(
                    emphasis="type", choices=list(CONFIG_TYPES)
                )
                raise GitExitingException(
                    errmsg, exit_code=ERR_INVALID_USAGE
                ) from ValueError(errmsg)
        if no_type and type is None:
            errmsg = "no_type has no effect without type"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    def _validate_value_match(
        self, *, value: str | None, no_value: bool, fixed_value: bool
    ) -> None:
        require_type(no_value, "no_value", bool, GitExitingException)
        require_type(fixed_value, "fixed_value", bool, GitExitingException)
        if value is not None:
            require_type(value, "value", str, GitExitingException)
        if no_value and value is not None:
            errmsg = errmsg_creator.not_allowed_together("value", "no_value")
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)
        if fixed_value and value is None and not no_value:
            errmsg = "fixed_value requires value"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    def _require_non_empty_str(self, value: str, name: str) -> None:
        require_type(value, name, str, GitExitingException)
        if value == "":
            errmsg = f"'{name}' is required"
            raise GitExitingException(
                errmsg, exit_code=ERR_INVALID_USAGE
            ) from ValueError(errmsg)

    def _require_path(self, value: Path, name: str) -> None:
        if not isinstance(value, Path):
            errmsg = f"'{name}' must be a pathlib.Path"
            raise GitExitingException(
                errmsg, exit_code=ERR_DATA_FORMAT_ERR
            ) from TypeError(errmsg)
