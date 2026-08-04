#!/usr/bin/env python3
# coding=utf-8

"""
Tests related to subprocess interfaces in gitbolt.
"""
import pytest
from pathlib import Path
from gitbolt.subprocess.constants import GIT_CMD
from gitbolt.subprocess.impl.simple import CLISimpleGitCommand, SimpleGitCommand


class TestStr:
    @pytest.mark.parametrize("git", [SimpleGitCommand(), CLISimpleGitCommand()])
    def test_str_of_git_only_class(self, git):
        assert str(git) == GIT_CMD

    def test_str_of_git_class(self):
        _a_git = CLISimpleGitCommand(opts=["-C", "a/b", "-C", "c/d", "--no-replace-objects"])
        assert str(_a_git) == f"{GIT_CMD} -C a/b -C c/d --no-replace-objects"
        _b_git = _a_git.git_opts_override(no_pager=True, literal_pathspecs=True)
        assert str(_b_git) == f"{GIT_CMD} -C a/b -C c/d --no-replace-objects --no-pager --literal-pathspecs"

    @pytest.mark.parametrize("git", [SimpleGitCommand(), CLISimpleGitCommand(opts=["-C", "i", "-C", "see/you"])])
    def test_str_cleans_cap_c_from_git_args(self, git):
        _a_git = git.git_opts_override(C=[Path("a"), Path("b"), Path("cd")])
        assert str(_a_git) == f"{GIT_CMD} -C a -C b -C cd"

    def test_str_cleans_cap_c_from_git_args_cli(self):
        git = CLISimpleGitCommand(opts=["-C", "i", "-C", "see/you"])
        _a_git = git.git_opts_override(C=[Path("a"), Path("b"), Path("cd")])
        assert str(_a_git) == f"{GIT_CMD} -C a -C b -C cd"

    @pytest.mark.parametrize("prefer_cli", [True, False])
    class TestCLISimpleGitCommand:
        """
        Test CLI subpart of the git command interface.
        """
        def test_no_cli_opts_provided(self, prefer_cli):
            """
            Simple ``git`` must be the output of str when no CLI options are provided.
            """
            git = CLISimpleGitCommand(prefer_cli=prefer_cli)
            assert str(git) == GIT_CMD

        def test_cli_opts_provided_no_cap_c(self, prefer_cli):
            """
            No Capital C or ``-C`` is provided on CLI and no override is performed.
            """
            git = CLISimpleGitCommand(opts=["--no-replace-objects", "--no-pager", "--config-env",
                                            "conf.dir=my-dir"], prefer_cli=prefer_cli)
            assert str(git) == f"{GIT_CMD} --no-replace-objects --no-pager --config-env conf.dir=my-dir"

        def test_cli_opts_provided_with_cap_c(self, prefer_cli):
            """
            Capital C or ``-C`` is provided on CLI and no override is performed.
            """
            git = CLISimpleGitCommand(opts=["--no-replace-objects", "-C", "a/b","--no-pager", "--config-env",
                                            "conf.dir=my-dir", "-C", "c/d/e"], prefer_cli=prefer_cli)
            assert str(git) == (f"{GIT_CMD} --no-replace-objects -C a/b --no-pager --config-env conf.dir=my-dir "
                                f"-C c/d/e")

        def test_cli_opts_provided_with_cap_c_and_envs(self, prefer_cli):
            """
            Capital C or ``-C`` is provided on CLI and no override is performed.
            """
            git = CLISimpleGitCommand(opts=["--no-replace-objects", "-C", "a/b","--no-pager", "--config-env",
                                            "conf.dir=my-dir", "-C", "c/d/e"],
                                      envs=dict(GIT_AUTHOR_NAME="ss", GIT_TRACE="true"),
                                      prefer_cli=prefer_cli)
            assert str(git) == (f"GIT_AUTHOR_NAME=ss GIT_TRACE=true {GIT_CMD} --no-replace-objects -C a/b "
                                f"--no-pager --config-env conf.dir=my-dir -C c/d/e")

    class TestPreferCLI:
        """
        Test CLI subpart when prefer cli is enabled.
        """
        def test_supplied_opts_cap_c_not_affected_on_non_cap_c_override(self):
            """
            -C is supplied in the CLI options and is not overridden but the options are not affected on str computation.
            Also, CLI options appear later in the string.
            """
            git = CLISimpleGitCommand(opts=["--no-replace-objects", "-C", "a/b","--no-pager", "--config-env",
                                            "conf.dir=my-dir", "-C", "c/d/e"], prefer_cli=True)
            assert str(git) == (f"{GIT_CMD} --no-replace-objects -C a/b --no-pager --config-env conf.dir=my-dir "
                                f"-C c/d/e")
            _a_git = git.git_opts_override(no_lazy_fetch=True, attr_source="some-src")
            assert str(_a_git) == (f"{GIT_CMD} --no-lazy-fetch --attr-source some-src --no-replace-objects -C a/b "
                                f"--no-pager --config-env conf.dir=my-dir -C c/d/e")

        def test_supplied_opts_cap_c_not_affected_on_cap_c_override(self):
            """
            -C is supplied in the CLI options and is overridden but the options are not affected on str computation.
            Also, CLI options appear later in the string.
            """
            git = CLISimpleGitCommand(opts=["--no-replace-objects", "-C", "a/b","--no-pager", "--config-env",
                                            "conf.dir=my-dir", "-C", "c/d/e"], prefer_cli=True)
            assert str(git) == (f"{GIT_CMD} --no-replace-objects -C a/b --no-pager --config-env conf.dir=my-dir "
                                f"-C c/d/e")
            _a_git = git.git_opts_override(C=[Path("my"), Path("other", "dir"), Path("file")],
                                           no_lazy_fetch=True, attr_source="some-src")
            assert str(_a_git) == (f"{GIT_CMD} --no-lazy-fetch --attr-source some-src --no-replace-objects -C a/b "
                                f"--no-pager --config-env conf.dir=my-dir -C c/d/e")

    class TestNoPreferCLI:
        """
        Test CLI subpart when prefer cli is disabled.
        """
        def test_supplied_opts_cap_c_not_affected_on_non_cap_c_override(self):
            """
            -C is supplied in the CLI options and is not overridden but the options are not affected on str computation.
            Also, supplied CLI options appear before in the string.
            """
            git = CLISimpleGitCommand(opts=["--no-replace-objects", "-C", "a/b","--no-pager", "--config-env",
                                            "conf.dir=my-dir", "-C", "c/d/e"])
            assert str(git) == (f"{GIT_CMD} --no-replace-objects -C a/b --no-pager --config-env conf.dir=my-dir "
                                f"-C c/d/e")
            _a_git = git.git_opts_override(no_lazy_fetch=True, attr_source="some-src")
            assert str(_a_git) == (f"{GIT_CMD} --no-replace-objects -C a/b --no-pager --config-env conf.dir=my-dir "
                                   f"-C c/d/e --no-lazy-fetch --attr-source some-src")

        def test_supplied_opts_cap_c_not_affected_on_cap_c_override(self):
            """
            -C is supplied in the CLI options and is overridden thus the options are affected on str computation.
            Also, supplied CLI options appear before in the string.
            """
            git = CLISimpleGitCommand(opts=["--no-replace-objects", "-C", "a/b","--no-pager", "--config-env",
                                            "conf.dir=my-dir", "-C", "c/d/e"])
            assert str(git) == (f"{GIT_CMD} --no-replace-objects -C a/b --no-pager --config-env conf.dir=my-dir "
                                f"-C c/d/e")
            _a_git = git.git_opts_override(C=[Path("my"), Path("other", "dir"), Path("file")],
                                           no_lazy_fetch=True, attr_source="some-src")
            assert str(_a_git) == (f"{GIT_CMD} --no-replace-objects --no-pager --config-env conf.dir=my-dir "
                                   f"-C my -C {Path("other", "dir")} -C file --no-lazy-fetch --attr-source "
                                   f"some-src")

        def test_supplied_opts_cap_c_not_affected_on_cap_c_override_with_envs(self):
            """
            -C is supplied in the CLI options and is overridden thus the options are affected on str computation.
            Also, supplied CLI options appear before in the string.

            Introducing envs in the mix.
            """
            git = CLISimpleGitCommand(opts=["--no-replace-objects", "-C", "a/b","--no-pager", "--config-env",
                                            "conf.dir=my-dir", "-C", "c/d/e"])
            assert str(git) == (f"{GIT_CMD} --no-replace-objects -C a/b --no-pager --config-env conf.dir=my-dir "
                                f"-C c/d/e")
            _a_git = git.git_opts_override(C=[Path("my"), Path("other", "dir"), Path("file")],
                                           no_lazy_fetch=True,
                                           attr_source="some-src").git_envs_override(GIT_ADVICE=False,
                                                                                     GIT_HTTP_USER_AGENT="https-agent")
            assert str(_a_git) == (f"GIT_ADVICE=False GIT_HTTP_USER_AGENT=https-agent {GIT_CMD} --no-replace-objects "
                                   f"--no-pager --config-env conf.dir=my-dir -C my -C {Path("other", "dir")} "
                                   f"-C file --no-lazy-fetch --attr-source some-src")
