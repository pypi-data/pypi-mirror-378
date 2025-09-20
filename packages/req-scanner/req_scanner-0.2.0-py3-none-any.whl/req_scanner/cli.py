# -*- coding: utf-8 -*-
"""
Defines the command-line interface (CLI) for req-scanner,
including commands, arguments, and handlers.
"""

import argparse
import os
import sys

# Relative imports from other modules in the package
from .scanner import (
    find_project_imports,
    resolve_primary_packages,
    parse_requirements_file,
)
from .deps import (
    get_installed_packages,
    get_all_dependencies_for_packages,
    find_missing_dependencies_with_path,
)

# --- Constants ---
DEFAULT_REQUIREMENTS_FILE = "requirements.txt"


# --- Command Handler Functions ---


def handle_generate(args: argparse.Namespace) -> None:
    """Business logic for the 'generate' command."""
    print(f"1. Scanning for Python imports in '{os.path.abspath(args.path)}'...")
    project_imports = find_project_imports(args.path, args.ignore)
    primary_packages, unmapped = resolve_primary_packages(project_imports)

    if unmapped:
        print(
            "\nWarning: The following imported modules could not be mapped to any installed package and will be ignored:"
        )
        for imp in sorted(list(unmapped)):
            print(f"   - '{imp}'")

    print(
        f"   > Identified {len(primary_packages)} primary (directly imported) packages."
    )

    final_packages_to_write = set(primary_packages)
    if args.include_deps:
        print("2. Resolving all transitive dependencies for primary packages...")
        all_deps_map = get_all_dependencies_for_packages(primary_packages)
        for deps in all_deps_map.values():
            final_packages_to_write.update(deps)
        print(
            f"   > Total packages including dependencies: {len(final_packages_to_write)}"
        )

    print(f"3. Writing final package list to '{args.output}'...")
    installed_packages = get_installed_packages()
    final_requirements = {
        pkg: installed_packages[pkg]
        for pkg in sorted(list(final_packages_to_write))
        if pkg in installed_packages
    }

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            for package, version in final_requirements.items():
                f.write(f"{package}=={version}\n")
    except IOError as e:
        print(
            f"Error: Could not write to output file '{args.output}': {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\n✅ Success! Requirements file saved to '{os.path.abspath(args.output)}'.")


def handle_check(args: argparse.Namespace) -> None:
    """Business logic for the 'check' command, following the 4 rules."""
    print(f"1. Analyzing project at '{os.path.abspath(args.path)}'...")

    req_packages_set = parse_requirements_file(args.file)
    if req_packages_set is None:
        sys.exit(1)

    installed_packages_set = set(get_installed_packages().keys())
    project_imports = find_project_imports(args.path, args.ignore)
    primary_packages, unmapped = resolve_primary_packages(project_imports)

    exit_code = 0
    print("\n--- Consistency Report ---")

    if unmapped:
        print(
            "\n❌ Error: The following imported modules could not be mapped to any installed package:"
        )
        for imp in sorted(list(unmapped)):
            print(f"   - '{imp}'")
        print("   > Please ensure they are installed or are valid local modules.")
        exit_code = 1

    # Rule 4: Packages in req file but not installed
    uninstalled_packages = req_packages_set - installed_packages_set
    if uninstalled_packages:
        print("\n❌ Error (Rule 4): Packages in requirements file are NOT installed:")
        for pkg in sorted(list(uninstalled_packages)):
            print(f"   - {pkg}")
        exit_code = 1

    primary_packages_in_reqs = req_packages_set.intersection(primary_packages)

    # Rule 2: Primary packages imported but missing from req file
    primary_missing = primary_packages - req_packages_set
    if primary_missing:
        print(
            "\n❌ Error (Rule 2): Primary packages are IMPORTED but MISSING from requirements file:"
        )
        for pkg in sorted(list(primary_missing)):
            print(f"   - {pkg}")
        exit_code = 1

    # Rule 1: Packages in req file but not used or dependencies
    all_deps_map = get_all_dependencies_for_packages(primary_packages_in_reqs)
    all_needed_deps_set = set()
    for deps in all_deps_map.values():
        all_needed_deps_set.update(deps)
    potential_unused = req_packages_set - primary_packages - all_needed_deps_set
    if potential_unused:
        print(
            "\n⚠️ Warning (Rule 1): Packages in requirements file are not directly imported and are not dependencies of any primary package:"
        )
        for pkg in sorted(list(potential_unused)):
            print(f"   - {pkg}")

    # Rule 3: Dependency Missing
    print("\n2. Checking for missing dependencies for each primary package...")
    missing_deps_map = find_missing_dependencies_with_path(
        primary_packages_in_reqs, req_packages_set
    )
    if missing_deps_map:
        exit_code = 1
        for primary, missing_items in missing_deps_map.items():
            print(
                f"\n❌ Error (Rule 3): Primary package '{primary}' has missing dependencies in the requirements file:"
            )
            for missing, path in sorted(missing_items.items()):
                path_str = " -> ".join(path)
                print(f"   - Missing: {missing} (path: {path_str})")

    if exit_code == 0 and not potential_unused:
        print("\n✅ Success! Your requirements file passed all checks.")
    elif exit_code == 0:
        print(
            "\n✅ Success! Your requirements file passed all error checks (warnings were found)."
        )
    else:
        print("\n❌ Check failed. Please resolve the errors listed above.")

    sys.exit(exit_code)


# --- Main CLI Setup ---


def main() -> None:
    """Configures the command-line interface and executes the chosen command."""
    parser = argparse.ArgumentParser(
        description="A robust tool to manage Python project requirements.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="The command to execute."
    )

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "path",
        default=".",
        nargs="?",
        help="Path to the Python project (default: current directory).",
    )
    common_parser.add_argument(
        "--ignore",
        nargs="+",
        default=[
            "venv",
            ".venv",
            ".*",
            "*_test.py",
            "tests",
            "__pycache__",
            "*.egg-info",
        ],
        help="Space-separated list of glob patterns to ignore.",
    )

    parser_generate = subparsers.add_parser(
        "generate",
        help="Generate a requirements file from project imports.",
        parents=[common_parser],
    )
    parser_generate.add_argument(
        "-o",
        "--output",
        default=DEFAULT_REQUIREMENTS_FILE,
        help=f"Output file name (default: {DEFAULT_REQUIREMENTS_FILE}).",
    )
    parser_generate.add_argument(
        "--include-deps",
        action="store_true",
        help="Include all transitive dependencies of primary packages.",
    )
    parser_generate.set_defaults(func=handle_generate)

    parser_check = subparsers.add_parser(
        "check",
        help="Check for inconsistencies based on 4 strict rules.",
        parents=[common_parser],
    )
    parser_check.add_argument(
        "--file",
        "-f",
        default=DEFAULT_REQUIREMENTS_FILE,
        help=f"Requirements file to check against (default: {DEFAULT_REQUIREMENTS_FILE}).",
    )
    parser_check.set_defaults(func=handle_check)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)
