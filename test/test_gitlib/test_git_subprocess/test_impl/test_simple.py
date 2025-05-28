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
    git = SimpleGitCommand()
    assert isinstance(git.exec_path, Path)

def test_overrides_and_exec_path():
    git = SimpleGitCommand()
    assert git.git_opts_override(exec_path=None).exec_path is not None

class TestMainCmdOverrides:
    class TestSupplied:
        class TestSameCall:
            def test_one_supplied(self):
                git = SimpleGitCommand()
                assert ['--no-replace-objects'] == git.git_opts_override(no_replace_objects=True).compute_main_cmd_args()

            def test_multiple_supplied(self):
                git = SimpleGitCommand()
                assert git.git_opts_override(no_replace_objects=True, git_dir=Path(),
                               paginate=True).compute_main_cmd_args() == ['--paginate', '--git-dir', '.',
                                                                          '--no-replace-objects']

    class TestMultipleCalls:
        def test_one_supplied(self):
            git = SimpleGitCommand()
            assert git.git_opts_override().git_opts_override(exec_path=Path('tmp')).git_opts_override(
                noglob_pathspecs=True).compute_main_cmd_args() == ['--exec-path', 'tmp', '--noglob-pathspecs']

        def test_multiple_supplied(self):
            git = SimpleGitCommand()
            assert git.git_opts_override(exec_path=Path('tmp')).git_opts_override(noglob_pathspecs=True, no_advice=True).git_opts_override(
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
            only --exec-path is set in first ``git_opts_override()`` call and is unset in next ``git_opts_override()`` call.
            """
            git = SimpleGitCommand()
            assert git.git_opts_override(exec_path=Path('tmp')).git_opts_override(exec_path=UNSET).compute_main_cmd_args() == []

        def test_unset_value_defined_with_others(self):
            """
            -C and --exec-path is set in first ``git_opts_override()`` call and is unset in next ``git_opts_override()`` call.
            """
            git = SimpleGitCommand()
            assert  git.git_opts_override(exec_path=Path('tmp'), C=[Path()]).git_opts_override(exec_path=UNSET).compute_main_cmd_args() == ['-C',
                                                                                                                '.']

        class TestMultipleCalls:
            def test_unset_value_on_last_call(self):
                """
                * -C and --exec-path is set in first ``git_opts_override()`` call.
                * --config-env is set in the next ``git_opts_override()`` call.
                * --exec-path is unset in last ``git_opts_override()`` call.
                """
                git = SimpleGitCommand()
                assert git.git_opts_override(exec_path=Path('tmp'), C=[Path()]).git_opts_override(config_env={'auth': 'suhas',
                                                                                  'comm': 'suyog'}).git_opts_override(
                    exec_path=UNSET).compute_main_cmd_args() == ['-C', '.', '--config-env', 'auth=suhas',
                                                                 '--config-env', 'comm=suyog']

            def test_unset_value_on_non_last_call(self):
                """
                * -C and --exec-path is set in first ``git_opts_override()`` call.
                * --config-env is set in the next ``git_opts_override()`` call.
                * --exec-path is unset in next ``git_opts_override()`` call.
                * --no-replace-objects is set in last ``git_opts_override()`` call.
                """
                git = SimpleGitCommand()
                assert git.git_opts_override(exec_path=Path('tmp'), C=[Path()]).git_opts_override(
                    config_env={'auth': 'suhas', 'comm': 'suyog'}).git_opts_override(exec_path=UNSET).git_opts_override(
                    no_replace_objects=True).compute_main_cmd_args() == ['-C', '.', '--config-env', 'auth=suhas',
                                                                         '--config-env', 'comm=suyog',
                                                                         '--no-replace-objects']

            def test_no_value_on_non_last_call(self):
                """
                * -C and --exec-path is set in first ``git_opts_override()`` call.
                * --config-env is set in the next ``git_opts_override()`` call.
                * --exec-path is unset in next ``git_opts_override()`` call.
                * no value given to last ``git_opts_override()`` call.
                """
                git = SimpleGitCommand()
                assert git.git_opts_override(
                    exec_path=Path('tmp'), C=[Path()]).git_opts_override(config_env={'auth': 'suhas', 'comm': 'suyog'}).git_opts_override(
                    exec_path=UNSET).git_opts_override().compute_main_cmd_args() == ['-C', '.', '--config-env', 'auth=suhas',
                                                                       '--config-env', 'comm=suyog']

            def test_re_set_value_on_non_last_call(self):
                """
                * -C and --exec-path is set in first ``git_opts_override()`` call.
                * --config-env is set in the next ``git_opts_override()`` call.
                * --exec-path is unset in next ``git_opts_override()`` call.
                * --no-replace-objects is set in last ``git_opts_override()`` call.
                """
                git = SimpleGitCommand()
                assert git.git_opts_override(exec_path=Path('tmp'), C=[Path()]).git_opts_override(
                    config_env={'auth': 'suhas', 'comm': 'suyog'}).git_opts_override(exec_path=UNSET).git_opts_override(
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
                git = SimpleGitCommand().git_opts_override(c=input_dict)
                assert git._main_cmd_small_c_args() == expected


def test_ls_tree(enc_local):
    git = SimpleGitCommand(enc_local)
    git.ls_tree_subcmd.ls_tree('HEAD')

def test_version():
    git = SimpleGitCommand()
    assert 'git version 2' in git.version

def test_version_build_options():
    git = SimpleGitCommand()
    version_build_info = git.version_subcmd.version(build_options=True)
    assert 'git version 2' in version_build_info
    assert 'cpu: ' in version_build_info
    assert 'built from commit: ' in version_build_info
    git.version_subcmd.git_opts_override().git_opts_override(no_advice=True)
    ano_build_info = git.version_subcmd.git_opts_override(namespace='suhas').version(build_options=True)
    assert 'git version 2' in ano_build_info
    assert 'cpu: ' in ano_build_info
    assert 'built from commit: ' in ano_build_info

class TestAddSubcmd:
    def test_add(self, enc_local):
        Path(enc_local, 'a-file').write_text('a-file')
        git = SimpleGitCommand(enc_local)
        git.add_subcmd.add(pathspec=['.'])

    def test_with_pathspec(self, enc_local):
        Path(enc_local, 'a-file').write_text('a-file')
        Path(enc_local, 'b-file').write_text('b-file')
        git = SimpleGitCommand(enc_local)
        git.add_subcmd.add(pathspec=['*-file'])

    def test_with_pathspec_from_file(self, enc_local, tmp_path):
        Path(enc_local, 'a-file').write_text('a-file')
        Path(enc_local, 'b-file').write_text('b-file')
        pathspec_file = Path(tmp_path, 'pathspec-file.txt')
        pathspec_file.write_text('*-file')
        git = SimpleGitCommand(enc_local)
        git.add_subcmd.add(pathspec_from_file=pathspec_file)
