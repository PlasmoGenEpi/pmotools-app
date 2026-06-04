# PMO Builder (pmotools-app)

A [Streamlit](https://streamlit.io/) app that helps you build **PMO** (Portable Microhaplotype Object) files from your own tabular data. The app guides you through entering or uploading data, mapping fields to the PMO schema, and merging everything into a validated PMO JSON file. Conversion and validation use the [`pmotools`](https://pypi.org/project/pmotools/) package ([source](https://github.com/PlasmoGenEpi/pmotools-python)).

## Documentation

**More information:** [PMO Builder app documentation](https://plasmogenepi.github.io/PMO_Docs/pmotools-app-usage/pmotools-app.html)

For the PMO file format and schema, see the [PMO documentation site](https://plasmogenepi.github.io/PMO_Docs/).

## Contents

- [Features](#features)
- [Workflow](#workflow)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [Web deployment](#web-deployment)
- [Project layout](#project-layout)
- [Developer notes](#developer-notes)

## Features

- Build PMOs section by section via a guided multipage UI
- Upload tables (CSV, TSV, Excel) or enter data manually
- Map your column names to PMO fields with fuzzy matching
- Save progress for reusable sections (e.g. panel definitions)
- Merge required and optional sections and export a PMO JSON file
- Validate output against the PMO schema before download

### Required sections

- **Panel Information** — targets, primers, and panel metadata
- **Microhaplotype Information** — allele calls and read counts per sample

### Optional sections

- Specimen-level metadata (recommended)
- Project information
- Library sample metadata
- Sequencing information
- Bioinformatics run information
- Read counts per pipeline stage

Use **Create Final PMO** to combine saved sections and download the result.

## Workflow

1. Start with **Panel Information**, then **Microhaplotype Information**.
2. Add any optional sections you need.
3. For each section: enter or upload data → map fields → save (optional).
4. Open **Create Final PMO** to merge, validate, and export.

Example files and an Excel template are in `example_data/`. The app home page also offers a downloadable PMO building template.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended for installs and locked dependencies)

## Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/PlasmoGenEpi/pmotools-app.git
   cd pmotools-app
   ```

2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if needed, then sync dependencies:

   ```bash
   uv sync
   ```

   For development (tests, coverage):

   ```bash
   uv sync --extra test
   ```

## Usage

Run the app from the repository root:

```bash
uv run streamlit run PMO_Builder.py
```

Open the URL shown in the terminal (typically `http://localhost:8501`). Use the sidebar to move between sections.

## Web deployment

You can use this app without installing Python locally. The [pmotool-app-web](https://github.com/PlasmoGenEpi/pmotool-app-web) repository packages **pmotools-app** as a browser-only app using [stlite](https://github.com/whitphx/stlite) (Streamlit compiled to WebAssembly via Pyodide).

- **Live app:** [https://pmotools.app/](https://pmotools.app/) (also [GitHub Pages](https://plasmogenepi.github.io/pmotool-app-web/))
- **Source & build:** [PlasmoGenEpi/pmotool-app-web](https://github.com/PlasmoGenEpi/pmotool-app-web)

That repo keeps `pmotools-app` as a [git submodule](https://github.com/PlasmoGenEpi/pmotool-app-web/blob/main/.gitmodules), bundles the Streamlit code into a single static `index.html`, and serves it from the `docs/` folder. Python dependencies for the browser build are derived from this project’s `pyproject.toml` (with `streamlit` omitted for stlite and versions resolved for Pyodide).

To update the public web app after changes here:

1. Merge or tag changes in **pmotools-app**.
2. In **pmotool-app-web**, update the submodule (`git submodule update --remote pmotools-app`), rebuild (`make build`), and deploy the built site.

See the [pmotool-app-web README](https://github.com/PlasmoGenEpi/pmotool-app-web#readme) for setup, `make serve` local preview, and stlite upgrade steps.

## Project layout

| Path | Description |
|------|-------------|
| `PMO_Builder.py` | Streamlit entrypoint and navigation |
| `app_pages/` | Individual app sections (not Streamlit’s auto `pages/` folder) |
| `src/` | Shared UI and data transformation helpers |
| `example_data/` | Sample inputs and PMO building template |
| `tests/` | Pytest suite |

## Developer notes

**Dependencies**

- Add: `uv add <package>`
- Remove: `uv remove <package>`
- Upgrade: `uv lock --upgrade-package <package>` then `uv sync`

Commit `uv.lock` with dependency changes so installs stay reproducible.

**Tests**

```bash
uv run --extra test pytest tests/ -v
```

**Pre-commit**

```bash
uv run pre-commit install          # once
uv run pre-commit run --all-files
```
