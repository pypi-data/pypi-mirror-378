# -*- coding: utf-8 -*-

"""
Centralized absolute path management for DevOps operations.

This module provides a unified entry point for all project paths using absolute path references,
eliminating current directory dependencies and enabling IDE autocomplete support for consistent
path access across development, testing, and deployment workflows.
"""

from pathlib import Path
from functools import cached_property

_dir_here = Path(__file__).absolute().parent
PACKAGE_NAME = _dir_here.name


class PathEnum:
    """
    Centralized enumeration of all project paths with absolute path references.

    Provides IDE-autocomplete-friendly access to all project directories and files using
    absolute paths to eliminate current directory dependencies and ensure consistent path
    resolution across different execution contexts and DevOps workflows.
    """
    # fmt: off
    # essential
    dir_project_root = _dir_here.parent

    @cached_property
    def dir_home(self):
        return Path.home()

    dir_python_lib = dir_project_root / PACKAGE_NAME
    path_pyproject_toml = dir_project_root / "pyproject.toml"
    path_requirements_txt = dir_project_root / "requirements.txt"
    dir_tmp = dir_project_root / "tmp"

    # Virtual environment
    dir_venv = dir_project_root / ".venv"
    dir_venv_bin = dir_venv / "bin"
    path_venv_bin_pip = dir_venv_bin / "pip"
    path_venv_bin_python = dir_venv_bin / "python"

    # Virtualenv executable paths
    bin_pytest = dir_venv_bin / "pytest"

    # Test
    dir_htmlcov = dir_project_root / "htmlcov"
    path_cov_index_html = dir_htmlcov / "index.html"
    dir_unit_test = dir_project_root / "tests"
    dir_int_test = dir_project_root / "tests_int"
    dir_load_test = dir_project_root / "tests_load"

    # Documentation
    dir_docs_source = dir_project_root / "docs" / "source"
    dir_docs_build_html = dir_project_root / "docs" / "build" / "html"
    # fmt: on


path_enum = PathEnum()
"""
Single entry point for all project paths with absolute path references.
"""
