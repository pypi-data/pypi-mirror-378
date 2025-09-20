# -*- coding: utf-8 -*-
"""
Handles all logic related to the installed environment,
such as calling `pip` and resolving dependencies.
"""

import subprocess
import sys
from functools import lru_cache
from typing import Dict, List, Set, Tuple


@lru_cache(maxsize=None)
def get_installed_packages() -> Dict[str, str]:
    """Retrieves a dictionary of installed packages and their versions via 'pip freeze'."""
    packages: Dict[str, str] = {}
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            if "==" in line:
                package, version = line.split("==", 1)
                packages[package.lower().replace("_", "-")] = version
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error: Could not run 'pip freeze'.\n{e}", file=sys.stderr)
    return packages


@lru_cache(maxsize=None)
def get_direct_dependencies_from_pip(package: str) -> Set[str]:
    """Gets the direct dependencies of a package using `pip show`."""
    dependencies = set()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        for line in result.stdout.splitlines():
            if line.startswith("Requires:"):
                deps_str = line.replace("Requires:", "").strip()
                if deps_str:
                    dependencies.update(
                        d.strip().lower().replace("_", "-") for d in deps_str.split(",")
                    )
                break
    except subprocess.CalledProcessError:
        print(
            f"Warning: `pip show {package}` failed. Could not determine its dependencies.",
            file=sys.stderr,
        )
    return dependencies


def get_all_dependencies_for_packages(packages: Set[str]) -> Dict[str, Set[str]]:
    """For each package, finds all its transitive dependencies using `pip show`."""
    dependencies: Dict[str, Set[str]] = {pkg: set() for pkg in packages}

    for package in packages:
        direct_deps = get_direct_dependencies_from_pip(package)
        queue = list(direct_deps)
        package_deps = set(queue)
        processed = set([package])

        while queue:
            current_pkg = queue.pop(0)
            if current_pkg in processed:
                continue
            processed.add(current_pkg)

            sub_deps = get_direct_dependencies_from_pip(current_pkg)
            for dep in sub_deps:
                if dep not in processed:
                    package_deps.add(dep)
                    queue.append(dep)

        dependencies[package] = package_deps

    return dependencies


def find_missing_dependencies_with_path(
    primary_packages: Set[str], req_packages_set: Set[str]
) -> Dict[str, Dict[str, List[str]]]:
    """
    For each primary package, finds missing transitive dependencies and the path to them.
    Returns: {primary_pkg: {missing_dep: [path, to, dep]}}
    """
    missing_map: Dict[str, Dict[str, List[str]]] = {}
    for primary in primary_packages:
        if primary not in req_packages_set:
            continue

        queue: List[Tuple[str, List[str]]] = []
        for direct_dep in get_direct_dependencies_from_pip(primary):
            queue.append((direct_dep, [primary, direct_dep]))

        processed = set([primary])
        primary_missing_deps = {}

        while queue:
            current_pkg, path = queue.pop(0)
            if current_pkg in processed:
                continue
            processed.add(current_pkg)

            if current_pkg not in req_packages_set:
                if current_pkg not in primary_missing_deps:
                    primary_missing_deps[current_pkg] = path
                continue  # Stop digging deeper if a dependency is already missing

            for sub_dep in get_direct_dependencies_from_pip(current_pkg):
                if sub_dep not in processed:
                    new_path = path + [sub_dep]
                    queue.append((sub_dep, new_path))

        if primary_missing_deps:
            missing_map[primary] = primary_missing_deps

    return missing_map
