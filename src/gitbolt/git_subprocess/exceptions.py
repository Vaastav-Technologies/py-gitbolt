#!/usr/bin/env python3
# coding=utf-8

"""
Exceptions specific to git using subprocess.
"""

from vt.utils.errors.error_specs.exceptions import VTCmdException

from gitbolt.exceptions import GitException


class GitCmdException(GitException, VTCmdException):
    """
    A ``GitException`` that is also a ``VTCmdException``.

    Examples:

        >>> from subprocess import CalledProcessError

      * raise without message:

        >>> raise GitCmdException(called_process_error=CalledProcessError(1, ['git', 'status'])) # always use `from` clause.
        Traceback (most recent call last):
        gitbolt.git_subprocess.exceptions.GitCmdException: CalledProcessError: Command '['git', 'status']' returned non-zero exit status 1.

      * raise with a message:

        >>> raise GitCmdException('Git failed', called_process_error=CalledProcessError(1, ['git', 'push'])) # always use `from` clause.
        Traceback (most recent call last):
        gitbolt.git_subprocess.exceptions.GitCmdException: CalledProcessError: Git failed

      * raise with overridden exit code:

        >>> raise GitCmdException('Git push failed', called_process_error=CalledProcessError(1, ['git', 'push']), exit_code=42) # always use `from` clause.
        Traceback (most recent call last):
        gitbolt.git_subprocess.exceptions.GitCmdException: CalledProcessError: Git push failed

      * raise without message, override with stderr inside CalledProcessError:

        >>> err = CalledProcessError(128, ['git', 'fetch'], stderr='fatal: not a git repository')
        >>> raise GitCmdException(called_process_error=err) # always use `from` clause.
        Traceback (most recent call last):
        gitbolt.git_subprocess.exceptions.GitCmdException: CalledProcessError: Command '['git', 'fetch']' returned non-zero exit status 128.

      * raise exception using `from` clause (chaining):

        >>> try:
        ...     raise CalledProcessError(129, ['git', 'clone'], stderr='fatal: repo not found')
        ... except CalledProcessError as e:
        ...     raise GitCmdException('Clone failed', called_process_error=e) from e
        Traceback (most recent call last):
        gitbolt.git_subprocess.exceptions.GitCmdException: CalledProcessError: Clone failed

      * cause reflects original CalledProcessError when chained:

        >>> try:
        ...     raise CalledProcessError(2, ['git', 'commit'])
        ... except CalledProcessError as e:
        ...     try:
        ...         raise GitCmdException('Commit failed', called_process_error=e) from e
        ...     except GitCmdException as g:
        ...         isinstance(g.cause, CalledProcessError)
        True

      * cause falls back to `called_process_error` when not chained:

        >>> e = CalledProcessError(3, ['git', 'diff'])
        >>> g = GitCmdException('Diff fail', called_process_error=e)
        >>> g.cause is g.called_process_error
        True

      * access exit code:

        >>> e = CalledProcessError(100, ['git', 'log'])
        >>> ex = GitCmdException('Failure', called_process_error=e)
        >>> ex.exit_code
        100

      * override exit code manually:

        >>> GitCmdException('Overridden', called_process_error=e, exit_code=77).exit_code
        77

      * access structured information:

        >>> g = GitCmdException('Git structured', called_process_error=e)
        >>> info = g.to_dict()
        >>> info['type'], 'Git structured' in info['message']
        ('GitCmdException', True)

      * raise exception with extra metadata:

        >>> e = CalledProcessError(4, ['git', 'tag'])
        >>> x = GitCmdException('Failed tagging', called_process_error=e, context='tagging-op')
        >>> x.kwargs['context']
        'tagging-op'

      * demonstrate subclass relationship:

        >>> isinstance(GitCmdException('x', called_process_error=e), VTCmdException)
        True

        >>> isinstance(GitCmdException('x', called_process_error=e), GitException)
        True

    ... rest examples mimic ``VTCmdException``.
    """

    pass
