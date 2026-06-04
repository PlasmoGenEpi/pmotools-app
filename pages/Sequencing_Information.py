import streamlit as st
import pandas as pd
from src.format_page import render_header
from src.field_matcher import load_data
from src.utils import load_schema


class SeqInfoPage:
    def __init__(
        self,
        required_fields,
        required_alternate_fields,
        optional_fields,
        optional_alternate_fields,
    ):
        self.required_fields = required_fields
        self.required_alternate_fields = required_alternate_fields
        self.optional_fields = optional_fields
        self.optional_alternate_fields = optional_alternate_fields

    def _show_runs_count(self):
        """Show current sequencing runs count."""
        if st.session_state.get("seq_info"):
            st.info(f"Current sequencing runs: {len(st.session_state['seq_info'])}")
            st.info(
                "To add another sequencing run, enter the information above and click the 'Add Sequencing Information' button again."
            )

    def _get_sequencing_info_name_input(self):
        """Get sequencing information name - either from library_sample_info or manual entry."""
        suggested_names = []
        if "library_sample_info" in st.session_state:
            library_sample_info = st.session_state["library_sample_info"]
            try:
                if isinstance(library_sample_info, pd.DataFrame):
                    if "sequencing_info_name" in library_sample_info.columns:
                        suggested_names = sorted(
                            library_sample_info["sequencing_info_name"]
                            .dropna()
                            .unique()
                            .tolist()
                        )
                elif isinstance(library_sample_info, dict):
                    if "sequencing_info_name" in library_sample_info:
                        seq_data = library_sample_info["sequencing_info_name"]
                        if isinstance(seq_data, (list, pd.Series)):
                            if isinstance(seq_data, pd.Series):
                                suggested_names = sorted(
                                    seq_data.dropna().unique().tolist()
                                )
                            else:
                                suggested_names = sorted(
                                    list(set([s for s in seq_data if s]))
                                )
                    else:
                        for value in library_sample_info.values():
                            if (
                                isinstance(value, pd.DataFrame)
                                and "sequencing_info_name" in value.columns
                            ):
                                suggested_names.extend(
                                    value["sequencing_info_name"]
                                    .dropna()
                                    .unique()
                                    .tolist()
                                )
                        suggested_names = sorted(list(set(suggested_names)))
                elif isinstance(library_sample_info, list):
                    seq_names = [
                        item.get("sequencing_info_name")
                        for item in library_sample_info
                        if isinstance(item, dict) and item.get("sequencing_info_name")
                    ]
                    suggested_names = sorted(list(set(seq_names)))
            except Exception:
                pass

        if suggested_names:
            name_options = suggested_names + ["Enter custom name"]
            selected_option = st.selectbox(
                "Select sequencing information name or enter custom:",
                name_options,
                index=0,
                help=f"Suggested names from library sample info: {', '.join(suggested_names)}",
                key="seq_info_name_select",
            )
            if selected_option == "Enter custom name":
                return st.text_input(
                    "Enter sequencing information name:",
                    help="A unique identifier for this sequencing info.",
                    key="seq_info_name_text",
                )
            return selected_option
        else:
            return st.text_input(
                "Sequencing Information Name:",
                help="A unique identifier for this sequencing info.",
                key="seq_info_name_text",
            )

    def add_manual_sequencing_information(self):
        """Add sequencing information via manual text inputs."""
        self._show_runs_count()
        seq_info = {}

        seq_info["sequencing_info_name"] = self._get_sequencing_info_name_input()
        seq_info["seq_platform"] = st.text_input(
            "Sequencing Platform:",
            help="The sequencing platform used to sequence the run, e.g. ILLUMINA, Illumina MiSeq.",
            key="seq_platform",
        )
        seq_info["seq_instrument_model"] = st.text_input(
            "Sequencing Instrument Model:",
            help="The sequencing instrument model used to sequence the run, e.g. Illumina MiSeq.",
            key="seq_instrument_model",
        )
        seq_info["library_layout"] = st.text_input(
            "Library Layout:",
            help="Specify the configuration of reads, e.g. paired-end.",
            key="library_layout",
        )
        seq_info["library_strategy"] = st.text_input(
            "Library Strategy:",
            help="The strategy used to prepare the library, e.g. WGS, WES, amplicon, etc.",
            key="library_strategy",
        )
        seq_info["library_source"] = st.text_input(
            "Library Source:",
            help="The source of the library, e.g. DNA, RNA, etc.",
            key="library_source",
        )
        seq_info["library_selection"] = st.text_input(
            "Library Selection:",
            help="The selection method used to prepare the library, e.g. PCR, etc.",
            key="library_selection",
        )

        st.write("**Optional Fields:**")
        seq_info["library_kit"] = st.text_input(
            "Library Kit (Optional):",
            help="Name, version, and applicable cell or cycle numbers for the kit used to prepare libraries.",
            key="library_kit",
        )
        seq_info["library_screen"] = st.text_input(
            "Library Screen (Optional):",
            help="Describe enrichment, screening, or normalization methods applied during amplification or library preparation.",
            key="library_screen",
        )
        seq_info["nucl_acid_amp"] = st.text_input(
            "Nucleic Acid Amplification (Optional):",
            help="Link to a reference or kit that describes the enzymatic amplification of nucleic acids.",
            key="nucl_acid_amp",
        )
        seq_info["nucl_acid_ext"] = st.text_input(
            "Nucleic Acid Extraction (Optional):",
            help="Link to a reference or kit that describes the recovery of nucleic acids from the sample.",
            key="nucl_acid_ext",
        )
        seq_info["nucl_acid_ext_date"] = st.date_input(
            "Nucleic Acid Extraction Date (Optional):",
            value=None,
            help="The date of the nucleoacide extraction.",
            key="nucl_acid_ext_date",
        )
        seq_info["nucl_acid_amp_date"] = st.date_input(
            "Nucleic Acid Amplification Date (Optional):",
            value=None,
            help="The date of the nucleoacide amplification.",
            key="nucl_acid_amp_date",
        )
        seq_info["pcr_cond"] = st.text_input(
            "PCR Conditions (Optional):",
            help="The method/conditions for PCR, List PCR cycles used to amplify the target.",
            key="pcr_cond",
        )
        seq_info["seq_center"] = st.text_input(
            "Sequencing Center (Optional):",
            help="Name of facility where sequencing was performed.",
            key="seq_center",
        )
        seq_info["seq_date"] = st.date_input(
            "Sequencing Date (Optional):",
            value=None,
            help="The date of sequencing, should be YYYY-MM or YYYY-MM-DD.",
            key="seq_date",
        )

        # Convert date objects to strings if they exist
        for date_field in ["seq_date", "nucl_acid_ext_date", "nucl_acid_amp_date"]:
            if seq_info[date_field] is not None:
                seq_info[date_field] = str(seq_info[date_field])

        # Remove empty optional fields
        cleaned_seq_info = {
            k: v for k, v in seq_info.items() if v is not None and v != ""
        }
        return cleaned_seq_info

    def add_upload_sequencing_information(self):
        """Add sequencing information via file upload and field mapping."""
        (
            df,
            mapped_fields,
            selected_optional_fields,
            selected_additional_fields,
        ) = load_data(
            self.required_fields,
            self.required_alternate_fields,
            self.optional_fields,
            self.optional_alternate_fields,
            key_suffix="seq_info",
        )
        return df, mapped_fields, selected_optional_fields, selected_additional_fields

    def _validate_sequencing_info(self, seq_info):
        """Validate that all required fields are filled."""
        required_fields = [
            "sequencing_info_name",
            "seq_platform",
            "seq_instrument_model",
            "library_layout",
            "library_strategy",
            "library_source",
            "library_selection",
        ]
        missing_fields = [
            f
            for f in required_fields
            if not seq_info.get(f) or not str(seq_info[f]).strip()
        ]
        if missing_fields:
            msg = (
                f"Missing required field: {missing_fields[0]}."
                if len(missing_fields) == 1
                else f"Missing required fields: {', '.join(missing_fields)}."
            )
            return False, [msg]
        return True, []

    def _save_manual_sequencing_info(self, seq_info):
        """Save a single manually entered sequencing run to session state."""
        if st.button("Add Sequencing Information", key="save_seq_info"):
            is_valid, errors = self._validate_sequencing_info(seq_info)
            if not is_valid:
                for error in errors:
                    st.error(error)
                st.warning("Please fill in all required fields before saving.")
            else:
                if "seq_info" not in st.session_state:
                    st.session_state["seq_info"] = []
                st.session_state["seq_info"].append(seq_info)
                st.success("Sequencing information saved successfully!")
                st.info(f"Total sequencing runs: {len(st.session_state['seq_info'])}")
                st.rerun()

    def _save_upload_sequencing_info(
        self, df, mapped_fields, selected_optional_fields, selected_additional_fields
    ):
        """Save uploaded sequencing info rows to session state."""
        if st.button("Add Sequencing Information", key="save_seq_info_upload"):
            if df is None or mapped_fields is None:
                st.error(
                    "Please upload a file and complete field mapping before saving."
                )
                return
            try:
                new_runs = []
                for _, row in df.iterrows():
                    entry = {}
                    for pmo_field, input_field in mapped_fields.items():
                        if input_field and input_field in df.columns:
                            val = row[input_field]
                            entry[pmo_field] = str(val) if pd.notna(val) else None
                    if selected_optional_fields:
                        for pmo_field, input_field in selected_optional_fields.items():
                            if input_field and input_field in df.columns:
                                val = row[input_field]
                                entry[pmo_field] = str(val) if pd.notna(val) else None
                    if selected_additional_fields:
                        for field in selected_additional_fields:
                            if field in df.columns:
                                val = row[field]
                                entry[field] = str(val) if pd.notna(val) else None
                    # Remove None/empty values
                    entry = {
                        k: v for k, v in entry.items() if v is not None and v != ""
                    }
                    new_runs.append(entry)
                if "seq_info" not in st.session_state:
                    st.session_state["seq_info"] = []
                st.session_state["seq_info"].extend(new_runs)
                st.success(f"Added {len(new_runs)} sequencing run(s) successfully!")
                st.info(f"Total sequencing runs: {len(st.session_state['seq_info'])}")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving sequencing information: {e}")

    def _remove_sequencing_runs(self):
        """Allow removal of sequencing runs."""
        if not st.session_state.get("seq_info"):
            return

        st.subheader("Remove Sequencing Runs")
        remove_toggle = st.checkbox(
            "Remove Existing Sequencing Runs",
            help="Check this box to remove existing sequencing runs",
            key="remove_seq_runs_checkbox",
        )
        if remove_toggle:
            seq_info_list = st.session_state["seq_info"]
            remove_options = [
                f"{idx}: {seq.get('sequencing_info_name', f'Run {idx+1}')}"
                for idx, seq in enumerate(seq_info_list)
            ]
            selected_to_remove = st.multiselect(
                "Select sequencing runs to remove:",
                options=remove_options,
                help="Select one or more sequencing runs to remove",
                key="select_seq_runs_to_remove",
            )
            if selected_to_remove and st.button(
                "Remove Selected Runs", type="secondary", key="remove_selected_seq_runs"
            ):
                indices_to_remove = sorted(
                    [int(opt.split(":")[0]) for opt in selected_to_remove], reverse=True
                )
                for idx in indices_to_remove:
                    if 0 <= idx < len(st.session_state["seq_info"]):
                        removed = st.session_state["seq_info"].pop(idx)
                        name = removed.get("sequencing_info_name", f"Run {idx+1}")
                        st.success(f"Removed sequencing run: {name}")
                st.info(
                    f"Remaining sequencing runs: {len(st.session_state['seq_info'])}"
                )
                st.rerun()

    def display_info(self):
        """Display preview of sequencing information."""
        if st.session_state.get("seq_info"):
            st.subheader("Preview Sequencing Information")
            preview_toggle = st.toggle("Preview Sequencing Information")
            if preview_toggle:
                st.write(f"Total sequencing runs: {len(st.session_state['seq_info'])}")
                for idx, seq_info in enumerate(st.session_state["seq_info"]):
                    st.write(f"**Sequencing Run {idx+1}:**")
                    st.json(seq_info)
                    if idx < len(st.session_state["seq_info"]) - 1:
                        st.write("---")

    def run(self):
        st.subheader("Add Sequencing Information")
        seq_input_mode = st.radio(
            "Sequencing information input method:",
            ["Upload File", "Enter Manually"],
            horizontal=True,
            key="seq_input_mode",
        )

        if seq_input_mode == "Enter Manually":
            seq_info = self.add_manual_sequencing_information()
            self._save_manual_sequencing_info(seq_info)
        else:
            (
                df,
                mapped_fields,
                selected_optional_fields,
                selected_additional_fields,
            ) = self.add_upload_sequencing_information()
            self._save_upload_sequencing_info(
                df, mapped_fields, selected_optional_fields, selected_additional_fields
            )

        self._remove_sequencing_runs()
        self.display_info()


# Initialize and run the page
if __name__ in ("__main__", "__page__"):
    render_header()
    st.subheader("Sequencing Information", divider="gray")
    schema_fields = load_schema()
    required_fields = schema_fields["sequencing_info"]["required"]
    required_alternate_fields = schema_fields["sequencing_info"][
        "required_alternatives"
    ]
    optional_fields = schema_fields["sequencing_info"]["optional"]
    optional_alternate_fields = schema_fields["sequencing_info"][
        "optional_alternatives"
    ]

    app = SeqInfoPage(
        required_fields,
        required_alternate_fields,
        optional_fields,
        optional_alternate_fields,
    )
    if "seq_info" in st.session_state and st.session_state["seq_info"]:
        st.success(
            f"You have {len(st.session_state['seq_info'])} sequencing run(s) saved."
        )
        if st.button("Clear Previous Info", type="secondary"):
            del st.session_state["seq_info"]
            st.rerun()
    app.run()
