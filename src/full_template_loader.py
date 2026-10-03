"""
Load a completed full PMO building template (see src/template_builder.py) and
convert every filled-in sheet into the same session data the individual pages
produce.
"""
import datetime
import re
import tarfile
import zipfile
from io import BytesIO
from pathlib import PurePosixPath

import pandas as pd

from src.template_builder import TEMPLATE_SECTIONS, schema_section
from src.transformer import (
    transform_library_sample_info,
    transform_mhap_info,
    transform_panel_info,
    transform_read_counts_per_stage,
    transform_specimen_info,
)
from src.utils import load_schema, parse_list_field

SECTION_BY_SHEET = {section["sheet"]: section for section in TEMPLATE_SECTIONS}
EXCEL_SUFFIXES = (".xlsx", ".xls")
TABLE_SUFFIXES = (".csv", ".tsv", ".txt")
ARCHIVE_SUFFIXES = (".zip", ".tar.gz", ".tgz", ".tar")
UPLOAD_TYPES = ["xlsx", "xls", "csv", "tsv", "txt", "gz", "zip", "tgz", "tar"]

# Sheets are stored in st.session_state under the keys the individual pages use.
# Genome Info is folded into the panel and Reads by Stage into the read counts.
SESSION_KEY_BY_SHEET = {
    "Panel Targets": "panel_info",
    "Microhaplotype": "microhaplotype_info",
    "Specimen Level": "specimen_info",
    "Project Info": "project_info",
    "Library Sample Info": "library_sample_info",
    "Sequencing Info": "seq_info",
    "Bioinformatics Methods": "bioinfo_methods_list",
    "Bioinformatics Run": "bioinfo_run_infos",
    "Raw Read Counts": "read_counts_per_stage",
}


def _clean_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp, datetime.date)):
        timestamp = pd.Timestamp(value)
        if timestamp == timestamp.normalize():
            return timestamp.strftime("%Y-%m-%d")
        return timestamp.isoformat()
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        return value.strip()
    return value


def _normalise_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


SHEET_BY_NORMALISED_NAME = {
    _normalise_name(name): section["sheet"]
    for section in TEMPLATE_SECTIONS
    for name in (section["sheet"], section["template_name"])
}


def sheet_for_file_name(file_name):
    """Template sheet matching a table file name, e.g. panel_targets.tsv or
    'Panel Targets.csv' or panel_info_template.csv, or None."""
    stem = PurePosixPath(file_name).name
    for suffix in (".gz", *TABLE_SUFFIXES):
        stem = stem[: -len(suffix)] if stem.lower().endswith(suffix) else stem
    normalised = _normalise_name(stem)
    normalised = normalised.removesuffix("template")
    return SHEET_BY_NORMALISED_NAME.get(normalised)


def _clean_sheets(tables):
    sheets = {}
    for name, df in tables.items():
        df = df.dropna(how="all").dropna(axis=1, how="all")
        if df.empty:
            continue
        df.columns = [str(c).strip() for c in df.columns]
        sheets[name] = df.astype(object).map(_clean_value)
    return sheets


def read_full_template(file) -> dict:
    """Return {sheet name: DataFrame} for every template sheet in an Excel
    workbook that contains data."""
    tables = pd.read_excel(file, sheet_name=None)
    return _clean_sheets({n: df for n, df in tables.items() if n in SECTION_BY_SHEET})


def _read_table(file_name, data):
    name = file_name.lower()
    compression = "gzip" if name.endswith(".gz") else None
    name = name.removesuffix(".gz")
    if name.endswith(".csv"):
        sep = ","
    elif name.endswith(".tsv"):
        sep = "\t"
    else:
        sep = None
    return pd.read_csv(BytesIO(data), sep=sep, engine="python", compression=compression)


def _archive_members(file_name, data):
    """Yield (member name, bytes) for files in a zip or tar archive."""
    if file_name.lower().endswith(".zip"):
        with zipfile.ZipFile(BytesIO(data)) as archive:
            for info in archive.infolist():
                if not info.is_dir():
                    yield info.filename, archive.read(info)
    else:
        with tarfile.open(fileobj=BytesIO(data)) as archive:
            for member in archive.getmembers():
                if member.isfile():
                    yield member.name, archive.extractfile(member).read()


def read_template_upload(files):
    """Read an uploaded template given as an Excel workbook, table files
    (CSV/TSV/TXT, optionally gzipped) named after the sheets, or a zip/tar
    archive of such files.

    Returns (sheets, ignored): sheets as for read_full_template, and the names
    of uploaded files that did not match a template sheet.
    """
    sheets, tables, ignored = {}, {}, []

    def add_table(file_name, data):
        base_name = PurePosixPath(file_name).name
        if base_name.startswith(".") or "__MACOSX" in file_name:
            return
        sheet = sheet_for_file_name(file_name)
        if sheet is None:
            ignored.append(file_name)
            return
        tables[sheet] = _read_table(file_name, data)

    for file in files:
        name = file.name
        lower = name.lower()
        data = file.getvalue()
        if lower.endswith(EXCEL_SUFFIXES):
            sheets.update(read_full_template(BytesIO(data)))
        elif lower.endswith(ARCHIVE_SUFFIXES):
            for member_name, member_data in _archive_members(name, data):
                add_table(member_name, member_data)
        else:
            add_table(name, data)

    sheets.update(_clean_sheets(tables))
    return sheets, ignored


def resolve_columns(df, sheet, schema=None):
    """Match the sheet's columns to schema fields by name or alternate name.

    Returns (required mapping, optional mapping, additional columns, missing
    required fields). Every optional field appears in the optional mapping,
    with None when the sheet has no matching column.
    """
    section = SECTION_BY_SHEET[sheet]
    fields = schema_section(schema or load_schema(), section["schema_path"])
    columns = {c.lower(): c for c in df.columns}
    used = set()

    def find(field, alternatives):
        for name in [field, *alternatives]:
            column = columns.get(name.lower())
            if column is not None and column not in used:
                used.add(column)
                return column
        return None

    required, missing = {}, []
    for field in fields["required"]:
        column = find(field, fields.get("required_alternatives", {}).get(field, []))
        if column is None:
            missing.append(field)
        required[field] = column
    optional = {
        field: find(field, fields.get("optional_alternatives", {}).get(field, []))
        for field in fields.get("optional", []) + section.get("link_fields", [])
    }
    additional = [c for c in df.columns if c not in used]
    return required, optional, additional, missing


def default_panel_name(sheets):
    """The single panel name used on the Library Sample Info sheet, if any."""
    return _single_value(sheets.get("Library Sample Info"), "panel_name")


def bioinformatics_run_names(sheets):
    """Run names listed on the Bioinformatics Run sheet."""
    df = sheets.get("Bioinformatics Run")
    if df is None or "bioinformatics_run_name" not in df.columns:
        return []
    return list(dict.fromkeys(df["bioinformatics_run_name"].dropna().astype(str)))


def _single_value(df, column):
    if df is None or column not in df.columns:
        return None
    values = df[column].dropna().astype(str).unique()
    return values[0] if len(values) == 1 else None


def _rows_to_dicts(df, mapping, additional, list_fields=()):
    """Convert rows to dicts keyed by PMO field, dropping blank values."""
    columns = {f: c for f, c in mapping.items() if c} | {c: c for c in additional}
    entries = []
    for _, row in df.iterrows():
        entry = {}
        for field, column in columns.items():
            value = row[column]
            if pd.isna(value) or value == "":
                continue
            if field in list_fields:
                value = parse_list_field(str(value))
                value = value if isinstance(value, list) else [value]
            else:
                value = str(value)
            entry[field] = value
        entries.append(entry)
    return entries


def _genome_info(df, schema):
    required, optional, additional, missing = resolve_columns(df, "Genome Info", schema)
    if missing:
        raise ValueError(f"Genome Info is missing required column(s): {missing}")
    genomes = _rows_to_dicts(
        df, required | optional, additional, list_fields=("taxon_id", "chromosomes")
    )
    for genome in genomes:
        genome["taxon_id"] = [int(t) for t in genome["taxon_id"]]
    return genomes


def _bioinformatics_methods(df, schema):
    required, optional, additional, missing = resolve_columns(
        df, "Bioinformatics Methods", schema
    )
    if missing:
        raise ValueError(f"missing required column(s): {missing}")
    group_col = optional.pop("bioinformatics_method_name")
    steps = _rows_to_dicts(
        df, required | optional, additional, list_fields=("additional_argument",)
    )
    for i, step in enumerate(steps, start=1):
        if not step.get("program") or not step.get("program_version"):
            raise ValueError(f"row {i} needs both program and program_version")
    if not group_col or df[group_col].isna().all():
        return [{"methods": steps}]
    if df[group_col].isna().any():
        raise ValueError(
            "bioinformatics_method_name must be filled for every row or left blank"
        )
    methods = {}
    for name, step in zip(df[group_col].astype(str), steps):
        methods.setdefault(name, []).append(step)
    return [
        {"bioinformatics_method_name": name, "methods": method_steps}
        for name, method_steps in methods.items()
    ]


def _bioinformatics_runs(df, methods, schema):
    required, optional, additional, missing = resolve_columns(
        df, "Bioinformatics Run", schema
    )
    if missing:
        raise ValueError(f"missing required column(s): {missing}")
    if not methods:
        raise ValueError("the Bioinformatics Methods sheet must also be filled in")
    method_col = optional.pop("bioinformatics_method_name")
    method_ids = {
        method.get("bioinformatics_method_name"): i for i, method in enumerate(methods)
    }
    runs = _rows_to_dicts(df, required | optional, additional)
    for run, (_, row) in zip(runs, df.iterrows()):
        method_name = row[method_col] if method_col else None
        if pd.isna(method_name) or method_name == "":
            if len(methods) > 1:
                raise ValueError(
                    f"run '{run['bioinformatics_run_name']}' needs a "
                    "bioinformatics_method_name because there are several pipelines"
                )
            run["bioinformatics_methods_id"] = 0
        elif str(method_name) in method_ids:
            run["bioinformatics_methods_id"] = method_ids[str(method_name)]
        else:
            raise ValueError(
                f"run '{run['bioinformatics_run_name']}' uses pipeline "
                f"'{method_name}', which is not on the Bioinformatics Methods sheet"
            )
    return runs


def load_full_template(sheets, panel_name=None, bioinformatics_run_name=None):
    """Convert template sheets to session data.

    Returns (data, errors): data maps st.session_state keys to the converted
    section, and errors maps sheet names to the reason they could not be loaded.
    Sheets are loaded independently, so one failing does not stop the others.
    """
    schema = load_schema()
    data, errors = {}, {}

    def columns(sheet):
        required, optional, additional, missing = resolve_columns(
            sheets[sheet], sheet, schema
        )
        if missing:
            raise ValueError(f"missing required column(s): {missing}")
        return required, optional, additional or None

    def load(sheet, build):
        if sheet not in sheets:
            return
        try:
            data[SESSION_KEY_BY_SHEET[sheet]] = build(sheets[sheet])
        except Exception as e:
            errors[sheet] = str(e)

    def panel(df):
        if not panel_name:
            raise ValueError("enter a panel name")
        genome = None
        if "Genome Info" in sheets:
            genome = _genome_info(sheets["Genome Info"], schema)
        required, optional, additional = columns("Panel Targets")
        return transform_panel_info(
            df, panel_name, required, genome, optional, additional
        )

    def mhap(df):
        return transform_mhap_info(
            df, bioinformatics_run_name or None, *columns("Microhaplotype")
        )

    def project(df):
        required, optional, additional = columns("Project Info")
        return _rows_to_dicts(
            df,
            required | optional,
            additional or [],
            list_fields=("project_contributors",),
        )

    def sequencing(df):
        required, optional, additional = columns("Sequencing Info")
        return _rows_to_dicts(df, required | optional, additional or [])

    def read_counts(df):
        raw_required, _, raw_additional = columns("Raw Read Counts")
        stage_df, stage_required, stage_additional = None, {}, None
        if "Reads by Stage" in sheets:
            stage_df = sheets["Reads by Stage"]
            stage_required, _, stage_additional = columns("Reads by Stage")
        return transform_read_counts_per_stage(
            df,
            stage_df,
            bioinformatics_run_name or None,
            raw_required,
            stage_required or {"target_name": None, "stage": None, "read_count": None},
            raw_additional,
            stage_additional,
        )

    load("Panel Targets", panel)
    load("Microhaplotype", mhap)
    load(
        "Specimen Level",
        lambda df: transform_specimen_info(df, *columns("Specimen Level")),
    )
    load("Project Info", project)
    load(
        "Library Sample Info",
        lambda df: transform_library_sample_info(df, *columns("Library Sample Info")),
    )
    load("Sequencing Info", sequencing)
    load(
        "Bioinformatics Methods",
        lambda df: _bioinformatics_methods(df, schema),
    )
    load(
        "Bioinformatics Run",
        lambda df: _bioinformatics_runs(df, data.get("bioinfo_methods_list"), schema),
    )
    load("Raw Read Counts", read_counts)

    if "Genome Info" in sheets and "Panel Targets" not in sheets:
        errors["Genome Info"] = "requires the Panel Targets sheet"
    if "Reads by Stage" in sheets and "Raw Read Counts" not in sheets:
        errors["Reads by Stage"] = "requires the Raw Read Counts sheet"
    return data, errors
