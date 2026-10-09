# git update-ref

[documentation](https://git-scm.com/docs/git-update-ref)

`git update-ref` updates the object name stored in a ref safely. It writes
under `.git`, so a repository is required.

### Overloads check

1) store a new value:
    ```shell
    $ git update-ref <ref> <new-oid>
    ```
2) store a new value after verifying the old value:
    ```shell
    $ git update-ref <ref> <new-oid> <old-oid>
    ```
    Forty `0` characters (or empty) as `<old-oid>` requires that the ref does not exist.
3) delete:
    ```shell
    $ git update-ref -d <ref>
    $ git update-ref -d <ref> <old-oid>
    ```
4) reason / no-deref / create-reflog:
    ```shell
    $ git update-ref -m "reason" --no-deref --create-reflog <ref> <new-oid>
    ```
5) stdin batch:
    ```shell
    $ git update-ref --stdin
    $ git update-ref --stdin -z --batch-updates
    ```
    GitBolt requires `stdin=` so the process does not hang.
6) Requires a git repository:
    ```shell
    $ git update-ref refs/heads/x <oid>
    fatal: not a git repository (or any of the parent directories): .git
    ```
