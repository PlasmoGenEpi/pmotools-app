# pmotools-app

This repository contains the code for an app built with Streamlit that helps users convert their data into the PMO format using the [`pmotools-python`](https://github.com/PlasmoGenEpi/pmotools-python) package.

Contents
- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [Developer Notes](#developer-notes)

## Features

- Convert your data to PMO (in development)
    - Upload your data files (CSV, TXT, or XLSX)
    - Converts the data into PMO format using `pmotools`
    - Download the converted data as PMO

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package and project manager)

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/PlasmoGenEpi/pmotools-python.git
   cd pmotools-app
   ```
2. Install uv and sync environment (if not already installed):
   ```bash
   pip install uv
   uv sync --dev
   ```

## Usage
Run the Streamlit app with uv:
```bash
uv run streamlit run PMO_Builder.py
```
## Developer Notes
- Install or update dependencies:
- Add: `uv add <package>`
- Remove: `uv remove <package>`
- Upgrade: `uv lock --upgrade` then `uv sync`
- Run pre-commit hooks (linting with ruff):
  ```bash
  uv run pre-commit run --all-files
  ```
- Install pre-commit hooks (run once):
  ```bash
  uv run pre-commit install
  ```
