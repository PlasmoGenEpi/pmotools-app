import streamlit as st
import json
import os
from src.format_page import render_header
from pmotools.pmo_builder.merge_to_pmo import merge_to_pmo

check_dict = {
    "panel_info": "Panel Information",
    "specimen_info": "Specimen Level Metadata",
    "library_sample_info": "Library Sample Level Metadata",
    "microhaplotype_info": "Microhaplotype Information",
    "seq_info": "Sequencing Information",
    "bioinfo_run_infos": "Bioinformatics Runs Information",
    "read_counts_per_stage": "Read Counts per Stage",
}


def check_all(check_dict):
    """
    checks if outputs of a given page exists, and refers user to the page to
    populate if the page doesn't exist
    """
    all_passed = True
    for check_key, source_page in check_dict.items():
        if check_key in st.session_state:
            st.success(f"Data from {source_page} tab has been successfully loaded.")
        else:
            st.error(
                f"Data from {source_page} tab not found. Please fill out"
                f" the {source_page} tab (the link is at the left side of this"
                " page) before proceeding"
            )
            all_passed = False
    return all_passed


def merge_data():
    # MERGE DATA
    st.subheader("Merge Components to Final PMO")
    panel_info = st.session_state["panel_info"]

    # Get bioinformatics methods and runs
    bioinfo_methods = st.session_state.get("bioinfo_methods_list", [])
    bioinfo_runs = st.session_state.get("bioinfo_run_infos", [])
    if "read_counts_per_stage" in st.session_state:
        read_counts_per_stage = st.session_state["read_counts_per_stage"]
    else:
        read_counts_per_stage = None
    if st.button("Merge Data"):
        try:
            st.session_state["formatted_pmo"] = merge_to_pmo(
                specimen_info=st.session_state["specimen_info"],
                library_sample_info=st.session_state["library_sample_info"],
                sequencing_info=st.session_state["seq_info"],
                panel_info=panel_info,
                mhap_info=st.session_state["microhaplotype_info"],
                bioinfo_method_info=bioinfo_methods,
                bioinfo_run_info=bioinfo_runs,
                project_info=st.session_state["project_info"],
                read_counts_by_stage_info=read_counts_per_stage,
            )
            st.success("Data merged successfully!")
        except Exception as e:
            st.error(f"Error merging data: {e}")

    # Download button - only show if PMO has been created
    if "formatted_pmo" in st.session_state:
        st.subheader("Download PMO File")

        # Convert the PMO data to JSON string
        pmo_json = json.dumps(st.session_state["formatted_pmo"], indent=2, default=str)

        # Create download button
        st.download_button(
            label="Download PMO JSON File",
            data=pmo_json,
            file_name="pmo_data.json",
            mime="application/json",
            help="Download the merged PMO data as a JSON file",
        )

        # Optional: Show preview of the data
        with st.expander("Preview PMO Data"):
            st.json(st.session_state["formatted_pmo"])


# Initialize and run the app
if __name__ == "__main__":
    current_directory = os.getcwd()  # Get the current working directory
    SAVE_DIR = os.path.join(current_directory, "finished_PMO_files")
    os.makedirs(SAVE_DIR, exist_ok=True)
    render_header()
    st.subheader("Create Final PMO", divider="gray")
    st.subheader("Components")
    if check_all(check_dict):
        merge_data()
