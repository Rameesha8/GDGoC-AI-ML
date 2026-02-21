# Day 3: Python Tooling Practice

## Overview
This project contains the work completed on **Day 3** of the Git and Python tooling practice.
The focus of this day was on setting up a proper **Python development environment** and implementing **code quality tools** such as `ruff` and `pre-commit` hooks.

---

## Features

1. **Editable Package Installation**
   - The project can be installed in editable mode using:
     ```bash
     python -m pip install -e ".[dev]"
     ```
   - Development dependencies include `ruff` (for linting) and `pre-commit` (for hooks).

2. **Ruff Linting**
   - Static code analysis and formatting.
   - Run checks:
     ```bash
     ruff check .
     ```
   - Auto-fix issues:
     ```bash
     ruff check --fix .
     ```
   - Format code:
     ```bash
     ruff format .
     ```

3. **Pre-commit Hooks**
   - Automatically checks and fixes code before committing.
   - Installed via:
     ```bash
     pre-commit install
     ```
   - Run manually on all files:
     ```bash
     pre-commit run --all-files
     ```

---

## Project Structure
Day3/
├─ .gitignore
├─ README.md
├─ pyproject.toml
├─ .pre-commit-config.yaml
└─ src/git_day_practice/
       ├─ __init__.py
       ├─ app.py
       └─ bad_style.py─ bad_style.py



- **`pyproject.toml`**: Project configuration and dependencies.
- **`.pre-commit-config.yaml`**: Pre-commit hooks configuration.
- **`src/git_day_practice/`**: Source code for Day 3 exercises.

---

## How to Use

1. Activate the virtual environment:

   source .venv/bin/activate

2. Install the package with development dependencies:

python -m pip install -e ".[dev]"

3. Run ruff and pre-commit to ensure code quality:

ruff check .
pre-commit run --all-files

## Notes

- This setup ensures consistent code quality across the project.

- Pre-commit hooks automatically fix formatting issues such as trailing whitespace and end-of-file newlines.


