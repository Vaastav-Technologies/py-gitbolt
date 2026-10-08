# git commit-tree

[documentation](https://git-scm.com/docs/git-commit-tree)

`git commit-tree` creates a commit object from an existing tree and prints the
new commit id. It writes to the object database, so a repository is required.

### Overloads check

1) tree and message (`-m`):
    ```shell
    $ git commit-tree <tree> -m "first"
    ```
2) parents (`-p`), can be given more than once:
    ```shell
    $ git commit-tree <tree> -p <parent> -m "second"
    $ git commit-tree <tree> -p <p1> -p <p2> -m "merge"
    ```
3) message from file (`-F`):
    ```shell
    $ git commit-tree <tree> -F msg.txt
    ```
4) message from stdin via `-F -`:
    ```shell
    $ git commit-tree <tree> -F -
    ```
5) message from stdin when neither `-m` nor `-F` is given:
    ```shell
    $ git commit-tree <tree>
    ```
    GitBolt requires `stdin=` in this form so the process does not hang.
6) multiple `-m` paragraphs:
    ```shell
    $ git commit-tree <tree> -m "a" -m "b"
    ```
7) GPG sign / countermand:
    ```shell
    $ git commit-tree <tree> -S -m "signed"
    $ git commit-tree <tree> -S<keyid> -m "signed"
    $ git commit-tree <tree> --no-gpg-sign -m "unsigned"
    ```
8) Requires a git repository:
    ```shell
    $ git commit-tree <tree> -m "first"
    fatal: not a git repository (or any of the parent directories): .git
    ```
