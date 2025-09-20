# Req-Scanner: The Smart Python Requirements Tool 🐍

[![PyPI version](https://badge.fury.io/py/req-scanner.svg)](https://badge.fury.io/py/req-scanner)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Req-Scanner** is a powerful command-line tool designed to bring sanity to your Python project's dependencies. It analyzes your project's imports, compares them against your `requirements.txt` file, and helps you create a clean, minimal, and accurate list of dependencies.

Stop guessing which packages are *really* needed. Let `req-scanner` do the work for you.

---

### What is Req-Scanner?

Manually managing a `requirements.txt` file is error-prone. You might forget to add a new import, leave behind unused packages, or miss a critical sub-dependency. `Req-Scanner` solves these problems by automating the analysis and validation process, ensuring your requirements file is always a perfect reflection of your project's actual needs.

It's built on a clear philosophy: distinguish between **primary packages** (what you directly `import`) and their **dependencies** (what *they* need to run). This allows for highly accurate and logical consistency checks.

### Key Features

-   **🎯 Accurate Import Detection:** Uses Python's Abstract Syntax Tree (`ast`) module to safely and precisely find all imported packages.
-   **🔍 Smart Dependency Analysis:** Leverages `pip`'s own resolver (via `pip show`) to accurately determine the real-world dependencies for your specific environment, correctly handling conditional and optional dependencies.
-   **✅ Comprehensive `check` Command:** Validates your `requirements.txt` against 4 crucial, strict rules to ensure perfect consistency with your codebase.
-   **✨ Clean `generate` Command:** Creates a flawless `requirements.txt` from scratch based on your project's actual imports, with optional inclusion of all transitive dependencies.
-   **🤖 CI/CD Friendly:** Exits with a non-zero status code on critical errors, making it ideal for integration into automated workflows like GitHub Actions.

---

### Installation

Install `req-scanner` directly from PyPI:

```bash
pip install req-scanner
````

-----

### Usage Guide

`req-scanner` has two main commands: `generate` and `check`. Both commands share the following options:

  - `path`: The path to your project directory (default: current directory).
  - `--ignore`: A space-separated list of file or directory patterns to ignore during the scan (e.g., `venv "*.pyc"`).

#### 1\. `generate`: Create a Perfect Requirements File

Use the `generate` command to create a clean `requirements.txt` from scratch based on your project's actual usage. This is the perfect starting point for any project.

**Command Signature:**

```bash
req-scanner generate [path] [--output <filename>] [--include-deps] [--ignore <patterns...>]
```

**Options:**

  - `--output <filename>` or `-o <filename>`: The name of the file to be created (default: `requirements.txt`).
  - `--include-deps`: If specified, the output file will contain both the primary packages and all of their transitive dependencies. This is **highly recommended** for creating fully reproducible environments.

**Examples:**

```bash
# Generate a complete, reproducible file named requirements.txt
req-scanner generate . --include-deps

# Generate a file with only primary (directly imported) packages
req-scanner generate . -o minimal-reqs.txt
```

#### 2\. `check`: Verify Your Requirements File

Once you have a `requirements.txt`, the `check` command is your best friend for maintaining it. It audits your project based on 4 strict rules to find inconsistencies.

**Command Signature:**

```bash
req-scanner check [path] [--file <filename>] [--ignore <patterns...>]
```

**Options:**

  - `--file <filename>` or `-f <filename>`: Specifies the requirements file to check against (default: `requirements.txt`).

**The 4 Rules of the `check` command:**

  - **❌ Error (Rule 2: Primary Missing):** Reports primary packages that are imported in your code but are missing from the requirements file.
  - **❌ Error (Rule 3: Dependency Missing):** Reports primary packages that are present, but their own dependencies are missing from the file. It even shows the dependency path\!
  - **❌ Error (Rule 4: Not Installed):** Reports packages listed in the file that aren't actually installed in your virtual environment.
  - **⚠️ Warning (Rule 1: Unused Package):** Warns about packages in the file that are never directly imported and are not dependencies of any other primary package.

**Examples:**

```bash
# Check the default requirements.txt in the current directory
req-scanner check .

# Check a different requirements file
req-scanner check . --file dev-requirements.txt

# Check a project in another folder, ignoring the 'build' directory
req-scanner check /path/to/project --ignore build
```

-----

### Contributing

Contributions are welcome\! Please feel free to open an issue or submit a pull request on the GitHub repository.

### License

This project is licensed under the MIT License - see the `LICENSE` file for details.
