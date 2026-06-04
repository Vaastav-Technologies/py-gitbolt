# 🚀 Gitbolt

![PyPI - Types](https://img.shields.io/pypi/types/gitbolt)
![GitHub License](https://img.shields.io/github/license/Vaastav-Technologies/py-gitbolt)
[![🔧 test](https://github.com/Vaastav-Technologies/py-gitbolt/actions/workflows/test.yml/badge.svg)](https://github.com/Vaastav-Technologies/py-gitbolt/actions/workflows/test.yml)
[![💡 typecheck](https://github.com/Vaastav-Technologies/py-gitbolt/actions/workflows/typecheck.yml/badge.svg)](https://github.com/Vaastav-Technologies/py-gitbolt/actions/workflows/typecheck.yml)
[![🛠️ lint](https://github.com/Vaastav-Technologies/py-gitbolt/actions/workflows/lint.yml/badge.svg)](https://github.com/Vaastav-Technologies/py-gitbolt/actions/workflows/lint.yml)
[![📊 coverage](https://codecov.io/gh/Vaastav-Technologies/py-gitbolt/branch/main/graph/badge.svg)](https://codecov.io/gh/Vaastav-Technologies/py-gitbolt)
[![📤 Upload Python Package](https://github.com/Vaastav-Technologies/py-gitbolt/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Vaastav-Technologies/py-gitbolt/actions/workflows/python-publish.yml)
![PyPI - Version](https://img.shields.io/pypi/v/gitbolt)

**Fast, flexible and type-safe Git command execution in Python using subprocess.**

---

## ✨ Features

* 🧠 **Typed:** All commands and options are statically type-checked.
* ⚡ **Fast:** Minimal abstractions over subprocess, runs directly on your system Git.
* 🧩 **Composable:** Git commands and options can be passed around as objects.
* 🔁 **Overridable:** Easily override environment variables and options in a chainable, readable manner.
* 📦 **Lightweight:** No dependencies on heavy Git libraries or C extensions.
* 🧰 **Extensible:** Future support for output transformers and other plugins.
* 🚨 **Exception Handling:** Raises any error as a Python-recognisable exception.
* 📤 **Debuggable:** Exceptions capture `stdout`, `stderr`, and the return code of the run command.
* 💤 **Lazy Execution:** Inherently lazily processed.
* 📄 **Transparent Output:** Returns a Git command's `stdout` as-is.
* 🧪 **Terminal Functions:** Git subcommands are terminal functions.
* 🧼 **Idiomatic Python:** Write commands in idiomatic Python at compile-time and be confident they’ll execute smoothly at runtime.
* 🎀 **Add-ons:** Special features provided to ease programming with git. These can be added if required.
* 💻 **CLI-cmd:** Take commands from cli and run in `gitbolt`.

---

## 📦 Installation

```bash
pip install gitbolt
```

---

## 💡 Motivation

Running system commands in Python can be tricky for the following reasons:

1. Arguments sent to `subprocess` may not be typed correctly and result in runtime errors.
2. Argument groups may be mutually exclusive or required conditionally — again causing runtime issues.
3. Errors from subprocess are often unhelpful and difficult to debug.

Also, using subprocess effectively means you must:

* Understand and manage process setup, piping, and teardown.
* Know your CLI command intricacies in depth.

> This project exists to fix all that — with ergonomics, speed, and type-safety.

---

## 🎯 Project Goals

### ✅ Predictable Compile-Time Behavior

Type-checking ensures runtime safety.

### ✅ Ergonomic APIs

<details>
<summary>Make git command interfaces as ergonomic to the user as possible.</summary>

#### Provide versions of most used command combinations

`git hash-object` supports taking multiple files and outputs a hash per file. But in practice, it's most often used to write a single file to the Git object database and return its hash. To match this real-world usage, Gitbolt offers a more ergonomic method that accepts one file and returns one hash — while still giving you the flexibility to access the full range of `git hash-object` capabilities when needed.

#### Let subcommands be passed around as objects

Gitbolt lets you pass subcommands around as typed objects. This enables highly focused, minimal APIs — you can write functions that accept only the subcommands they truly need. This leads to cleaner logic, better separation of concerns, and compile-time guarantees that help prevent misuse.

```python
import gitbolt

git = gitbolt.get_git()
version_subcmd = git.version_subcmd
add_subcmd = git.add_subcmd

def method_which_only_adds_a_file(add_subcmd: gitbolt.base.Add):
    """
    This method only requires the `add` subcommand.
    """
    ...

method_which_only_adds_a_file(add_subcmd)
```

</details>

### ✅ Subcommands as Objects

git subcommands are modeled as terminal functions that return stdout.

```python
import gitbolt

git = gitbolt.get_git()
version_stdout = git.version_subcmd.version().version()
print(version_stdout)
```

### 🪼 Modular Architecture

#### 🧑‍💻 Modular at the programmatic level

Commands are designed to be passed around as objects. This makes them modular and thus users can opt to use only
particular commands.

```python
from gitbolt import get_git

git = get_git() # get git object for the current working directory
add_subcmd = git.add_subcmd
ls_tree_subcmd = git.ls_tree_subcmd

# now, functions can be written to accept only the required subcommands and nothing more than that.
```

#### 📽️ Modular at project level

Only required commands and hence their implementations can be installed as per user requirement.

e.g.

- To install only the `git add` command related logic:
  - ```shell
    pip install gitbolt[add]
    ```
- To install command logic related to `git add` and `git rm` commands:
  - ```shell
    pip install gitbolt[add,rm]
    ```
- Install all porcelain related commands:
  - ```shell
    pip install gitbolt[porcelain]
    ```
- Install high performance `pygit2` implementations:
  - ```shell
    pip install gitbolt[pygit2]
    ```
  - ```shell
    pip install gitbolt[add,pygit2,rm]
    ```
- At last, install every command's implementation:
  - ```shell
    pip install gitbolt[all]
    ```

---

## 🧠 Strong Typing Everywhere

Extensive use of type-hints ensures that invalid usages fail early — at *compile-time*. Write at compile-time and be sure that commands run error-free at runtime.

---

<details>
<summary>Allow users to set/unset/reset Git environment variables and main command options using typed, chainable, Pythonic methods — just before a subcommand is executed.</summary>

### 🧬 Git Environment Variables

#### 🔁 Override a single Git env (e.g., `GIT_TRACE`)

```python
import gitbolt

git = gitbolt.get_git()
git = git.git_envs_override(GIT_TRACE=True)
```

#### 🌐 Override multiple Git envs (e.g., `GIT_TRACE`, `GIT_DIR`, `GIT_EDITOR`)

```python
from pathlib import Path
import gitbolt

git = gitbolt.get_git()
git = git.git_envs_override(GIT_TRACE=1, GIT_DIR=Path('/tmp/git-dir/'), GIT_EDITOR='vim')
```

#### 🪢 Chain multiple overrides fluently

```python
from pathlib import Path
import gitbolt

git = gitbolt.get_git()
overridden_git = git.git_envs_override(GIT_SSH=Path('/tmp/SSH')).git_envs_override(
    GIT_TERMINAL_PROMPT=1,
    GIT_NO_REPLACE_OBJECTS=True
)
re_overridden_git = overridden_git.git_envs_override(GIT_TRACE=True)
```

#### ❌ Unset Git envs using a special `UNSET` marker

```python
import gitbolt
from vt.utils.commons.commons.core_py import UNSET

git = gitbolt.get_git()
overridden_git = git.git_envs_override(GIT_ADVICE=True, GIT_TRACE=True)
no_advice_unset_git = overridden_git.git_envs_override(GIT_TRACE=UNSET)
```

#### 🔄 Reset Git envs by setting new values

```python
import gitbolt

git = gitbolt.get_git()
overridden_git = git.git_envs_override(GIT_TRACE=True)
git_trace_reset_git = overridden_git.git_envs_override(GIT_TRACE=False)
```
</details>

---

<details>
<summary>Allow users to set/unset/reset git main command options in typed and pythonic manner just before subcommand run to provide maximal flexibility.</summary>

### ⚙️ Git Main Command Options

#### 🔁 Override a single Git opt (e.g., `--no-replace-objects`)

```python
import gitbolt

git = gitbolt.get_git()
git = git.git_opts_override(no_replace_objects=True)
```

#### 🌐 Override multiple options (e.g., `--git-dir`, `--paginate`)

```python
from pathlib import Path
from gitbolt.subprocess.impl.simple import SimpleGitCommand

git = SimpleGitCommand()
git = git.git_opts_override(no_replace_objects=True, git_dir=Path(), paginate=True)
```

#### 🪢 Chain multiple option overrides fluently

```python
import gitbolt
from pathlib import Path

git = gitbolt.get_git()
overridden_git = git.git_opts_override(exec_path=Path('tmp')).git_opts_override(
    noglob_pathspecs=True,
    no_advice=True
).git_opts_override(
    config_env={'auth': 'suhas', 'comm': 'suyog'}
)
re_overridden_git = overridden_git.git_opts_override(glob_pathspecs=True)
```

#### ❌ Unset Git opts using a special `UNSET` marker

```python
import gitbolt
from pathlib import Path
from vt.utils.commons.commons.core_py import UNSET

git = gitbolt.get_git()
overridden_git = git.git_opts_override(exec_path=Path('tmp'), no_advice=True)
no_advice_unset_git = overridden_git.git_opts_override(no_advice=UNSET)
```

#### 🔄 Reset Git opts by setting new values

```python
import gitbolt

git = gitbolt.get_git()
overridden_git = git.git_opts_override(no_advice=True)
no_advice_reset_git = overridden_git.git_opts_override(no_advice=False)
```

</details>

### 🔄 Run unchecked commands

At last, run unchecked commands in git.

Introduced in `0.0.0.dev4` to
- experiment.
- have consistent interfaced commands run until all subcommands are provided by the library.

#### 🖥️ Run one process per command

```python
import gitbolt

git = gitbolt.get_git_command()
git = git.git_opts_override(no_advice=True)
git.subcmd_unchecked.run(['--version']) # run the version option for git.
git.subcmd_unchecked.run(['version']) # run the version subcommand.
```

#### 🖥️ Run one long-running process and communicate with it

Introduced in `0.0.0.dev16` to:
- Make communicable processes using `subprocess.Popen`.

Get a long-running process and communicate with it for batching and faster operations.

```python
import gitbolt
import sys

git = gitbolt.get_git_command()
with git.subcmd_unchecked.popen(["cat-file", "--batch-command"]) as cf:
    cf.stdin.write(b"contents HEAD\n")
    cf.stdin.flush()
    header = cf.stdout.readline().strip()
    print(f"HEADER: {header}", file=sys.stderr)
    obj, typ, size = header.split()
    print(cf.stdout.read(int(size)))
    cf.stdout.readline()
```

Error handling and I/O management is left to the client/caller.

#### 🏃 Communicate with long-running git sessions

Introduced in `0.0.0.dev17` to:
- Make long-running git command sessions.
- Have reentrant sessions.
- Communicate with long-running git command session using their `stdin` and `stdout`.

Get long-running process sessions and communicate with them for batching and faster operations.

```python
import gitbolt
from gitbolt.subprocess.utils.session import cat_file_blob_content, cat_file_tree_data, cat_file_tree_content, \
    mktree_tree_make

git = gitbolt.get_git_command()
with git.session(
        cat_file1=["cat-file", "--batch"],
        cat_file2=["cat-file", "--batch"],
        cat_file3=lambda: git.subcmd_unchecked.popen(["cat-file", "--batch"]),  # pass your own git subcmd Popen(s)
        mktree=["mktree", "--batch", "-z"]
) as ses:   # reusable and reentrant session
    tree_data: list[bytes] = []
    for mode_, sha_, name_ in cat_file_tree_data(ses.commands.cat_file2, b"HEAD^{tree}"):
        print(mode_, sha_, name_)
    for tree_entry in cat_file_tree_content(ses.commands.cat_file2, b"HEAD^{tree}"):
        tree_data.append(tree_entry)
    print("+" * 40)
    print(cat_file_blob_content(ses.commands.cat_file3, b"9854cb4d432a881f59d38582791cf2636e7819d9"))
    print("~" * 40)
    with ses:  # is reentrant, if you want
        tree_hash = mktree_tree_make(ses.commands.mktree, b"\0".join(tree_data))    # make tree
        print("Obtained tree: ", tree_hash)

assert not ses.active  # session no long active
```

#### 💻 Run commands received from CLI

Introduced in `0.0.0.dev11` is the ability to take commands from CLI and run it inside `gitbolt`.

While making a system it may be required to run cli commands as received from cli using gitbolt. An obvious example
would be to make a system that receives CLI commands and does certain modifications/additions inside `gitbolt` before
actually running them. An example:

```python
import gitbolt

opts = ["--no-pager", "--namespace", "n1"]  # options received from outside your program.
envs = dict(GIT_AUTHOR_NAME="ss")  # env-vars received form outside your program.
git = gitbolt.get_git_command(opts=opts, envs=envs)

# these can later be overridden
git = git.git_opts_override(namespace="n2")
```

---

## 🔍 Transparent by Default

Output of git commands is returned as-is. No transformations unless explicitly requested.
Transformers for formatting/parsing can be added later.

---

## ✅ Benefits Out-of-the-Box

* 🔄 Composable Git commands.
* 📤 Returns raw stdout.
* 🚨 Exceptions with full context.
* 💤 Lazy execution.
* 🧠 Strong typing and compile-time guarantees.
* 🧼 Idiomatic Python.
* 🧪 Terminal subcommands.
* 💣 Fail-fast on invalid usage.

---

## 📄 More Information

- 📜 [License (Apache-2.0)](./LICENSE)
- 🤝 [Contributing Guide](./CONTRIBUTING.md)

---

## 🚧 Future Goals

* Support `pygit2` for direct, fast Git access.
* Enable `porcelain` support using `pygit2` where required.
  > `pygit2` usage will automatically make all commands return in porcelain mode.
