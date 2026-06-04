import streamlit as st
import json
import os
from src.format_page import render_header
from pmotools.pmo_builder.merge_to_pmo import merge_to_pmo
from jsonschema import ValidationError
from pmotools.pmo_engine.pmo_checker import PMOChecker, load_schema


optional_check_dict = {
    "project_info": "Project Information",
    "specimen_info": "Specimen Level Metadata",
    "library_sample_info": "Library Sample Level Metadata",
    "seq_info": "Sequencing Information",
    "bioinfo_run_infos": "Bioinformatics Runs Information",
    "read_counts_per_stage": "Read Counts per Stage",
}

check_dict = {
    "panel_info": "Panel Information",
    "microhaplotype_info": "Microhaplotype Information",
}


def check_all(check_dict, optional_check_dict):
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
    for check_key, source_page in optional_check_dict.items():
        if check_key in st.session_state:
            st.success(f"Data from {source_page} tab has been successfully loaded.")
        else:
            st.warning(
                f"Optional Data from {source_page} not found, will not be included in PMO"
            )
    return all_passed


def merge_data():
    # MERGE DATA
    st.subheader("Merge Components to Final PMO")
    panel_info = st.session_state["panel_info"]

    # Get bioinformatics methods and runs if present
    bioinfo_methods = None
    if "bioinfo_methods_list" in st.session_state:
        bioinfo_methods = st.session_state.get("bioinfo_methods_list", [])
    bioinfo_runs = None
    if "bioinfo_methods_list" in st.session_state:
        bioinfo_runs = st.session_state.get("bioinfo_run_infos", [])
    if "read_counts_per_stage" in st.session_state:
        read_counts_per_stage = st.session_state["read_counts_per_stage"]
    else:
        read_counts_per_stage = None
    if "project_info" in st.session_state:
        project_info = st.session_state["project_info"]
    else:
        project_info = None
    if "seq_info" in st.session_state:
        seq_info = st.session_state["seq_info"]
    else:
        seq_info = None
    if st.button("Merge Data"):
        try:
            if (
                "specimen_info" not in st.session_state
                and "library_sample_info" not in st.session_state
            ):
                spec_info = None
                lib_info = None
            elif (
                "specimen_info" in st.session_state
                and "library_sample_info" not in st.session_state
            ):
                spec_info = st.session_state["specimen_info"]
                lib_info = None
            elif (
                "specimen_info" not in st.session_state
                and "library_sample_info" in st.session_state
            ):
                # in this instance, the default specimen_info will just bhe library_sample_info 1:1
                spec_info = None
                lib_info = st.session_state["library_sample_info"]
            else:
                spec_info = st.session_state["specimen_info"]
                lib_info = st.session_state["library_sample_info"]
            st.session_state["formatted_pmo"] = merge_to_pmo(
                specimen_info=spec_info,
                library_sample_info=lib_info,
                sequencing_info=seq_info,
                panel_target_info=panel_info,
                mhap_info=st.session_state["microhaplotype_info"],
                bioinfo_method_info=bioinfo_methods,
                bioinfo_run_info=bioinfo_runs,
                project_info=project_info,
                read_counts_by_stage_info=read_counts_per_stage,
            )
            st.success("Data merged successfully!")

            # --- Merge summary ---
            pmo = st.session_state["formatted_pmo"]

            def _count(key, nested_key=None):
                """Return len of pmo[key] or pmo[key][nested_key], defaulting to 0."""
                val = pmo.get(key)
                if val is None:
                    return 0
                if nested_key is not None:
                    val = val.get(nested_key) if isinstance(val, dict) else None
                    if val is None:
                        return 0
                return len(val) if hasattr(val, "__len__") else 0

            # Always-present fields
            library_samples_with_detected_count = 0
            for detected in pmo.get("detected_microhaplotypes", []):
                library_samples_with_detected_count += len(detected["library_samples"])

            always_present = [
                (_count("specimen_info"), "specimen(s)"),
                (_count("library_sample_info"), "library sample(s)"),
                (
                    library_samples_with_detected_count,
                    "library sample(s) with detected microhaplotypes",
                ),
                (_count("panel_info"), "panel(s)"),
                (_count("target_info"), "target(s)"),
                (
                    _count("representative_microhaplotypes", "targets"),
                    "target(s) with microhaplotype calls",
                ),
            ]
            library_samples_with_read_counts_per_stage = 0
            for reads_by_stage in pmo.get("read_counts_by_stage", []):
                library_samples_with_read_counts_per_stage += len(
                    reads_by_stage["read_counts_by_library_sample_by_stage"]
                )

            # Optional fields (show 0 if absent)
            optional = [
                (_count("targeted_genomes"), "genome(s)"),
                (_count("sequencing_info"), "sequencing run(s)"),
                (_count("project_info"), "project(s)"),
                (_count("bioinformatics_run_info"), "bioinformatics run(s)"),
                (
                    library_samples_with_read_counts_per_stage,
                    "library sample(s) with read counts per stage",
                ),
            ]

            st.markdown("**Merge Summary**")
            for count, label in always_present + optional:
                st.markdown(f"- Loaded **{count}** {label}")
        except Exception as e:
            with st.expander("Error merging data", expanded=True):
                st.error(str(e))

    # Download button - only show if PMO has been created
    if "formatted_pmo" in st.session_state:
        # Validate PMO
        st.subheader("Validate PMO File")
        avail_versions = ["v1.0.0", "v1.1.0"]
        schema_version = st.selectbox(
            "Select schema version", avail_versions, index=len(avail_versions) - 1
        )

        if st.button("Validate PMO against schema"):
            try:
                pmo_jsonschema_data_ = load_schema(
                    f"portable_microhaplotype_object_{schema_version}.schema.json"
                )
                pmo_checker = PMOChecker(pmo_jsonschema_data_)
                pmo_checker.validate_pmo_json(st.session_state["formatted_pmo"])
                st.success("✅ Valid PMO — passed schema validation.")
            except ValidationError as e:
                # Build a detailed error message matching the CLI output
                path_str = (
                    " -> ".join(str(p) for p in e.absolute_path)
                    if e.absolute_path
                    else "root"
                )
                schema_path_str = " -> ".join(str(p) for p in e.absolute_schema_path)
                detailed_msg = (
                    f"**Message:** {e.message}\n\n"
                    f"**Instance path:** `{path_str}`\n\n"
                    f"**Schema path:** `{schema_path_str}`\n\n"
                    f"**Failing value:** `{e.instance}`"
                )
                st.error("❌ Schema validation failed:")
                st.markdown(detailed_msg)
                with st.expander("Full validation error", expanded=True):
                    st.code(str(e), language="text")
            except Exception as e:
                st.error(f"❌ Validation error: {e}")

        st.subheader("Download PMO File")

        # Convert the PMO data to JSON string
        pmo_json = json.dumps(st.session_state["formatted_pmo"], indent=2, default=str)

        # Create a download button
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
if __name__ in ("__main__", "__page__"):
    current_directory = os.getcwd()  # Get the current working directory
    SAVE_DIR = os.path.join(current_directory, "finished_PMO_files")
    os.makedirs(SAVE_DIR, exist_ok=True)
    render_header()
    st.subheader("Create Final PMO", divider="gray")
    st.subheader("Components")
    if check_all(check_dict, optional_check_dict):
        merge_data()
