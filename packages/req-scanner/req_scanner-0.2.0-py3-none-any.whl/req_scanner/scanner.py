# -*- coding: utf-8 -*-
"""
Handles all logic related to parsing source code to find imports
and mapping them to package names.
"""
import ast
import fnmatch
import os
import sys
from functools import lru_cache
from typing import Dict, List, Optional, Set, Tuple

try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata

from packaging.requirements import Requirement

from .deps import get_installed_packages


class ImportVisitor(ast.NodeVisitor):
    """An AST visitor that extracts all top-level module imports from a Python file."""

    def __init__(self) -> None:
        self.imports: Set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.add(alias.name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module and node.level == 0:
            self.imports.add(node.module.split(".")[0])
        self.generic_visit(node)


def find_project_imports(
    project_path: str, ignore_patterns: Optional[List[str]] = None
) -> Set[str]:
    """Recursively walks a project directory to find unique top-level module imports."""
    imports: Set[str] = set()
    ignore_patterns = ignore_patterns or []
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [
            d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in ignore_patterns)
        ]
        for file in files:
            if not file.endswith(".py") or any(
                fnmatch.fnmatch(file, p) for p in ignore_patterns
            ):
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    tree = ast.parse(f.read(), filename=file_path)
                    visitor = ImportVisitor()
                    visitor.visit(tree)
                    imports.update(visitor.imports)
            except Exception as e:
                print(
                    f"Warning: Could not parse '{file_path}'. Skipping. Error: {e}",
                    file=sys.stderr,
                )
    return imports


@lru_cache(maxsize=None)
def map_imports_to_packages() -> Dict[str, str]:
    """Creates a mapping from importable module names to their distribution package names."""
    mapping: Dict[str, str] = {}
    for dist in metadata.distributions():
        package_name = dist.metadata["name"]
        if not package_name:
            continue
        normalized_package_name = package_name.lower().replace("_", "-")
        try:
            top_level_modules = dist.read_text("top_level.txt")
            if top_level_modules:
                for module in top_level_modules.strip().split("\n"):
                    mapping[module] = normalized_package_name
            else:
                mapping[package_name.replace("-", "_")] = normalized_package_name
        except (FileNotFoundError, IsADirectoryError, PermissionError):
            mapping[package_name.replace("-", "_")] = normalized_package_name
    return mapping


def resolve_primary_packages(project_imports: Set[str]) -> Tuple[Set[str], Set[str]]:
    """
    Filters project imports to find corresponding primary package names.
    Returns a tuple of (found_primary_packages, unmappable_imports).
    """
    std_lib_modules = (
        set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()
    )
    primary_packages = set()
    unmapped_imports = set()
    import_map = map_imports_to_packages()
    installed_packages = get_installed_packages()

    for imp in project_imports:
        if imp in std_lib_modules or imp in sys.builtin_module_names:
            continue

        package_name = import_map.get(imp)
        if not package_name:
            normalized_imp = imp.lower().replace("_", "-")
            if normalized_imp in installed_packages:
                package_name = normalized_imp

        if package_name and package_name in installed_packages:
            primary_packages.add(package_name)
        else:
            unmapped_imports.add(imp)

    return primary_packages, unmapped_imports


def parse_requirements_file(file_path: str) -> Optional[Set[str]]:
    """Parses a requirements.txt file and returns a set of package names."""
    packages = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        req = Requirement(line)
                        packages.add(req.name.lower().replace("_", "-"))
                    except Exception:
                        print(
                            f"Warning: Could not parse line in requirements file: '{line}'",
                            file=sys.stderr,
                        )
    except FileNotFoundError:
        print(f"Error: Requirements file not found at '{file_path}'", file=sys.stderr)
        return None
    return packages
