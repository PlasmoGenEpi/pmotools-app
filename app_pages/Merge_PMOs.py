import gzip
import json
import warnings

import pandas as pd
import streamlit as st

from src.format_page import render_header
from src.pmo_merger import (
    UPLOAD_TYPES,
    available_schema_versions,
    merge_pmos,
    read_pmo_uploads,
    summarise_pmo,
    validate_pmo,
)

MERGED_KEY = "merged_pmo"


class _NamedBytes:
    def __init__(self, name, data):
        self.name = name
        self._data = data

    def getvalue(self):
        return self._data


@st.cache_data(show_spinner="Reading PMO files...")
def load_uploads(uploads):
    """Read and validate uploaded PMO files, given as (name, bytes) pairs."""
    pmos, ignored, errors = read_pmo_uploads([_NamedBytes(n, d) for n, d in uploads])
    validation = {name: validate_pmo(pmo) for name, pmo in pmos}
    return pmos, ignored, errors, validation


def show_uploaded_pmos(pmos, validation):
    rows = [
        {
            "File": name,
            **summarise_pmo(pmo),
            "Valid": "Yes" if validation[name] is None else "No",
        }
        for name, pmo in pmos
    ]
    st.write(f"PMO files found: {len(pmos)}")
    st.dataframe(pd.DataFrame(rows), hide_index=True)
    invalid = {name: error for name, error in validation.items() if error}
    if invalid:
        with st.expander(
            f"{len(invalid)} file(s) failed schema validation", expanded=True
        ):
            st.warning(
                "You can still try to merge these files, but the merged PMO may"
                " not be valid."
            )
            for name, error in invalid.items():
                st.markdown(f"**{name}**: {error}")


def merge(pmos, upload_key):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            merged = merge_pmos(pmos)
        except Exception as e:
            st.session_state.pop(MERGED_KEY, None)
            st.error("Could not merge the PMOs:")
            st.code(str(e), language="text")
            return
    st.session_state[MERGED_KEY] = {"pmo": merged, "upload_key": upload_key}
    for w in caught:
        st.warning(str(w.message))


def show_merged(merged):
    st.subheader("Merged PMO", divider="gray")
    summary = summarise_pmo(merged)
    for column, (label, count) in zip(st.columns(len(summary)), summary.items()):
        column.metric(label, count)

    versions = available_schema_versions()
    version = st.selectbox(
        "Validate against schema version", versions, index=len(versions) - 1
    )
    error = validate_pmo(merged, version)
    if error:
        st.error(f"The merged PMO failed schema validation: {error}")
    else:
        st.success(f"The merged PMO is valid against schema v{version}.")

    file_name = st.text_input("File name", value="merged_pmo")
    compress = st.checkbox("Compress (.json.gz)", value=True)
    data = json.dumps(merged, indent=2, default=str).encode()
    if compress:
        data = gzip.compress(data)
    file_name = file_name.removesuffix(".gz").removesuffix(".json")
    st.download_button(
        label="Download merged PMO",
        data=data,
        file_name=f"{file_name}.json{'.gz' if compress else ''}",
        mime="application/gzip" if compress else "application/json",
        icon=":material/download:",
        type="primary",
    )


if __name__ in ("__main__", "__page__"):
    render_header()
    st.subheader("Merge PMO Files", divider="gray")
    st.markdown(
        """
        Combine several PMO files into one, for example PMOs from different
        sequencing runs or sites that used the same panel. Upload the PMO
        files (`.json` or `.json.gz`): select all the files in a folder at
        once, or upload the folder as a `.zip` or `.tar.gz` file.

        When merging:
        - Targets, panels and genomes with the same name are combined.
        - Every library sample name must be unique across the files.
        - A specimen can appear in more than one file only if its metadata is
          identical in each.
        - Projects with the same name must have the same description.
        - Sequencing information, bioinformatics methods and runs are kept
          from every file.
        """
    )

    uploaded_files = st.file_uploader(
        "Upload PMO files (.json, .json.gz, or a .zip/.tar.gz folder)",
        type=UPLOAD_TYPES,
        accept_multiple_files=True,
    )
    if not uploaded_files:
        st.session_state.pop(MERGED_KEY, None)
        st.stop()

    uploads = tuple((f.name, f.getvalue()) for f in uploaded_files)
    upload_key = tuple((name, len(data)) for name, data in uploads)
    try:
        pmos, ignored, errors, validation = load_uploads(uploads)
    except Exception as e:
        st.error(f"Could not read the upload: {e}")
        st.stop()

    if ignored:
        st.warning(
            "These files are not PMO files (.json or .json.gz) and were ignored: "
            + ", ".join(ignored)
        )
    for name, error in errors.items():
        st.error(f"Could not read {name}: {error}")
    if not pmos:
        st.stop()

    show_uploaded_pmos(pmos, validation)
    if len(pmos) < 2:
        st.info("Upload at least two PMO files to merge.")
        st.stop()

    if st.button("Merge PMOs", type="primary"):
        with st.spinner("Merging..."):
            merge(pmos, upload_key)

    merged = st.session_state.get(MERGED_KEY)
    if merged and merged["upload_key"] == upload_key:
        show_merged(merged["pmo"])
