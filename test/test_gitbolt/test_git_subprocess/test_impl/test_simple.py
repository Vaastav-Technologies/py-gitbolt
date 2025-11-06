#!/usr/bin/env python3
# coding=utf-8

"""
Tests for Git command interfaces with default implementation using subprocess calls.
"""

from pathlib import Path

import pytest
from vt.utils.commons.commons.core_py import UNSET
from vt.utils.errors.error_specs import ERR_DATA_FORMAT_ERR, ERR_INVALID_USAGE

from gitbolt.exceptions import GitExitingException
from gitbolt.git_subprocess.impl.simple import SimpleGitCommand, CLISimpleGitCommand


def test_exec_path():
    git = SimpleGitCommand()
    assert isinstance(git.exec_path, Path)


def test_overrides_and_exec_path():
    git = SimpleGitCommand()
    assert git.git_opts_override(exec_path=None).exec_path is not None

@pytest.mark.parametrize("git", [SimpleGitCommand(), CLISimpleGitCommand()])
class TestMainGit:
    class TestMainCmdOverrides:
        class TestSupplied:
            class TestSameCall:
                def test_one_supplied(self, git):
                    assert ["--no-replace-objects"] == git.git_opts_override(
                        no_replace_objects=True
                    ).build_main_cmd_args()

                def test_multiple_supplied(self, git):
                    assert git.git_opts_override(
                        no_replace_objects=True, git_dir=Path(), paginate=True
                    ).build_main_cmd_args() == [
                        "--paginate",
                        "--git-dir",
                        ".",
                        "--no-replace-objects",
                    ]

        class TestMultipleCalls:
            def test_one_supplied(self, git):
                assert git.git_opts_override().git_opts_override(
                    exec_path=Path("tmp")
                ).git_opts_override(noglob_pathspecs=True).build_main_cmd_args() == [
                    "--exec-path",
                    "tmp",
                    "--noglob-pathspecs",
                ]

            def test_multiple_supplied(self, git):
                assert git.git_opts_override(exec_path=Path("tmp")).git_opts_override(
                    noglob_pathspecs=True, no_advice=True
                ).git_opts_override(
                    config_env={"auth": "suhas", "comm": "suyog"}
                ).build_main_cmd_args() == [
                    "--config-env",
                    "auth=suhas",
                    "--config-env",
                    "comm=suyog",
                    "--exec-path",
                    "tmp",
                    "--no-advice",
                    "--noglob-pathspecs",
                ]

        class TestOverrideValues:
            def test_unset_value_alone(self, git):
                """
                only --exec-path is set in first ``git_opts_override()`` call and is unset in next ``git_opts_override()`` call.
                """
                assert (
                    git.git_opts_override(exec_path=Path("tmp"))
                    .git_opts_override(exec_path=UNSET)
                    .build_main_cmd_args()
                    == []
                )

            def test_unset_value_defined_with_others(self, git):
                """
                -C and --exec-path is set in first ``git_opts_override()`` call and is unset in next ``git_opts_override()`` call.
                """
                assert git.git_opts_override(
                    exec_path=Path("tmp"), C=[Path()]
                ).git_opts_override(exec_path=UNSET).build_main_cmd_args() == ["-C", "."]

            class TestMultipleCalls:
                def test_unset_value_on_last_call(self, git):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in last ``git_opts_override()`` call.
                    """
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(exec_path=UNSET).build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                    ]

                def test_unset_value_on_non_last_call(self, git):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in next ``git_opts_override()`` call.
                    * --no-replace-objects is set in last ``git_opts_override()`` call.
                    """
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(exec_path=UNSET).git_opts_override(
                        no_replace_objects=True
                    ).build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                        "--no-replace-objects",
                    ]

                def test_no_value_on_non_last_call(self, git):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in next ``git_opts_override()`` call.
                    * no value given to last ``git_opts_override()`` call.
                    """
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(
                        exec_path=UNSET
                    ).git_opts_override().build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                    ]

                def test_re_set_value_on_non_last_call(self, git):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in next ``git_opts_override()`` call.
                    * --no-replace-objects is set in last ``git_opts_override()`` call.
                    """
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(exec_path=UNSET).git_opts_override(
                        exec_path=Path()
                    ).build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                        "--exec-path",
                        ".",
                    ]

        class TestIndividualMethods:
            class TestSmallC:
                @pytest.mark.parametrize(
                    "input_dict,expected",
                    [
                        # Simple key-value
                        ({"foo.bar": "baz"}, ["-c", "foo.bar=baz"]),
                        # Empty string value
                        ({"foo.bar": ""}, ["-c", "foo.bar="]),
                        # Boolean True (no equals sign)
                        ({"foo.bar": True}, ["-c", "foo.bar"]),
                        # Boolean False (explicit empty string)
                        ({"foo.bar": False}, ["-c", "foo.bar="]),
                        # None (treated as True)
                        ({"foo.bar": None}, ["-c", "foo.bar"]),
                        # Mixed values
                        (
                            {"a.b": "x", "c.d": "", "e.f": True, "g.h": False, "i.j": None},
                            [
                                "-c",
                                "a.b=x",
                                "-c",
                                "c.d=",
                                "-c",
                                "e.f",
                                "-c",
                                "g.h=",
                                "-c",
                                "i.j",
                            ],
                        ),
                        # Empty config (no args)
                        ({}, []),
                        # c is None
                        (None, []),
                        # c is UNSET
                        (UNSET, []),
                        # Missing key
                        ({}, []),
                        # UNSET should remove the key
                        ({"foo.bar": "value", "bar.baz": UNSET}, ["-c", "foo.bar=value"]),
                        # All keys are unset
                        ({"foo.bar": UNSET}, []),
                        # Mixed unset, true, false
                        (
                            {"a.b": UNSET, "b.c": True, "c.d": False},
                            ["-c", "b.c", "-c", "c.d="],
                        ),
                    ],
                )
                def test_main_cmd_c_args(self, git, input_dict, expected):
                    git = git.git_opts_override(c=input_dict)
                    assert git._main_cmd_small_c_args() == expected


    class TestEnvOverrides:
        class TestSupplied:
            class TestSameCall:
                def test_one_supplied(self, git):
                    assert git.git_envs_override(GIT_TRACE=True).build_git_envs() == {
                        "GIT_TRACE": "True"
                    }

                def test_multiple_supplied(self, git):
                    assert git.git_envs_override(
                        GIT_TRACE=1, GIT_DIR=Path("/tmp/git-dir/"), GIT_EDITOR="vim"
                    ).build_git_envs() == {
                        "GIT_TRACE": "1",
                        "GIT_DIR": str(Path("/tmp/git-dir")),
                        "GIT_EDITOR": "vim",
                    }

                class TestMainOptMixed:
                    def test_one_supplied_main_opts_last_call(self, git):
                        assert git.git_envs_override(GIT_TRACE=True).git_opts_override(
                            no_pager=True
                        ).build_git_envs() == {"GIT_TRACE": "True"}

                    def test_one_supplied_main_opts_non_last_call(self, git):
                        assert git.git_opts_override(no_pager=True).git_envs_override(
                            GIT_TRACE=True
                        ).build_git_envs() == {"GIT_TRACE": "True"}

                    def test_multiple_supplied_main_opts_first(self, git):
                        assert git.git_opts_override(no_advice=True).git_envs_override(
                            GIT_TRACE=1, GIT_DIR=Path("/tmp/git-dir/"), GIT_EDITOR="vim"
                        ).build_git_envs() == {
                            "GIT_TRACE": "1",
                            "GIT_DIR": str(Path("/tmp/git-dir")),
                            "GIT_EDITOR": "vim",
                        }

                    def test_multiple_supplied_main_opts_last(self, git):
                        assert git.git_envs_override(
                            GIT_TRACE=1, GIT_DIR=Path("/tmp/git-dir/"), GIT_EDITOR="vim"
                        ).git_opts_override(no_advice=True).build_git_envs() == {
                            "GIT_TRACE": "1",
                            "GIT_DIR": str(Path("/tmp/git-dir")),
                            "GIT_EDITOR": "vim",
                        }

        class TestMultipleCalls:
            def test_one_supplied(self, git):
                assert git.git_envs_override().git_envs_override(
                    GIT_TRACE_SETUP=2
                ).git_envs_override().build_git_envs() == {"GIT_TRACE_SETUP": "2"}

            def test_one_supplied_more_calls(self, git):
                assert git.git_envs_override().git_envs_override(
                    GIT_TRACE_SETUP=2
                ).git_envs_override(GIT_ADVICE=False).build_git_envs() == {
                    "GIT_TRACE_SETUP": "2",
                    "GIT_ADVICE": "False",
                }

            def test_multiple_supplied(self, git):
                assert git.git_envs_override(GIT_SSH=Path("/tmp/SSH")).git_envs_override(
                    GIT_TERMINAL_PROMPT=1, GIT_NO_REPLACE_OBJECTS=True
                ).git_envs_override(
                    GIT_ALTERNATE_OBJECT_DIRECTORIES=Path("/tmp/alter")
                ).build_git_envs() == {
                    "GIT_SSH": str(Path("/tmp/SSH")),
                    "GIT_TERMINAL_PROMPT": "1",
                    "GIT_NO_REPLACE_OBJECTS": "True",
                    "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(Path("/tmp/alter")),
                }

            class TestMainOptsMixed:
                def test_one_supplied(self, git):
                    assert git.git_envs_override().git_opts_override().git_envs_override(
                        GIT_TRACE_SETUP=2
                    ).git_envs_override().git_opts_override(
                        noglob_pathspecs=True, icase_pathspecs=False
                    ).build_git_envs() == {"GIT_TRACE_SETUP": "2"}

                def test_one_supplied_more_calls(self, git):
                    assert git.git_envs_override().git_opts_override(
                        exec_path=Path("/tmp/git-dir")
                    ).git_envs_override(GIT_TRACE_SETUP=2).git_envs_override(
                        GIT_ADVICE=False
                    ).git_opts_override(
                        noglob_pathspecs=True, icase_pathspecs=False
                    ).build_git_envs() == {"GIT_TRACE_SETUP": "2", "GIT_ADVICE": "False"}

                def test_multiple_supplied(self, git):
                    assert git.git_envs_override(
                        GIT_SSH=Path("/tmp/SSH")
                    ).git_opts_override(exec_path=Path("/tmp/git-dir")).git_envs_override(
                        GIT_TERMINAL_PROMPT=1, GIT_NO_REPLACE_OBJECTS=True
                    ).git_envs_override(
                        GIT_ALTERNATE_OBJECT_DIRECTORIES=Path("/tmp/alter")
                    ).build_git_envs() == {
                        "GIT_SSH": str(Path("/tmp/SSH")),
                        "GIT_TERMINAL_PROMPT": "1",
                        "GIT_NO_REPLACE_OBJECTS": "True",
                        "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(Path("/tmp/alter")),
                    }

        class TestOverrideValues:
            def test_unset_value_alone(self, git):
                """
                only GIT_DIR is set in first ``git_envs_override()`` call and is unset in next ``git_envs_override()`` call.
                """
                assert (
                    git.git_envs_override(GIT_DIR=Path("tmp"))
                    .git_envs_override(GIT_DIR=UNSET)
                    .build_git_envs()
                    == {}
                )

            def test_unset_value_defined_with_others(self, git):
                """
                GIT_DIR and GIT_ADVICE is set in first ``git_envs_override()`` call and is unset in next ``git_envs_override()`` call.
                """
                assert git.git_envs_override(
                    GIT_DIR=Path("tmp"), GIT_TRACE=2, GIT_ADVICE=0
                ).git_envs_override(GIT_DIR=UNSET).build_git_envs() == {
                    "GIT_TRACE": "2",
                    "GIT_ADVICE": "0",
                }

            class TestMultipleCalls:
                def test_unset_value_on_last_call(self, git):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in last ``git_opts_override()`` call.
                    """
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(exec_path=UNSET).build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                    ]

                def test_unset_value_on_non_last_call(self, git):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in next ``git_opts_override()`` call.
                    * --no-replace-objects is set in last ``git_opts_override()`` call.
                    """
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(exec_path=UNSET).git_opts_override(
                        no_replace_objects=True
                    ).build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                        "--no-replace-objects",
                    ]

                def test_no_value_on_non_last_call(self, git):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in next ``git_opts_override()`` call.
                    * no value given to last ``git_opts_override()`` call.
                    """
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(
                        exec_path=UNSET
                    ).git_opts_override().build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                    ]

                def test_re_set_value_on_non_last_call(self, git):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in next ``git_opts_override()`` call.
                    * --no-replace-objects is set in last ``git_opts_override()`` call.
                    """
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(exec_path=UNSET).git_opts_override(
                        exec_path=Path()
                    ).build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                        "--exec-path",
                        ".",
                    ]

        class TestIndividualMethods:
            class TestSmallC:
                @pytest.mark.parametrize(
                    "input_dict,expected",
                    [
                        # Simple key-value
                        ({"foo.bar": "baz"}, ["-c", "foo.bar=baz"]),
                        # Empty string value
                        ({"foo.bar": ""}, ["-c", "foo.bar="]),
                        # Boolean True (no equals sign)
                        ({"foo.bar": True}, ["-c", "foo.bar"]),
                        # Boolean False (explicit empty string)
                        ({"foo.bar": False}, ["-c", "foo.bar="]),
                        # None (treated as True)
                        ({"foo.bar": None}, ["-c", "foo.bar"]),
                        # Mixed values
                        (
                            {"a.b": "x", "c.d": "", "e.f": True, "g.h": False, "i.j": None},
                            [
                                "-c",
                                "a.b=x",
                                "-c",
                                "c.d=",
                                "-c",
                                "e.f",
                                "-c",
                                "g.h=",
                                "-c",
                                "i.j",
                            ],
                        ),
                        # Empty config (no args)
                        ({}, []),
                        # c is None
                        (None, []),
                        # c is UNSET
                        (UNSET, []),
                        # Missing key
                        ({}, []),
                        # UNSET should remove the key
                        ({"foo.bar": "value", "bar.baz": UNSET}, ["-c", "foo.bar=value"]),
                        # All keys are unset
                        ({"foo.bar": UNSET}, []),
                        # Mixed unset, true, false
                        (
                            {"a.b": UNSET, "b.c": True, "c.d": False},
                            ["-c", "b.c", "-c", "c.d="],
                        ),
                    ],
                )
                def test_main_cmd_c_args(self, git, input_dict, expected):
                    git = git.git_opts_override(c=input_dict)
                    assert git._main_cmd_small_c_args() == expected


    class TestOptsEnvMixedOverrides:
        class TestNoOverrides:
            def test_leaves_envs_empty(self, git):
                assert git._env_vars == {}

            def test_leaves_opts_empty(self, git):
                assert git._main_cmd_opts == {}

        class TestOverridingPropDoesNotAffectParentProps:
            """
            Overriding properties using *_override() methods do not change the properties of the objects which they've
            overridden, instead a new object with the overridden properties is returned.
            """

            class TestEnvs:
                def test_once(self, git):
                    envs_o_git = git.git_envs_override(
                        GIT_AUTHOR_NAME="ss", GIT_OBJECT_DIRECTORY=Path("/tmp/obj-dir/")
                    )
                    assert (
                        git._env_vars == {}
                    )  # parent ``git`` object protected properties still empty.
                    assert envs_o_git._env_vars == {
                        "GIT_AUTHOR_NAME": "ss",
                        "GIT_OBJECT_DIRECTORY": Path("/tmp/obj-dir/"),
                    }

                def test_twice(self, git):
                    envs_o_git = git.git_envs_override(
                        GIT_AUTHOR_NAME="ss", GIT_OBJECT_DIRECTORY=Path("/tmp/obj-dir/")
                    )
                    envs_o_o_git = envs_o_git.git_envs_override(GIT_SSH_COMMAND="gpg")
                    assert (
                        git._env_vars == {}
                    )  # ancestor ``git`` object protected properties still empty.
                    assert envs_o_git._env_vars == {
                        "GIT_AUTHOR_NAME": "ss",
                        "GIT_OBJECT_DIRECTORY": Path("/tmp/obj-dir/"),
                    }  # parent git protected properties still not overridden
                    assert envs_o_o_git._env_vars == {
                        "GIT_AUTHOR_NAME": "ss",
                        "GIT_OBJECT_DIRECTORY": Path("/tmp/obj-dir/"),
                        "GIT_SSH_COMMAND": "gpg",
                    }  # new property added in child object

            class TestOpts:
                def test_once(self, git):
                    main_o_git = git.git_opts_override(
                        namespace="ss", git_dir=Path("/tmp/git-dir/.git")
                    )
                    assert (
                        git._main_cmd_opts == {}
                    )  # parent ``git`` object protected properties still empty.
                    assert main_o_git._main_cmd_opts == {
                        "namespace": "ss",
                        "git_dir": Path("/tmp/git-dir/.git"),
                    }

                def test_twice(self, git):
                    main_o_git = git.git_opts_override(
                        namespace="ss", git_dir=Path("/tmp/git-dir/.git")
                    )
                    main_o_o_git = main_o_git.git_opts_override(paginate=True)
                    assert (
                        git._main_cmd_opts == {}
                    )  # ancestor ``git`` object protected properties still empty.
                    assert main_o_git._main_cmd_opts == {
                        "namespace": "ss",
                        "git_dir": Path("/tmp/git-dir/.git"),
                    }  # parent git protected properties still not overridden
                    assert main_o_o_git._main_cmd_opts == {
                        "namespace": "ss",
                        "git_dir": Path("/tmp/git-dir/.git"),
                        "paginate": True,
                    }  # new property added in child object

        class TestOverridingOneDoesNotAffectOther:
            def test_override_envs(self, git):
                envs_o_git = git.git_envs_override(
                    GIT_AUTHOR_NAME="ss", GIT_OBJECT_DIRECTORY=Path("/tmp/obj-dir/")
                )
                assert (
                    git._main_cmd_opts == {}
                )  # overriding envs didn't override main-opts in parent
                assert (
                    envs_o_git._main_cmd_opts == {}
                )  # overriding envs didn't override main-opts

            def test_override_opts(self, git):
                main_o_git = git.git_opts_override(
                    namespace="ss", git_dir=Path("/tmp/git-dir/.git")
                )
                assert git._env_vars == {}  # overriding opts didn't override envs in parent
                assert main_o_git._env_vars == {}  # overriding opts didn't override envs


# TODO: this goes into vt-commons (maybe in cli package).
def _adjust_opts(opts: list[str], prefer_overriding: bool, overriding_opts: list[str]) -> list[str]:
    """
    Position ``overriding_opts`` after ``opts`` in the returned list when prefer_overriding is ``True``.

    Position ``overriding_opts`` before ``opts`` in the returned list when prefer_overriding is ``False``.

    >>> _adjust_opts(["a", "b"], True, ["c", "d"])
    ['a', 'b', 'c', 'd']

    >>> _adjust_opts(["a", "b"], False, ["c", "d"])
    ['c', 'd', 'a', 'b']

    :param opts: options to adjust according to ``prefer_cli``.
    :param prefer_overriding: positions ``overriding_opts`` after (when ``True``) or before (when ``False``) ``opts``.
    :param overriding_opts: options that will be positioned before or after ``opts``.
    :returns: options with appropriate ordering of ``opts`` and ``overriding_opts`` according to ``prefer_cli``.
    """
    if prefer_overriding:
        opts = overriding_opts + opts
    else:
        opts.extend(overriding_opts)
    return opts


# TODO: complete all the test cases for CLISimpleGitCommand
class TestMainCLIGit:
    """
    Test for ``CLISimpleGitCommand``.
    """
    class TestOnlyCtorCall:
        """
        Tests where the values are directly and exclusively set on ctor and no other setting operation is performed
        after that.
        """

        class TestNoArg:
            def test_opts(self):
                git = CLISimpleGitCommand()
                assert [] == git.build_main_cmd_args()

            def test_envs(self):
                git = CLISimpleGitCommand()
                assert {} == git.build_git_envs()

        @pytest.mark.parametrize("opts", [
            None,
            [],
            ["--no-replace-objects"],
            ["--paginate", "--git-dir", ".", "--no-replace-objects"],
            ["--"]
        ])
        def test_opts(self, opts):
            git = CLISimpleGitCommand(opts=opts)
            opts = opts or []   # just for opts=None case
            assert git.build_main_cmd_args() == opts

        @pytest.mark.parametrize("envs", [
            None,
            {},
            {"GIT_AUTHOR_NAME": "ss"},
            {"GIT_EDITOR": "vi", "GIT_SSH": "/ssh/home/.ssh", "GIT_TRACE": "1"},
            {"GIT_TERMINAL_PROMPT": "0", "GNUPGHOME": "/tmp/path"},
        ])
        def test_envs(self, envs: dict[str, str]):
            git = CLISimpleGitCommand(envs=envs)
            envs = envs or {}   # just for envs=None case
            assert git.build_git_envs() == envs

        @pytest.mark.parametrize("opts, envs", [
            (None, None),
            ([], {}),
            ([], {"GIT_COMMITTER_NAME": "ss"}),
            ([], {"SSH_HOME": "/ssh/path", "GIT_COMMITTER_NAME": "ss"}),
            (["--no-pager", "--no-replace-objects"], {"SSH_HOME": "/ssh/path", "GIT_COMMITTER_NAME": "ss"}),
            (["--namespace", "n1", "--paginate"], {}),
            (["--config-env", "env1=val1", "--config-env", "env2=val2", "--no-replace-objects"], None),
        ])
        def test_opts_and_envs(self, opts: list[str], envs: dict[str, str]):
            git = CLISimpleGitCommand(opts=opts, envs=envs)
            opts = opts or []
            envs = envs or {}
            assert git.build_git_envs() == envs
            assert git.build_main_cmd_args() == opts

    class TestMainCmdOverrides:
        """
        Tests for programmatically overriding user supplied cli git opts.
        """

        @pytest.mark.parametrize("opts", [
            [],
            ["--no-replace-objects"],
            ["--paginate", "--git-dir", ".", "--no-replace-objects"],
            ["-c", "p1=v1", "-c", "p2=v2"]
        ])
        @pytest.mark.parametrize("prefer_cli", [True, False])
        class TestNonOverriding:
            class TestSingleCall:
                def test_single_supplied(self, opts: list[str], prefer_cli: bool):
                    git = CLISimpleGitCommand(opts=opts.copy(), prefer_cli=prefer_cli).git_opts_override(C=[Path()])
                    overriding_opts = ["-C", str(Path())]
                    opts = _adjust_opts(opts, prefer_cli, overriding_opts)
                    assert git.build_main_cmd_args() == opts

                def test_multiple_supplied(self, opts: list[str], prefer_cli: bool):
                    git = CLISimpleGitCommand(opts=opts.copy(),
                                              prefer_cli=prefer_cli).git_opts_override(namespace="n1", exec_path=Path(),
                                                                                    c=dict(p3="v3", p4="v4v5"))
                    overriding_opts = ['-c', 'p3=v3', '-c', 'p4=v4v5', '--exec-path', '.', '--namespace', 'n1']
                    opts = _adjust_opts(opts, prefer_cli, overriding_opts)
                    assert git.build_main_cmd_args() == opts

            class TestMultipleCalls:
                def test_one_supplied(self, opts: list[str], prefer_cli: bool):
                    git = CLISimpleGitCommand(opts=opts.copy(), prefer_cli=prefer_cli)
                    overriding_opts = ["--exec-path", "tmp", "--noglob-pathspecs",]
                    opts = _adjust_opts(opts, prefer_cli, overriding_opts)
                    assert git.git_opts_override().git_opts_override(
                        exec_path=Path("tmp")
                    ).git_opts_override(noglob_pathspecs=True).build_main_cmd_args() == opts

                def test_multiple_supplied(self, opts: list[str], prefer_cli: bool):
                    git = CLISimpleGitCommand(opts=opts.copy(), prefer_cli=prefer_cli)
                    overriding_opts = [
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                        "--exec-path",
                        "tmp",
                        "--no-advice",
                        "--noglob-pathspecs",
                    ]
                    opts = _adjust_opts(opts, prefer_cli, overriding_opts)
                    assert git.git_opts_override(exec_path=Path("tmp")).git_opts_override(
                        noglob_pathspecs=True, no_advice=True
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).build_main_cmd_args() == opts

            def test_intermixed(self, opts: list[str], prefer_cli: bool):
                git = CLISimpleGitCommand(opts=opts.copy(), prefer_cli=prefer_cli)
                overriding_opts = [
                    "--config-env",
                    "auth=suhas",
                    "--config-env",
                    "comm=suyog",
                    "--exec-path",
                    "tmp",
                    "--no-pager",
                    "--no-advice",
                    "--noglob-pathspecs",
                ]
                opts = _adjust_opts(opts, prefer_cli, overriding_opts)
                assert git.git_opts_override(exec_path=Path("tmp")).git_opts_override(
                    noglob_pathspecs=True, no_advice=True
                ).git_opts_override(
                    config_env={"auth": "suhas", "comm": "suyog"}
                ).git_opts_override(no_pager=True).build_main_cmd_args() == opts

        class TestOverrideValues:
            def test_unset_value_alone(self):
                """
                only --exec-path is set in first ``git_opts_override()`` call and is unset in next ``git_opts_override()`` call.
                """
                git = CLISimpleGitCommand(opts=["--no-pager"])
                assert (
                    git.git_opts_override(exec_path=Path("tmp"))
                    .git_opts_override(exec_path=UNSET)
                    .build_main_cmd_args()
                    == ["--no-pager"]
                )

            def test_override_conflicting_value_alone(self):
                """
                only --exec-path is set in first ``git_opts_override()`` call and is unset in next ``git_opts_override()`` call
                but is set from before in the ctor.
                """
                opts = ["--exec-path", str(Path("tmp", "exec"))]
                git = CLISimpleGitCommand(opts=opts.copy())
                assert (
                    git.git_opts_override(exec_path=Path("tmp"))
                    .git_opts_override(exec_path=UNSET)
                    .build_main_cmd_args()
                    == opts
                )

            @pytest.mark.parametrize("prefer_cli", [True, False])
            def test_unset_value_defined_with_others(self, prefer_cli):
                """
                -C and --exec-path is set in first ``git_opts_override()`` call and is unset in next ``git_opts_override()`` call.
                """
                opts = ["--no-pager"]
                git = CLISimpleGitCommand(opts=["--no-pager"], prefer_cli=prefer_cli)
                opts = _adjust_opts(opts, prefer_cli, ["-C", str(Path("."))])
                assert git.git_opts_override(
                    exec_path=Path("tmp"), C=[Path()]
                ).git_opts_override(exec_path=UNSET).build_main_cmd_args() == opts

            @pytest.mark.parametrize("prefer_cli", [True, False])
            def test_override_conflicting_value_defined_with_others(self, prefer_cli):
                """
                -C and --exec-path is set in first ``git_opts_override()`` call and is unset in next ``git_opts_override()`` call
                but is set from before in the ctor.
                """
                opts = ["--exec-path", str(Path("tmp", "exec"))]
                git = CLISimpleGitCommand(opts=opts.copy(), prefer_cli=prefer_cli)
                opts = _adjust_opts(opts, prefer_cli, ["-C", str(Path("."))])
                assert git.git_opts_override(
                    exec_path=Path("tmp"), C=[Path()]
                ).git_opts_override(exec_path=UNSET).build_main_cmd_args() == opts

            class TestMultipleCalls:
                def test_unset_value_on_last_call(self):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in last ``git_opts_override()`` call.
                    """
                    git = SimpleGitCommand()
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(exec_path=UNSET).build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                    ]

                def test_unset_value_on_non_last_call(self):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in next ``git_opts_override()`` call.
                    * --no-replace-objects is set in last ``git_opts_override()`` call.
                    """
                    git = SimpleGitCommand()
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(exec_path=UNSET).git_opts_override(
                        no_replace_objects=True
                    ).build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                        "--no-replace-objects",
                    ]

                def test_no_value_on_non_last_call(self):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in next ``git_opts_override()`` call.
                    * no value given to last ``git_opts_override()`` call.
                    """
                    git = SimpleGitCommand()
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(
                        exec_path=UNSET
                    ).git_opts_override().build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                    ]

                def test_re_set_value_on_non_last_call(self):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in next ``git_opts_override()`` call.
                    * --no-replace-objects is set in last ``git_opts_override()`` call.
                    """
                    git = SimpleGitCommand()
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(exec_path=UNSET).git_opts_override(
                        exec_path=Path()
                    ).build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                        "--exec-path",
                        ".",
                    ]

        class TestIndividualMethods:
            class TestSmallC:
                @pytest.mark.parametrize(
                    "input_dict,expected",
                    [
                        # Simple key-value
                        ({"foo.bar": "baz"}, ["-c", "foo.bar=baz"]),
                        # Empty string value
                        ({"foo.bar": ""}, ["-c", "foo.bar="]),
                        # Boolean True (no equals sign)
                        ({"foo.bar": True}, ["-c", "foo.bar"]),
                        # Boolean False (explicit empty string)
                        ({"foo.bar": False}, ["-c", "foo.bar="]),
                        # None (treated as True)
                        ({"foo.bar": None}, ["-c", "foo.bar"]),
                        # Mixed values
                        (
                            {"a.b": "x", "c.d": "", "e.f": True, "g.h": False, "i.j": None},
                            [
                                "-c",
                                "a.b=x",
                                "-c",
                                "c.d=",
                                "-c",
                                "e.f",
                                "-c",
                                "g.h=",
                                "-c",
                                "i.j",
                            ],
                        ),
                        # Empty config (no args)
                        ({}, []),
                        # c is None
                        (None, []),
                        # c is UNSET
                        (UNSET, []),
                        # Missing key
                        ({}, []),
                        # UNSET should remove the key
                        ({"foo.bar": "value", "bar.baz": UNSET}, ["-c", "foo.bar=value"]),
                        # All keys are unset
                        ({"foo.bar": UNSET}, []),
                        # Mixed unset, true, false
                        (
                            {"a.b": UNSET, "b.c": True, "c.d": False},
                            ["-c", "b.c", "-c", "c.d="],
                        ),
                    ],
                )
                def test_main_cmd_c_args(self, input_dict, expected):
                    git = SimpleGitCommand().git_opts_override(c=input_dict)
                    assert git._main_cmd_small_c_args() == expected


    class TestEnvOverrides:
        class TestSupplied:
            class TestSameCall:
                @pytest.mark.parametrize("prefer_cli", [True, False])
                def test_one_supplied(self, prefer_cli):
                    git = CLISimpleGitCommand(envs=dict(GIT_AUTHOR_NAME="ss"), prefer_cli=prefer_cli)
                    assert git.git_envs_override(GIT_TRACE=True).build_git_envs() == {
                        "GIT_AUTHOR_NAME": "ss",
                        "GIT_TRACE": "True"
                    }

                def test_multiple_supplied(self):
                    git = SimpleGitCommand()
                    assert git.git_envs_override(
                        GIT_TRACE=1, GIT_DIR=Path("/tmp/git-dir/"), GIT_EDITOR="vim"
                    ).build_git_envs() == {
                        "GIT_TRACE": "1",
                        "GIT_DIR": str(Path("/tmp/git-dir")),
                        "GIT_EDITOR": "vim",
                    }

                class TestMainOptMixed:
                    def test_one_supplied_main_opts_last_call(self):
                        git = SimpleGitCommand()
                        assert git.git_envs_override(GIT_TRACE=True).git_opts_override(
                            no_pager=True
                        ).build_git_envs() == {"GIT_TRACE": "True"}

                    def test_one_supplied_main_opts_non_last_call(self):
                        git = SimpleGitCommand()
                        assert git.git_opts_override(no_pager=True).git_envs_override(
                            GIT_TRACE=True
                        ).build_git_envs() == {"GIT_TRACE": "True"}

                    def test_multiple_supplied_main_opts_first(self):
                        git = SimpleGitCommand()
                        assert git.git_opts_override(no_advice=True).git_envs_override(
                            GIT_TRACE=1, GIT_DIR=Path("/tmp/git-dir/"), GIT_EDITOR="vim"
                        ).build_git_envs() == {
                            "GIT_TRACE": "1",
                            "GIT_DIR": str(Path("/tmp/git-dir")),
                            "GIT_EDITOR": "vim",
                        }

                    def test_multiple_supplied_main_opts_last(self):
                        git = SimpleGitCommand()
                        assert git.git_envs_override(
                            GIT_TRACE=1, GIT_DIR=Path("/tmp/git-dir/"), GIT_EDITOR="vim"
                        ).git_opts_override(no_advice=True).build_git_envs() == {
                            "GIT_TRACE": "1",
                            "GIT_DIR": str(Path("/tmp/git-dir")),
                            "GIT_EDITOR": "vim",
                        }

        class TestMultipleCalls:
            def test_one_supplied(self):
                git = SimpleGitCommand()
                assert git.git_envs_override().git_envs_override(
                    GIT_TRACE_SETUP=2
                ).git_envs_override().build_git_envs() == {"GIT_TRACE_SETUP": "2"}

            def test_one_supplied_more_calls(self):
                git = SimpleGitCommand()
                assert git.git_envs_override().git_envs_override(
                    GIT_TRACE_SETUP=2
                ).git_envs_override(GIT_ADVICE=False).build_git_envs() == {
                    "GIT_TRACE_SETUP": "2",
                    "GIT_ADVICE": "False",
                }

            def test_multiple_supplied(self):
                git = SimpleGitCommand()
                assert git.git_envs_override(GIT_SSH=Path("/tmp/SSH")).git_envs_override(
                    GIT_TERMINAL_PROMPT=1, GIT_NO_REPLACE_OBJECTS=True
                ).git_envs_override(
                    GIT_ALTERNATE_OBJECT_DIRECTORIES=Path("/tmp/alter")
                ).build_git_envs() == {
                    "GIT_SSH": str(Path("/tmp/SSH")),
                    "GIT_TERMINAL_PROMPT": "1",
                    "GIT_NO_REPLACE_OBJECTS": "True",
                    "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(Path("/tmp/alter")),
                }

            class TestMainOptsMixed:
                def test_one_supplied(self):
                    git = SimpleGitCommand()
                    assert git.git_envs_override().git_opts_override().git_envs_override(
                        GIT_TRACE_SETUP=2
                    ).git_envs_override().git_opts_override(
                        noglob_pathspecs=True, icase_pathspecs=False
                    ).build_git_envs() == {"GIT_TRACE_SETUP": "2"}

                def test_one_supplied_more_calls(self):
                    git = SimpleGitCommand()
                    assert git.git_envs_override().git_opts_override(
                        exec_path=Path("/tmp/git-dir")
                    ).git_envs_override(GIT_TRACE_SETUP=2).git_envs_override(
                        GIT_ADVICE=False
                    ).git_opts_override(
                        noglob_pathspecs=True, icase_pathspecs=False
                    ).build_git_envs() == {"GIT_TRACE_SETUP": "2", "GIT_ADVICE": "False"}

                def test_multiple_supplied(self):
                    git = SimpleGitCommand()
                    assert git.git_envs_override(
                        GIT_SSH=Path("/tmp/SSH")
                    ).git_opts_override(exec_path=Path("/tmp/git-dir")).git_envs_override(
                        GIT_TERMINAL_PROMPT=1, GIT_NO_REPLACE_OBJECTS=True
                    ).git_envs_override(
                        GIT_ALTERNATE_OBJECT_DIRECTORIES=Path("/tmp/alter")
                    ).build_git_envs() == {
                        "GIT_SSH": str(Path("/tmp/SSH")),
                        "GIT_TERMINAL_PROMPT": "1",
                        "GIT_NO_REPLACE_OBJECTS": "True",
                        "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(Path("/tmp/alter")),
                    }

        class TestOverrideValues:
            def test_unset_value_alone(self):
                """
                only GIT_DIR is set in first ``git_envs_override()`` call and is unset in next ``git_envs_override()`` call.
                """
                git = SimpleGitCommand()
                assert (
                    git.git_envs_override(GIT_DIR=Path("tmp"))
                    .git_envs_override(GIT_DIR=UNSET)
                    .build_git_envs()
                    == {}
                )

            def test_unset_value_defined_with_others(self):
                """
                GIT_DIR and GIT_ADVICE is set in first ``git_envs_override()`` call and is unset in next ``git_envs_override()`` call.
                """
                git = SimpleGitCommand()
                assert git.git_envs_override(
                    GIT_DIR=Path("tmp"), GIT_TRACE=2, GIT_ADVICE=0
                ).git_envs_override(GIT_DIR=UNSET).build_git_envs() == {
                    "GIT_TRACE": "2",
                    "GIT_ADVICE": "0",
                }

            class TestMultipleCalls:
                def test_unset_value_on_last_call(self):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in last ``git_opts_override()`` call.
                    """
                    git = SimpleGitCommand()
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(exec_path=UNSET).build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                    ]

                def test_unset_value_on_non_last_call(self):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in next ``git_opts_override()`` call.
                    * --no-replace-objects is set in last ``git_opts_override()`` call.
                    """
                    git = SimpleGitCommand()
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(exec_path=UNSET).git_opts_override(
                        no_replace_objects=True
                    ).build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                        "--no-replace-objects",
                    ]

                def test_no_value_on_non_last_call(self):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in next ``git_opts_override()`` call.
                    * no value given to last ``git_opts_override()`` call.
                    """
                    git = SimpleGitCommand()
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(
                        exec_path=UNSET
                    ).git_opts_override().build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                    ]

                def test_re_set_value_on_non_last_call(self):
                    """
                    * -C and --exec-path is set in first ``git_opts_override()`` call.
                    * --config-env is set in the next ``git_opts_override()`` call.
                    * --exec-path is unset in next ``git_opts_override()`` call.
                    * --no-replace-objects is set in last ``git_opts_override()`` call.
                    """
                    git = SimpleGitCommand()
                    assert git.git_opts_override(
                        exec_path=Path("tmp"), C=[Path()]
                    ).git_opts_override(
                        config_env={"auth": "suhas", "comm": "suyog"}
                    ).git_opts_override(exec_path=UNSET).git_opts_override(
                        exec_path=Path()
                    ).build_main_cmd_args() == [
                        "-C",
                        ".",
                        "--config-env",
                        "auth=suhas",
                        "--config-env",
                        "comm=suyog",
                        "--exec-path",
                        ".",
                    ]

        class TestIndividualMethods:
            class TestSmallC:
                @pytest.mark.parametrize(
                    "input_dict,expected",
                    [
                        # Simple key-value
                        ({"foo.bar": "baz"}, ["-c", "foo.bar=baz"]),
                        # Empty string value
                        ({"foo.bar": ""}, ["-c", "foo.bar="]),
                        # Boolean True (no equals sign)
                        ({"foo.bar": True}, ["-c", "foo.bar"]),
                        # Boolean False (explicit empty string)
                        ({"foo.bar": False}, ["-c", "foo.bar="]),
                        # None (treated as True)
                        ({"foo.bar": None}, ["-c", "foo.bar"]),
                        # Mixed values
                        (
                            {"a.b": "x", "c.d": "", "e.f": True, "g.h": False, "i.j": None},
                            [
                                "-c",
                                "a.b=x",
                                "-c",
                                "c.d=",
                                "-c",
                                "e.f",
                                "-c",
                                "g.h=",
                                "-c",
                                "i.j",
                            ],
                        ),
                        # Empty config (no args)
                        ({}, []),
                        # c is None
                        (None, []),
                        # c is UNSET
                        (UNSET, []),
                        # Missing key
                        ({}, []),
                        # UNSET should remove the key
                        ({"foo.bar": "value", "bar.baz": UNSET}, ["-c", "foo.bar=value"]),
                        # All keys are unset
                        ({"foo.bar": UNSET}, []),
                        # Mixed unset, true, false
                        (
                            {"a.b": UNSET, "b.c": True, "c.d": False},
                            ["-c", "b.c", "-c", "c.d="],
                        ),
                    ],
                )
                def test_main_cmd_c_args(self, input_dict, expected):
                    git = SimpleGitCommand().git_opts_override(c=input_dict)
                    assert git._main_cmd_small_c_args() == expected


    class TestOptsEnvMixedOverrides:
        class TestNoOverrides:
            def test_leaves_envs_empty(self):
                git = SimpleGitCommand()
                assert git._env_vars == {}

            def test_leaves_opts_empty(self):
                git = SimpleGitCommand()
                assert git._main_cmd_opts == {}

        class TestOverridingPropDoesNotAffectParentProps:
            """
            Overriding properties using *_override() methods do not change the properties of the objects which they've
            overridden, instead a new object with the overridden properties is returned.
            """

            class TestEnvs:
                def test_once(self):
                    git = SimpleGitCommand()
                    envs_o_git = git.git_envs_override(
                        GIT_AUTHOR_NAME="ss", GIT_OBJECT_DIRECTORY=Path("/tmp/obj-dir/")
                    )
                    assert (
                        git._env_vars == {}
                    )  # parent ``git`` object protected properties still empty.
                    assert envs_o_git._env_vars == {
                        "GIT_AUTHOR_NAME": "ss",
                        "GIT_OBJECT_DIRECTORY": Path("/tmp/obj-dir/"),
                    }

                def test_twice(self):
                    git = SimpleGitCommand()
                    envs_o_git = git.git_envs_override(
                        GIT_AUTHOR_NAME="ss", GIT_OBJECT_DIRECTORY=Path("/tmp/obj-dir/")
                    )
                    envs_o_o_git = envs_o_git.git_envs_override(GIT_SSH_COMMAND="gpg")
                    assert (
                        git._env_vars == {}
                    )  # ancestor ``git`` object protected properties still empty.
                    assert envs_o_git._env_vars == {
                        "GIT_AUTHOR_NAME": "ss",
                        "GIT_OBJECT_DIRECTORY": Path("/tmp/obj-dir/"),
                    }  # parent git protected properties still not overridden
                    assert envs_o_o_git._env_vars == {
                        "GIT_AUTHOR_NAME": "ss",
                        "GIT_OBJECT_DIRECTORY": Path("/tmp/obj-dir/"),
                        "GIT_SSH_COMMAND": "gpg",
                    }  # new property added in child object

            class TestOpts:
                def test_once(self):
                    git = SimpleGitCommand()
                    main_o_git = git.git_opts_override(
                        namespace="ss", git_dir=Path("/tmp/git-dir/.git")
                    )
                    assert (
                        git._main_cmd_opts == {}
                    )  # parent ``git`` object protected properties still empty.
                    assert main_o_git._main_cmd_opts == {
                        "namespace": "ss",
                        "git_dir": Path("/tmp/git-dir/.git"),
                    }

                def test_twice(self):
                    git = SimpleGitCommand()
                    main_o_git = git.git_opts_override(
                        namespace="ss", git_dir=Path("/tmp/git-dir/.git")
                    )
                    main_o_o_git = main_o_git.git_opts_override(paginate=True)
                    assert (
                        git._main_cmd_opts == {}
                    )  # ancestor ``git`` object protected properties still empty.
                    assert main_o_git._main_cmd_opts == {
                        "namespace": "ss",
                        "git_dir": Path("/tmp/git-dir/.git"),
                    }  # parent git protected properties still not overridden
                    assert main_o_o_git._main_cmd_opts == {
                        "namespace": "ss",
                        "git_dir": Path("/tmp/git-dir/.git"),
                        "paginate": True,
                    }  # new property added in child object

        class TestOverridingOneDoesNotAffectOther:
            def test_override_envs(self):
                git = SimpleGitCommand()
                envs_o_git = git.git_envs_override(
                    GIT_AUTHOR_NAME="ss", GIT_OBJECT_DIRECTORY=Path("/tmp/obj-dir/")
                )
                assert (
                    git._main_cmd_opts == {}
                )  # overriding envs didn't override main-opts in parent
                assert (
                    envs_o_git._main_cmd_opts == {}
                )  # overriding envs didn't override main-opts

            def test_override_opts(self):
                git = SimpleGitCommand()
                main_o_git = git.git_opts_override(
                    namespace="ss", git_dir=Path("/tmp/git-dir/.git")
                )
                assert git._env_vars == {}  # overriding opts didn't override envs in parent
                assert main_o_git._env_vars == {}  # overriding opts didn't override envs


class TestLsTreeSubcmd:
    # TODO: refactor when commit_subcmd is implemented.
    def test_ls_tree(self, repo_local):
        git = SimpleGitCommand(repo_local)
        Path(repo_local, "a-file").write_text("a-file")
        git.add_subcmd.add(".")
        git.subcmd_unchecked.run(["config", "--local", "user.name", "suhas"])
        git.subcmd_unchecked.run(
            ["config", "--local", "user.email", "suhas@example.com"]
        )
        git.subcmd_unchecked.run(["commit", "-m", "committed a-file"])
        assert (
            git.ls_tree_subcmd.ls_tree("HEAD")
            == "100644 blob 7c35e066a9001b24677ae572214d292cebc55979	a-file"
        )

    class TestArgValidation:
        @pytest.mark.parametrize(
            "tree_ish",
            [
                True,
                False,
                20,
                -90.0,
                None,
                ["tree", "ish"],
                {"key": "value"},
                (1, 2, 3),
                {1, 2},
                bytes("tree", "utf-8"),
                b"HEAD",
                object(),
            ],
        )
        def test_tree_ish_must_be_str(self, tree_ish):
            with pytest.raises(GitExitingException) as e:
                SimpleGitCommand().ls_tree_subcmd.ls_tree(tree_ish)  # type: ignore[arg-type] # expects str and provided Any
            assert e.value.exit_code == ERR_DATA_FORMAT_ERR

        @pytest.mark.parametrize("abbrev", ["abc", True, 5.5, [5], None])
        def test_abbrev_must_be_int(self, abbrev):
            with pytest.raises(GitExitingException) as e:
                SimpleGitCommand().ls_tree_subcmd.ls_tree("HEAD", abbrev=abbrev)  # type: ignore[arg-type] # expects int, provided Any
            assert e.value.exit_code == ERR_DATA_FORMAT_ERR

        @pytest.mark.parametrize("abbrev", [-1, 41, 100])
        def test_abbrev_must_be_in_range(self, abbrev):
            with pytest.raises(GitExitingException) as e:
                SimpleGitCommand().ls_tree_subcmd.ls_tree("HEAD", abbrev=abbrev)
            assert e.value.exit_code == ERR_INVALID_USAGE

        @pytest.mark.parametrize(
            "format_",
            [10, True, None, ["format"], {"format": "value"}, 5.5, b"%(objectname)"],
        )
        def test_format_must_be_str(self, format_):
            with pytest.raises(GitExitingException) as e:
                SimpleGitCommand().ls_tree_subcmd.ls_tree("HEAD", format_=format_)  # type: ignore[arg-type] # expects str, provided Any
            assert e.value.exit_code == ERR_DATA_FORMAT_ERR

        @pytest.mark.parametrize(
            "path",
            [
                "src/",
                123,
                None,
                [1, 2, 3],
                [None, "file"],
                [b"bytes"],
                (["tuple"],),
                {"a", "b"},
            ],
        )
        def test_path_must_be_list_of_strings(self, path):
            with pytest.raises(GitExitingException) as e:
                SimpleGitCommand().ls_tree_subcmd.ls_tree("HEAD", path=path)  # type: ignore[arg-type] # expects list[str], provided Any
            assert e.value.exit_code == ERR_DATA_FORMAT_ERR


def test_version():
    git = SimpleGitCommand()
    assert "git version 2" in git.version


def test_version_build_options():
    git = SimpleGitCommand()
    version_build_info = git.version_subcmd.version(build_options=True)
    assert "git version 2" in version_build_info
    assert "cpu: " in version_build_info
    assert "shell-path: " in version_build_info
    git.version_subcmd.git_opts_override().git_opts_override(no_advice=True)
    ano_build_info = git.version_subcmd.git_opts_override(namespace="suhas").version(
        build_options=True
    )
    assert "git version 2" in ano_build_info
    assert "cpu: " in ano_build_info
    assert "shell-path: " in ano_build_info


class TestAddSubcmd:
    def test_add(self, repo_local):
        Path(repo_local, "a-file").write_text("a-file")
        git = SimpleGitCommand(repo_local)
        git.add_subcmd.add(".")
        assert (
            "a-file"
            in git.subcmd_unchecked.run(
                ["diff", "--cached", "--name-only"],
                cwd=repo_local,
                text=True,
            ).stdout
        )

    def test_with_pathspec(self, repo_local):
        Path(repo_local, "a-file").write_text("a-file")
        Path(repo_local, "b-file").write_text("b-file")
        git = SimpleGitCommand(repo_local)
        git.add_subcmd.add("*-file")
        indexed_files = git.subcmd_unchecked.run(
            ["diff", "--cached", "--name-only"],
            text=True,
        ).stdout
        assert "a-file" in indexed_files
        assert "b-file" in indexed_files

    def test_with_pathspecs(self, repo_local):
        Path(repo_local, "a-file").write_text("a-file")
        Path(repo_local, "b-file").write_text("b-file")
        git = SimpleGitCommand(repo_local)
        git.add_subcmd.add("a-file", "b-file")
        indexed_files = git.subcmd_unchecked.run(
            ["diff", "--cached", "--name-only"],
            text=True,
        ).stdout
        assert "a-file" in indexed_files
        assert "b-file" in indexed_files

    def test_with_pathspec_from_file(self, repo_local, tmp_path):
        Path(repo_local, "a-file").write_text("a-file")
        Path(repo_local, "b-file").write_text("b-file")
        pathspec_file = Path(tmp_path, "pathspec-file.txt")
        pathspec_file.write_text("*-file")
        git = SimpleGitCommand(repo_local)
        git.add_subcmd.add(pathspec_from_file=pathspec_file)
        indexed_files = git.subcmd_unchecked.run(
            ["diff", "--cached", "--name-only"],
            text=True,
        ).stdout
        assert "a-file" in indexed_files
        assert "b-file" in indexed_files


@pytest.mark.parametrize(
    "subcmd", ["add_subcmd", "version_subcmd", "ls_tree_subcmd", "subcmd_unchecked"]
)
class TestSubcommandsPersistence:
    def test_envs_set_remain_set(self, repo_local, subcmd):
        git = SimpleGitCommand(repo_local)
        git = git.git_envs_override(GIT_TRACE=True).git_envs_override(
            GIT_AUTHOR_NAME="ss", GIT_COMMITTER_NAME="sos"
        )
        git = git.git_envs_override(GIT_SSH_COMMAND="ssh-l")
        _subcmd = getattr(git, subcmd)
        assert (
            dict(
                GIT_TRACE="True",
                GIT_AUTHOR_NAME="ss",
                GIT_COMMITTER_NAME="sos",
                GIT_SSH_COMMAND="ssh-l",
            )
            == _subcmd.underlying_git.build_git_envs()
        )

    def test_opts_set_remain_set(self, repo_local, subcmd):
        git = SimpleGitCommand(repo_local)
        git = git.git_opts_override(git_dir=repo_local).git_opts_override(
            no_pager=True, icase_pathspecs=True
        )
        git = git.git_opts_override(c={"foo": True, "foo.bar": 10})
        _subcmd = getattr(git, subcmd)
        assert {
            "c": {"foo": True, "foo.bar": 10},
            "git_dir": repo_local,
            "icase_pathspecs": True,
            "no_pager": True,
        } == _subcmd.underlying_git._main_cmd_opts

    def test_opts_and_envs_intermixed_remain_set(self, repo_local, subcmd):
        git = SimpleGitCommand(repo_local)
        git = git.git_envs_override(GIT_TRACE=True).git_envs_override(
            GIT_AUTHOR_NAME="ss", GIT_COMMITTER_NAME="sos"
        )
        git = (
            git.git_opts_override(git_dir=repo_local)
            .git_opts_override(no_pager=True, icase_pathspecs=True)
            .git_envs_override(GIT_SSH_COMMAND="ssh-l")
            .git_opts_override(c={"foo": True, "foo.bar": 10})
        )
        _subcmd = getattr(git, subcmd)
        assert {
            "c": {"foo": True, "foo.bar": 10},
            "git_dir": repo_local,
            "icase_pathspecs": True,
            "no_pager": True,
        } == _subcmd.underlying_git._main_cmd_opts

        assert (
            dict(
                GIT_TRACE="True",
                GIT_AUTHOR_NAME="ss",
                GIT_COMMITTER_NAME="sos",
                GIT_SSH_COMMAND="ssh-l",
            )
            == _subcmd.underlying_git.build_git_envs()
        )
        assert {
            "c": {"foo": True, "foo.bar": 10},
            "git_dir": repo_local,
            "icase_pathspecs": True,
            "no_pager": True,
        } == _subcmd.underlying_git._main_cmd_opts


# TODO: write exhaustive tests for unchecked subcmd
