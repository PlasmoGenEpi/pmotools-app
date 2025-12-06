import streamlit as st
from src.format_page import render_header


class SeqInfoPage:
    def __init__(self):
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize session state variables if they don't exist."""
        if "seq_info" not in st.session_state:
            st.session_state["seq_info"] = []

    def _show_runs_count(self):
        """Show current sequencing runs count."""
        if st.session_state.get("seq_info"):
            st.info(f"Current sequencing runs: {len(st.session_state['seq_info'])}")
            st.info(
                "To add another sequencing run, enter the information above and click the 'Add Sequencing Information' button again."
            )

    def add_sequencing_information(self):
        """Add sequencing information section - one run at a time."""
        st.subheader("Add Sequencing Information")
        self._show_runs_count()

        seq_info = {}

        seq_info["sequencing_info_name"] = st.text_input(
            "Sequencing Information Name:",
            help="A unique identifier for this sequencing info.",
            key="seq_info_name",
        )
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

        # Optional fields
        st.write("**Optional Fields:**")
        seq_info["library_kit"] = st.text_input(
            "Library Kit (Optional):",
            help="Name, version, and applicable cell or cycle numbers for the kit used to prepare libraries and load cells or chips for sequencing.",
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
            help="Name of facility where sequencing was performed (lab, core facility, or company).",
            key="seq_center",
        )
        seq_info["seq_date"] = st.date_input(
            "Sequencing Date (Optional):",
            value=None,
            help="The date of sequencing, should be YYYY-MM or YYYY-MM-DD.",
            key="seq_date",
        )

        # Convert date objects to strings if they exist
        if seq_info["seq_date"] is not None:
            seq_info["seq_date"] = str(seq_info["seq_date"])
        if seq_info["nucl_acid_ext_date"] is not None:
            seq_info["nucl_acid_ext_date"] = str(seq_info["nucl_acid_ext_date"])
        if seq_info["nucl_acid_amp_date"] is not None:
            seq_info["nucl_acid_amp_date"] = str(seq_info["nucl_acid_amp_date"])

        # Remove empty optional fields
        cleaned_seq_info = {
            k: v for k, v in seq_info.items() if v is not None and v != ""
        }

        return cleaned_seq_info

    def _validate_sequencing_info(self, seq_info):
        """Validate that all required fields are filled."""
        errors = []
        required_fields = [
            "sequencing_info_name",
            "seq_platform",
            "seq_instrument_model",
            "library_layout",
            "library_strategy",
            "library_source",
            "library_selection",
        ]

        missing_fields = []
        for field in required_fields:
            if not seq_info.get(field) or not str(seq_info[field]).strip():
                missing_fields.append(field)

        if missing_fields:
            if len(missing_fields) == 1:
                errors.append(f"Missing required field: {missing_fields[0]}.")
            else:
                errors.append(f"Missing required fields: {', '.join(missing_fields)}.")

        return len(errors) == 0, errors

    def _save_sequencing_info(self, seq_info):
        """Save sequencing information to session state."""
        if st.button("Add Sequencing Information", key="save_seq_info"):
            is_valid, errors = self._validate_sequencing_info(seq_info)

            if not is_valid:
                for error in errors:
                    st.error(error)
                st.warning("Please fill in all required fields before saving.")
            else:
                # Append to existing list in session state
                st.session_state["seq_info"].append(seq_info)
                st.success("Sequencing information saved successfully!")
                st.info(f"Total sequencing runs: {len(st.session_state['seq_info'])}")
                st.rerun()

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
            if not seq_info_list:
                st.warning("No sequencing runs available to remove.")
                return

            # Create options for removal
            remove_options = []
            for idx, seq_info in enumerate(seq_info_list):
                name = seq_info.get("sequencing_info_name", f"Run {idx+1}")
                remove_options.append(f"{idx}: {name}")

            selected_to_remove = st.multiselect(
                "Select sequencing runs to remove:",
                options=remove_options,
                help="Select one or more sequencing runs to remove",
                key="select_seq_runs_to_remove",
            )

            if selected_to_remove and st.button(
                "Remove Selected Runs",
                type="secondary",
                key="remove_selected_seq_runs",
            ):
                # Extract indices and remove in reverse order
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
        seq_info = self.add_sequencing_information()
        self._save_sequencing_info(seq_info)
        self._remove_sequencing_runs()
        self.display_info()


# Initialize and run the page
if __name__ == "__main__":
    render_header()
    st.subheader("Sequencing Information", divider="gray")
    app = SeqInfoPage()
    if "seq_info" in st.session_state and st.session_state["seq_info"]:
        st.success(
            f"You have {len(st.session_state['seq_info'])} sequencing run(s) saved."
        )
    app.run()
