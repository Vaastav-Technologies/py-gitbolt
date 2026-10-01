# git hash-object

[documentation](https://git-scm.com/docs/git-hash-object)

### Overloads check

1) files supplied on cli:
    ```shell
    $ git hash-object README.md pyproject.toml
    420c7303f1473d651d10563122fbb560bcc58f18
    77a287da24c115af0f70807143b214bc10ff3b7e
    ```
2) files with no-filter:
   ```shell
   $ git hash-object README.md pyproject.toml --no-filters
   7b57702826b23bceafcff707e7d098174dc6b911
   77a287da24c115af0f70807143b214bc10ff3b7e
   ```
3) files with literally asn/or no-filters:
   ```shell
   $ git hash-object README.md pyproject.toml --literally --no-filters
   7b57702826b23bceafcff707e7d098174dc6b911
   77a287da24c115af0f70807143b214bc10ff3b7e
   ```
4) files supplied on cli with some content on stdin, stdin content treated as one blob:
    ```shell
    $ git hash-object README.md pyproject.toml --stdin
    README.md
    pyproject.toml
    ^Z
    5cf2e020410a1bd0fd3cfd84cb650b77fa529499
    420c7303f1473d651d10563122fbb560bcc58f18
    77a287da24c115af0f70807143b214bc10ff3b7e
    ```
5) stdin content supplied:
    ```shell
    $ git hash-object --stdin
    README pyproject
    pyproject
    ^D
    ^Z
    f6041284446082947582c1a07a5dbd95caeb1373
    ```
6) filepaths and stdin-paths cannot be supplied together:
    ```shell
    $ git hash-object README.md pyproject.toml --stdin-paths
    error: Can't specify files with --stdin-paths
    ```
7) stdin and stdin-paths cannot be supplied together:
    ```shell
    $ git hash-object --stdin --stdin-paths
    error: Can't use --stdin-paths with --stdin
    ```
8) Does not require git repo to just calculate a hash:
    ```shell
    $ git hash-object text.txt
    ff74c091ea05be29fb7354da08d42f71f34956c1
    ```
9) Requires a git repo to write the hash:
    ```shell
    $ git hash-object -w text.txt
    fatal: not a git repository (or any of the parent directories): .git
    ```
10) path file used to hash a repo outside file as if it were inside the repo
    ```shell
    $ git hash-object --path=path-to-repo pathspec-file
    dc4a47da6342d30a44bbf4ac00183673a37399af
    ```
11) path and no-filter cannot be supplied together:
    ```shell
    $ git hash-object --path=pathspec-file pathspec-file --no-filter
    error: Can't use --path with --no-filters
    ```
12) literally can be used:
   ```shell
   $ git hash-object --path=pathspec-file pathspec-file --literally -w
   dc4a47da6342d30a44bbf4ac00183673a37399af
   ```
13) path and stdin-path cannot be used together:
   ```shell
   $ git hash-object --path=pathspec-file --stdin-paths
   error: Can't use --stdin-paths with --path
   ```
14) literally can be used with stdin-paths:
   ```shell
   $ git hash-object --stdin-paths --literally
   README.md
   7b57702826b23bceafcff707e7d098174dc6b911
   pyproject.toml
   77a287da24c115af0f70807143b214bc10ff3b7e
   ^Z
   ```
15) type can be used with stdin-paths
   ```shell
   $ git hash-object --stdin-paths --literally -t commit
   README.md
   c2e06e742fa583924e30a52e1c84b3eb5af216a7
   ```
16) no-filter can be used with stdin-paths
```shell
$ git hash-object --stdin-paths --literally -t commit --no-filter
README.md
c2e06e742fa583924e30a52e1c84b3eb5af216a7

```
