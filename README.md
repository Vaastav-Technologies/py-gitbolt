# Gitbolt

Typed Git command interfaces in Python.

> Note: Here compile-time checks actually mean checks done by python static-type checkers like mypy or pyright.

### Motivation

Running system commands in python can be tricky for the following reasons:

1) The command arguments sent to `subprocess` may not be typed correctly and may result in wrong command interpretation
   at runtime.
2) Sent command arguments or their groups may be mutually exclusive in certain scenarios, this may manifest itself as an
   error at runtime.
3) There may be certain command arguments that are required or must be provided only when certain other command
   arguments are provided, this will err at runtime with nasty tracebacks.

Apart from these, running commands using subprocess requires:

* Technical standpoint:
    * Setting up a process.
    * Piping its respective file-descriptors if communication is required.
    * Running the process.
    * Tearing down the process.
* Learning standpoint:
    * Having exhaustive knowledge of CLI commands.

Reasons listed above are compelling enough for people who work heavily with programming git and/or using it inside
their own programs to make an ergonomic, fast and compile-time-type-checked library for it.

### Aim of this project

To provide a uniform and predictable behavior at compile(or type-checking)-time to git commands when used in Python.
The following are targeted:

<details>
<summary>Make git command interfaces as ergonomic to the user as possible.</summary>

##### Provide versions of most used command combinations

`git hash-object` can take multiple files at the cli to give out multiple hashes (one per file). But,
`git hash-object` is mostly ever used to write one file to git object database and get a hash for it hence, it is more
ergonomic to provide a method call to the user that simply takes one file and returns one hash. Other calls that satisfy
all the different `git hash-object` behavior can also be provided to give users all the call options/combinations.

##### Let subcommands be passed around as objects

This can enable the user to write with parameter that only takes a required subset of subcommands which will make user's
life easier as they'd be able to write logic which is more focussed on one thing and can do one thing pretty good.

```python

import gitbolt
from gitbolt.git_subprocess.impl.simple import SimpleGitCommand

git = SimpleGitCommand()
version_subcmd = git.version_subcmd
add_subcmd = git.add_subcmd


def method_which_only_adds_a_file(add_subcmd: vt.vcs.git.gitlib.base.Add):
    """
    This method only requires the ``add`` subcommand.
    """
    ...


method_which_only_adds_a_file(add_subcmd)
```
</details>

<details>
<summary>Model git commands and subcommands to be called as methods in Python. </summary>

These methods are terminal operations and return the called subcommand's stdout.

```python
from gitbolt.git_subprocess.impl.simple import SimpleGitCommand

git = SimpleGitCommand()
status_out = git.status_subcmd.status()
print(status_out)
```
```python
"""
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
"""
```

</details>

<details>
<summary>Type-hint as extensively as possible so that compile-time checks can ensure runtime-safety later.</summary>
</details>

<details>
<summary>Allow users to set/unset/reset environment variables in typed manner in pythonic methods just before 
subcommand run to provide maximal flexibility.</summary>

#### Set environment variables in a typed manner

##### Just override one git env (as `GIT_TRACE`) and return a git command

```python
from gitbolt.git_subprocess.impl.simple import SimpleGitCommand

git = SimpleGitCommand()
git = git.git_envs_override(GIT_TRACE=True)
```

##### Override multiple envs (as `GIT_TRACE`, `GIT_DIR` and `GIT_EDITOR`) and return a git command

```python
from pathlib import Path
from gitbolt.git_subprocess.impl.simple import SimpleGitCommand

git = SimpleGitCommand()
git = git.git_envs_override(GIT_TRACE=1, GIT_DIR=Path('/tmp/git-dir/'), GIT_EDITOR='vim')
```

##### Allow users to pass git commands around and perform multiple git envs overrides

```python
from pathlib import Path
from gitbolt.git_subprocess.impl.simple import SimpleGitCommand

git = SimpleGitCommand()
overridden_git = git.git_envs_override(GIT_SSH=Path('/tmp/SSH')).git_envs_override(GIT_TERMINAL_PROMPT=1,
                                                                                   GIT_NO_REPLACE_OBJECTS=True)
re_overridden_git = overridden_git.git_envs_override(GIT_TRACE=True)
```

##### Allow users to pass git commands around and unset git envs in their own overrides

```python
from gitbolt.git_subprocess.impl.simple import SimpleGitCommand
from vt.utils.commons.commons.core_py import UNSET

git = SimpleGitCommand()
# set GIT_TRACE to True
overridden_git = git.git_envs_override(GIT_ADVICE=True).git_envs_override(GIT_TRACE=True)

# unset GIT_TRACE later-on
no_advice_unset_git = overridden_git.git_envs_override(GIT_TRACE=UNSET)
```

##### Allow users to pass git commands around and reset git opts in their own overrides

```python
from gitbolt.git_subprocess.impl.simple import SimpleGitCommand

git = SimpleGitCommand()
# set GIT_TRACE to True
overridden_git = git.git_envs_override(GIT_TRACE=True)

# reset GIT_TRACE later-on to False
git_trace_reset_git = overridden_git.git_envs_override(GIT_TRACE=False)
```

</details>

<details>
<summary>Allow users to set/unset/reset git main command options in typed and pythonic manner just before subcommand 
run to provide maximal flexibility.</summary>

#### Set git main command options in a typed manner

##### Just override one git opt (as `--no-replace-objects`) and return a git command

```python
from gitbolt.git_subprocess.impl.simple import SimpleGitCommand

git = SimpleGitCommand()
git = git.git_opts_override(no_replace_objects=True)
```

##### Override multiple options (as `--no-replace-objects`, `--git-dir` and `--paginate`) and return a git command

```python
from pathlib import Path
from gitbolt.git_subprocess.impl.simple import SimpleGitCommand

git = SimpleGitCommand()
git = git.git_opts_override(no_replace_objects=True, git_dir=Path(), paginate=True)
```

##### Allow users to pass git commands around and perform multiple git opts overrides

```python
from pathlib import Path
from gitbolt.git_subprocess.impl.simple import SimpleGitCommand

git = SimpleGitCommand()
overridden_git = git.git_opts_override(exec_path=Path('tmp')).git_opts_override(noglob_pathspecs=True,
                                                                                no_advice=True).git_opts_override(
    config_env={'auth': 'suhas', 'comm': 'suyog'})
re_overridden_git = overridden_git.git_opts_override(glob_pathspecs=True)
```

##### Allow users to pass git commands around and unset git opts in their own overrides

```python
from pathlib import Path
from gitbolt.git_subprocess.impl.simple import SimpleGitCommand
from vt.utils.commons.commons.core_py import UNSET

git = SimpleGitCommand()
# set --no-advice to True
overridden_git = git.git_opts_override(exec_path=Path('tmp')).git_opts_override(no_advice=True)

# unset --no-advice later-on
no_advice_unset_git = overridden_git.git_opts_override(no_advice=UNSET)
```

##### Allow users to pass git commands around and reset git opts in their own overrides

```python
from gitbolt.git_subprocess.impl.simple import SimpleGitCommand

git = SimpleGitCommand()
# set --no-advice to True
overridden_git = git.git_opts_override(no_advice=True)

# reset --no-advice later-on to False
no_advice_reset_git = overridden_git.git_opts_override(no_advice=False)
```

</details>

<details>
<summary>Return the full stdout output to the user. Parsing the output of a git command  and do not try to be fancy 
with it, i.e, no need to parse the stdout output into python objects. Leave parsing of outputs to the user. They'd know better.
</summary>
</details> 

<details>
<summary>Optionally, transformers can be planned, provided and shipped at a later date with this library (or a 
separate library). These transformers can supply a format to the git command and thus can parse the output from it 
into a python object.</summary>
</details>


## Benefits out-of-the box

- Provides maximal flexibility to run git commands by the mechanism of override.
- Inherently lazily processed.
- Returns a git command stdout as-is.
- Raises any error as a python recognisable exception.
- Exceptions capture stdout, stderr as well as the return-code of the run command.
- Very typed.
- Write commands in idiomatic Python at compile-time and be sure that they'll run as expected during runtime.
- Fail-fast.
- Send commands around like objects.
- Git subcommands are terminal-functions.


## Future goals
- support `pygit2` to enable fast and direct library based access.
- support `porcelain` on each command if it needs `pygit2` support.
