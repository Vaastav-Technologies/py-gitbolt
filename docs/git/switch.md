# git switch

[documentation](https://git-scm.com/docs/git-switch)

### Switch to a branch

```shell
$ git switch master
```

### Create and switch

```shell
$ git switch -c fixup HEAD~3
```

### Detach

```shell
$ git switch --detach HEAD~3
```

### Orphan

```shell
$ git switch --orphan new-branch
```

``--guess`` is Git's default; GitBolt omits it unless ``guess`` is set. ``force=True`` maps to ``--discard-changes`` (Git ``-f``).
