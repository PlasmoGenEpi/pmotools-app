import pandas as pd
import streamlit as st

from src.format_page import render_header
from src.full_template_loader import (
    SECTION_BY_SHEET,
    SESSION_KEY_BY_SHEET,
    UPLOAD_TYPES,
    bioinformatics_run_names,
    default_panel_name,
    load_full_template,
    read_template_upload,
)
from src.template_builder import TEMPLATE_SECTIONS, XLSX_MIME, build_full_template

RUN_NAME_SHEETS = ("Microhaplotype", "Raw Read Counts")
CUSTOM_RUN_NAME = "Enter a different name"


def panel_name_input(sheets):
    if "Panel Targets" not in sheets:
        return None
    return st.text_input(
        "Panel name:",
        value=default_panel_name(sheets) or "",
        help="Identifier name for the panel. Must match panel_name on the Library Sample Info sheet.",
    )


def run_name_input(sheets):
    if not any(sheet in sheets for sheet in RUN_NAME_SHEETS):
        return None
    help_text = (
        "The bioinformatics run that produced the microhaplotypes and read counts."
    )
    run_names = bioinformatics_run_names(sheets)
    if run_names:
        selected = st.selectbox(
            "Bioinformatics run name:", run_names + [CUSTOM_RUN_NAME], help=help_text
        )
        if selected != CUSTOM_RUN_NAME:
            return selected
    return st.text_input("Bioinformatics run name (optional):", help=help_text)


def show_sheet_summary(sheets):
    summary = pd.DataFrame(
        [
            {
                "Sheet": sheet,
                "Rows": len(df),
                "App page": SECTION_BY_SHEET[sheet]["page"],
            }
            for sheet, df in sheets.items()
        ]
    )
    st.write("Filled-in sheets found:")
    st.dataframe(summary, hide_index=True)


def load_into_app(sheets, panel_name, run_name):
    data, errors = load_full_template(sheets, panel_name, run_name)
    for key, value in data.items():
        st.session_state[key] = value

    loaded = [s for s, key in SESSION_KEY_BY_SHEET.items() if key in data]
    loaded += [
        s for s in ("Genome Info", "Reads by Stage") if s in sheets and s not in errors
    ]
    if loaded:
        st.success(f"Loaded: {', '.join(s for s in sheets if s in loaded)}")
    for sheet, error in errors.items():
        st.error(f"Could not load {sheet}: {error}")
    if "panel_info" in data and "microhaplotype_info" in data:
        st.page_link(
            "app_pages/Create_Final_PMO.py",
            label="Continue to Create Final PMO",
            icon=":material/arrow_forward:",
        )


if __name__ in ("__main__", "__page__"):
    render_header()
    st.subheader("Load Full Template", divider="gray")
    st.markdown(
        """
        Fill in the PMO building template and upload it here to load every
        section at once, either as the Excel workbook or as CSV/TSV files.
        Only the **Panel Targets** and **Microhaplotype** sheets are required
        for a minimum PMO; the other sheets are optional. Sheets left empty are skipped, and column names are matched
        automatically. Loading replaces any data already entered on the pages
        for the sections you upload. If you only fill in the required sheets,
        you can add the optional sections afterwards on their own pages in the
        sidebar, by typing them in or uploading a table. You can also open any
        page afterwards to review or change a section.
        """
    )
    st.download_button(
        label="Download PMO Excel template",
        data=build_full_template(),
        file_name="PMO_building_template.xlsx",
        mime=XLSX_MIME,
        icon=":material/download:",
    )

    with st.expander("Using CSV or TSV files instead of Excel"):
        st.markdown(
            "Instead of the workbook, you can upload one CSV, TSV or TXT file per"
            " sheet: select all the files in your folder at once, or upload the"
            " folder as a .zip or .tar.gz file. Files can also be gzipped"
            " (e.g. `specimen_level.csv.gz`). Each file must be named after its"
            " sheet; case, spaces and underscores don't matter, and the"
            " single-page template names also work:"
        )
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Sheet": s["sheet"],
                        "Example file names": f"{s['sheet'].lower().replace(' ', '_')}.csv,"
                        f" {s['template_name']}.tsv",
                    }
                    for s in TEMPLATE_SECTIONS
                ]
            ),
            hide_index=True,
        )

    uploaded_files = st.file_uploader(
        "Upload completed template (Excel workbook, CSV/TSV files, or a .zip/.tar.gz folder)",
        type=UPLOAD_TYPES,
        accept_multiple_files=True,
    )
    if uploaded_files:
        try:
            sheets, ignored = read_template_upload(uploaded_files)
        except Exception as e:
            st.error(f"Could not read the upload: {e}")
            st.stop()
        if ignored:
            st.warning(
                "These files don't match a template sheet name and were ignored: "
                + ", ".join(ignored)
            )
        if not sheets:
            st.warning(
                "No filled-in template sheets found. Sheet and file names must"
                " match the PMO building template."
            )
            st.stop()

        show_sheet_summary(sheets)
        panel_name = panel_name_input(sheets)
        run_name = run_name_input(sheets)
        if st.button("Load into app", type="primary"):
            load_into_app(sheets, panel_name, run_name)
