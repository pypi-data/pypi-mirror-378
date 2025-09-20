Req-Scanner: The Smart Requirements Tool 🐍Req-Scanner is a powerful command-line tool designed to bring sanity to your Python project's dependencies. It analyzes your project's imports, compares them against your requirements.txt file, and helps you create a clean, minimal, and accurate list of dependencies.Stop guessing which packages are really needed. Let req-scanner do the work for you. Key Features🎯 Accurate Import Detection: Uses Python's ast module to safely and accurately find all imported packages.🔍 Smart Dependency Analysis: Distinguishes between primary packages (directly imported) and their transitive dependencies. ✅ Comprehensive check command: Validates your requirements.txt against 4 crucial rules to ensure consistency. ✨ Clean generate command: Creates a perfect requirements.txt file from your project, optionally including all necessary dependencies. 🤖 CI/CD Friendly: Exits with a non-zero status code on errors, making it perfect for use in automated workflows.InstallationInstall req-scanner directly from PyPI:pip install req-scanner
Usagereq-scanner is simple to use and has two main commands: check and generate.check: Verify Your RequirementsThe check command is your best friend for maintaining a healthy requirements.txt. It verifies your project against 4 strict rules.# Run the check against the default requirements.txt
req-scanner check /path/to/your/project

# Specify a different requirements file
req-scanner check . --file dev-requirements.txt

# Ignore certain directories or files
req-scanner check . --ignore venv build "*.pyc"
The check command will report:❌ Error (Rule 2): Primary packages imported in your code but missing from the file.❌ Error (Rule 3): Primary packages that are missing their own dependencies in the file.❌ Error (Rule 4): Packages listed in the file that aren't installed in your environment.⚠️ Warning (Rule 1): Packages in the file that are never imported and are not dependencies.generate: Create a Perfect Requirements FileUse the generate command to create a clean requirements.txt from scratch based on your project's imports.# Generate a file with only primary (directly imported) packages
req-scanner generate /path/to/your/project -o minimal-reqs.txt

# Generate a complete file with all dependencies included (recommended)
req-scanner generate . --include-deps -o requirements.txt
ContributingContributions are welcome! Please feel free to open an issue or submit a pull request.LicenseThis project is licensed under the MIT License - see the LICENSE file for details.