# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Date format: YYYY-MM-DD

## [Unreleased]

### Added

- Listed Thamotharan R as a project author.

### Fixed

- `GitSession` ignores a broken pipe when closing a git process that already exited (`#11`).
  This avoids `BrokenPipeError` on macOS in `test_one_wrong_command_does_not_affect_others`.

## [0.0.0.dev26] - 2026-09-22

### Added

- Introduced initial Changelog.
- Preserved caller order of main git command options and env vars when forming commands (`#2`).
  `build_main_cmd_args()` and `str(git)` now follow the order passed to `git_opts_override()` / `git_envs_override()`.

### Changed

- `merge_typed_dicts` keeps insertion order: existing fallback keys first, then new keys from each override.
- `GitCommand.build_main_cmd_args()` walks `_main_cmd_opts` instead of a fixed `-C`, `-c`, `--exec-path` sequence.

## [0.0.0.dev25] - 2026-08-06

### Added

- String representation of git commands to ease debugging.
- Worktree lifecycle functions.
- Warnings for unstable worktree implementations.

### Changed

- Subcommand properties are now functions (clearer intent; created lazily).
- `clone` and `subcmd` methods separated so cloning no longer raised the worktree warning.
