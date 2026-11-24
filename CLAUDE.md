# gitbolt

## Tests

- **Run git through gitbolt**, never through `subprocess`, in every test and in every fixture or helper of the tests:
  - `git.subcmd_unchecked().run([...])` for every subcommand that is not yet provided by gitbolt, such as `init`. Use gitbolt's interfaces for all available commands.
  - `git.session(...)` for long-running processes, such as `cat-file --batch` or `mktree --batch`.
- **Use gitbolt's own fixtures** for repositories. They are in `src/gitbolt/pytest_plugin.py`, and pytest loads them by
  itself (no import needed):
  - `repo_root`: an empty directory, which is not a repository yet.
  - `repo_remote`: a bare repository.
  - `repo_local`: a clone of `repo_remote`.
- **An option that the fixtures lack** (like `git init --object-format`) is no reason to leave gitbolt: start from
  `repo_root` and run the subcommand through gitbolt.
- **Before writing a test file**, read the tests next to it and follow them.
