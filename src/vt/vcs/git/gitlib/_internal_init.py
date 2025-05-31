#!/usr/bin/env python3
# coding=utf-8

"""
Git command interfaces with default implementation using subprocess calls.

This file is created to behave as an __init__ but only for internal stuff as we do not want to export everything
in the package's __init__.
"""

from vt.utils.errors.error_specs import ErrorMsgFormer

errmsg_creator = ErrorMsgFormer
"""
Create formatted error messages using this global instance.

To get a local instance use ``errmsg_creator.clone_with(...)``.
"""
