# git config

[documentation](https://git-scm.com/docs/git-config)

`git config` gets and sets repository or global options. GitBolt wraps the
current subcommands (`list`, `get`, `set`, `unset`, `rename-section`,
`remove-section`). Deprecated modes (`git config <name> <value>`, `--get`,
`--add`, …) are not exposed. `edit` is not wrapped (it opens an editor).

File-option flags (`--system`, `--global`, `--local`, `--worktree`, `--file`,
`--blob`) are omitted unless set, so Git keeps its default scopes: read from
all files, write to the repository `.git/config`. Python uses `global_` for
`--global`.

Writes in tests should use `file=` so they never change the user or system
config, and they do not change other GitBolt commands (those still use
`git -c` / env overrides, not this subcommand).

### Overloads check

1) list:
    ```shell
    $ git config list
    $ git config list --file cfg
    $ git config list --name-only
    ```
2) get:
    ```shell
    $ git config get core.filemode
    $ git config get --all --show-names core.gitproxy
    $ git config get --type=bool --default=false core.filemode
    $ git config get --url=https://example.com http.sslverify
    ```
3) set (write to repo local by default; pass `file=` to target a file):
    ```shell
    $ git config set core.filemode true
    $ git config set --file cfg core.filemode true
    $ git config set --append core.gitproxy '"proxy" for example.com'
    $ git config set --all core.gitproxy ssh
    $ git config set --value='for kernel.org$' core.gitproxy '"ssh" for kernel.org'
    ```
4) unset:
    ```shell
    $ git config unset diff.renames
    $ git config unset --all core.gitproxy
    ```
5) rename-section / remove-section:
    ```shell
    $ git config rename-section section other
    $ git config remove-section section
    ```
6) `--system` and `--global` cannot be combined:
    ```shell
    $ git config get --system --global core.filemode
    ```
    GitBolt rejects this before spawning Git.
7) `blob` is read-only (list/get), not for set/unset.
