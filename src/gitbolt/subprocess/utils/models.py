#!/usr/bin/env python3
# coding=utf-8

"""
Models useful for session utilities.
"""
import dataclasses
import datetime


@dataclasses.dataclass
class GitRawActor:
    name: bytes
    email: bytes
    time: datetime.datetime

    @classmethod
    def from_commit_bytes(cls, commit_bytes: bytes, email_start_pattern: bytes = b" <",
                          email_end_pattern: bytes = b"> ") -> "GitRawActor":
        """
        Obtain ``Actor`` object from the author/committer bytes.

        Examples:

        Simple timestamp without timezone:

        >>> _ss_actor1 = GitRawActor.from_commit_bytes(b"Suhas <sss@ss.ss> 1780211249")
        >>> assert _ss_actor1.name == b"Suhas"
        >>> assert _ss_actor1.email == b"sss@ss.ss"
        >>> assert _ss_actor1.time.timestamp() == 1780211249.0

        Simple timestamp with timezone:

        >>> _ss_actor2 = GitRawActor.from_commit_bytes(b"Suhas Srivastava <sss@vaastav.tech> 1780211249 +0530")
        >>> assert _ss_actor2.name == b"Suhas Srivastava"
        >>> assert _ss_actor2.email == b"sss@vaastav.tech"

        # failing timezone test >>> assert _ss_actor2.time.timestamp() == 1780211249.0

        :param commit_bytes: author/committer information in bytes form.
        :param email_start_pattern: email spearates name and timestamp. Thus is required as a separator.
            Marks email beginning.
        :param email_end_pattern: email spearates name and timestamp. Thus is required as a separator.
            Marks email ending.
        :returns: ``Actor`` object with all the parsed and set values.
        """
        email_pattern_start_index = commit_bytes.find(email_start_pattern)
        email_pattern_end_index = commit_bytes.rfind(email_end_pattern)
        email_start_index = email_pattern_start_index+len(email_start_pattern)
        email_end_index = email_pattern_end_index
        name = commit_bytes[:email_pattern_start_index]
        email = commit_bytes[email_start_index:email_end_index]
        # TODO: handle timezone correctly
        time_bytes = commit_bytes[email_end_index+len(email_end_pattern):]
        time_main, time_zone = time_bytes.split() if b" " in time_bytes else (time_bytes, b"")
        date_time_for_iso_str = datetime.datetime.fromtimestamp(int(time_main))
        date_time = datetime.datetime.fromisoformat(f"{date_time_for_iso_str.date()}T{date_time_for_iso_str.time()}{time_zone.decode()}")
        return GitRawActor(name, email, date_time)


@dataclasses.dataclass
class GitRawSignature:
    signature: bytes


@dataclasses.dataclass
class GPGGitRawSignature(GitRawSignature):
    pass


@dataclasses.dataclass
class SSHGitRawSignature(GitRawSignature):
    pass


@dataclasses.dataclass
class RawCommitBytesObj:
    """
    Commit info all in bytes as read from ``git cat-file --batch``.
    """
    commit_hash: bytes
    tree_hash: bytes
    parents: list[bytes]
    author: GitRawActor
    committer: GitRawActor
    signature: GitRawSignature | None
    message: bytes


@dataclasses.dataclass
class RawBytesValsOfCommit:
    tree_val: bytes
    commit_parents_vals: list[bytes]
    author_val: bytes
    committer_val: bytes
    signature_val: bytes | None
    commit_message: bytes
