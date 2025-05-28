#!/usr/bin/env python3
# coding=utf-8

"""
Git command interfaces with default implementation using subprocess calls.
"""

from vt.vcs.git.gitlib.base import *

from vt.utils.errors.error_specs import ErrorMsgFormer

errmsg_creator = ErrorMsgFormer
"""
Create formatted error messages using this global instance.

To get a local instance use ``errmsg_creator.clone_with(...)``.
"""
