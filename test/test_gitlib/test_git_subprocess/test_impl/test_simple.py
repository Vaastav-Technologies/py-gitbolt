#!/usr/bin/env python3
# coding=utf-8

"""
Tests for Git command interfaces with default implementation using subprocess calls.
"""
from pathlib import Path

import pytest
from vt.utils.commons.commons.core_py import UNSET

from vt.vcs.git.gitlib.git_subprocess.impl.simple import SimpleGitCommand


def test_exec_path():
    git = SimpleGitCommand[str]()
    assert git.exec_path is None

def test_overrides_and_exec_path():
    git = SimpleGitCommand[str]()
    assert git.git(exec_path=None).exec_path is not None

class TestMainCmdOverrides:
    class TestSupplied:
        class TestSameCall:
            def test_one_supplied(self):
                git = SimpleGitCommand[str]()
                assert ['--no-replace-objects'] == git.git(no_replace_objects=True).compute_main_cmd_args()

            def test_multiple_supplied(self):
                git = SimpleGitCommand[str]()
                assert git.git(no_replace_objects=True, git_dir=Path(),
                               paginate=True).compute_main_cmd_args() == ['--paginate', '--git-dir', '.',
                                                                          '--no-replace-objects']

    class TestMultipleCalls:
        def test_one_supplied(self):
            git = SimpleGitCommand()
            assert git.git().git(exec_path=Path('tmp')).git(
                noglob_pathspecs=True).compute_main_cmd_args() == ['--exec-path', 'tmp', '--noglob-pathspecs']

        def test_multiple_supplied(self):
            git = SimpleGitCommand()
            assert git.git(exec_path=Path('tmp')).git(noglob_pathspecs=True, no_advice=True).git(
                config_env={'auth': 'suhas', 'comm': 'suyog'}).compute_main_cmd_args() == ['--config-env',
                                                                                           'auth=suhas',
                                                                                           '--config-env',
                                                                                           'comm=suyog',
                                                                                           '--exec-path',
                                                                                           'tmp', '--no-advice',
                                                                                           '--noglob-pathspecs']

    class TestOverrideValues:
        def test_unset_value_alone(self):
            """
            only --exec-path is set in first ``git()`` call and is unset in next ``git()`` call.
            """
            git = SimpleGitCommand()
            assert git.git(exec_path=Path('tmp')).git(exec_path=UNSET).compute_main_cmd_args() == []

        def test_unset_value_defined_with_others(self):
            """
            -C and --exec-path is set in first ``git()`` call and is unset in next ``git()`` call.
            """
            git = SimpleGitCommand()
            assert  git.git(exec_path=Path('tmp'), C=[Path()]).git(exec_path=UNSET).compute_main_cmd_args() == ['-C',
                                                                                                                '.']

        class TestMultipleCalls:
            def test_unset_value_on_last_call(self):
                """
                * -C and --exec-path is set in first ``git()`` call.
                * --config-env is set in the next ``git()`` call.
                * --exec-path is unset in last ``git()`` call.
                """
                git = SimpleGitCommand()
                assert git.git(exec_path=Path('tmp'), C=[Path()]).git(config_env={'auth': 'suhas',
                                                                                  'comm': 'suyog'}).git(
                    exec_path=UNSET).compute_main_cmd_args() == ['-C', '.', '--config-env', 'auth=suhas',
                                                                 '--config-env', 'comm=suyog']

            def test_unset_value_on_non_last_call(self):
                """
                * -C and --exec-path is set in first ``git()`` call.
                * --config-env is set in the next ``git()`` call.
                * --exec-path is unset in next ``git()`` call.
                * --no-replace-objects is set in last ``git()`` call.
                """
                git = SimpleGitCommand()
                assert git.git(exec_path=Path('tmp'), C=[Path()]).git(
                    config_env={'auth': 'suhas', 'comm': 'suyog'}).git(exec_path=UNSET).git(
                    no_replace_objects=True).compute_main_cmd_args() == ['-C', '.', '--config-env', 'auth=suhas',
                                                                         '--config-env', 'comm=suyog',
                                                                         '--no-replace-objects']

            def test_no_value_on_non_last_call(self):
                """
                * -C and --exec-path is set in first ``git()`` call.
                * --config-env is set in the next ``git()`` call.
                * --exec-path is unset in next ``git()`` call.
                * no value given to last ``git()`` call.
                """
                git = SimpleGitCommand()
                assert git.git(
                    exec_path=Path('tmp'), C=[Path()]).git(config_env={'auth': 'suhas', 'comm': 'suyog'}).git(
                    exec_path=UNSET).git().compute_main_cmd_args() == ['-C', '.', '--config-env', 'auth=suhas',
                                                                       '--config-env', 'comm=suyog']

            def test_re_set_value_on_non_last_call(self):
                """
                * -C and --exec-path is set in first ``git()`` call.
                * --config-env is set in the next ``git()`` call.
                * --exec-path is unset in next ``git()`` call.
                * --no-replace-objects is set in last ``git()`` call.
                """
                git = SimpleGitCommand()
                assert git.git(exec_path=Path('tmp'), C=[Path()]).git(
                    config_env={'auth': 'suhas', 'comm': 'suyog'}).git(exec_path=UNSET).git(
                    exec_path=Path()).compute_main_cmd_args() == ['-C', '.', '--config-env', 'auth=suhas',
                                                                  '--config-env', 'comm=suyog', '--exec-path', '.']
    class TestIndividualMethods:
        class TestSmallC:
            @pytest.mark.parametrize("input_dict,expected", [
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
                ({
                    "a.b": "x",
                    "c.d": "",
                    "e.f": True,
                    "g.h": False,
                    "i.j": None
                }, [
                     "-c", "a.b=x",
                     "-c", "c.d=",
                     "-c", "e.f",
                     "-c", "g.h=",
                     "-c", "i.j"
                 ]),

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
                ({
                    "a.b": UNSET,
                    "b.c": True,
                    "c.d": False
                }, ["-c", "b.c", "-c", "c.d="])
            ])
            def test_main_cmd_c_args(self, input_dict, expected):
                git = SimpleGitCommand().git(c=input_dict)
                assert git._main_cmd_small_c_args() == expected


def test_ls_tree(enc_local):
    git = SimpleGitCommand[str](enc_local)
    git.ls_tree_subcmd.ls_tree('HEAD')

def test_version():
    git = SimpleGitCommand()
    assert 'git version 2' in git.version

def test_version_build_options():
    git = SimpleGitCommand[str]()
    version_build_info = git.version_subcmd.version(build_options=True)
    assert 'git version 2' in version_build_info
    assert 'cpu: ' in version_build_info
    assert 'built from commit: ' in version_build_info
    ano_build_info = git.version_subcmd.git_opts_override(namespace='suhas').version(build_options=True)
    assert 'git version 2' in ano_build_info
    assert 'cpu: ' in ano_build_info
    assert 'built from commit: ' in ano_build_info
