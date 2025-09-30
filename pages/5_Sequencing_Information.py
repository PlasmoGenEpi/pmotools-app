import streamlit as st
from src.format_page import render_header


class SeqInfoPage:
    def __init__(self):
        self.seq_info = {}

    def add_sequencing_information(self):
        st.subheader("Add Sequencing Information")

        self.seq_info["sequencing_info_name"] = st.text_input(
            "Sequencing Information Name:",
            help="A unique identifier for this sequencing info.",
        )
        seq_platform = st.text_input(
            "Sequencing Platform:",
            help="The sequencing platform used to sequence the run, e.g. ILLUMINA, Illumina MiSeq.",
        )
        seq_instrument_model = st.text_input(
            "Sequencing Instrument Model:",
            help="The sequencing instrument model used to sequence the run, e.g. Illumina MiSeq.",
        )
        library_layout = st.text_input(
            "Library Layout:",
            help="Specify the configuration of reads, e.g. paired-end.",
        )
        library_strategy = st.text_input(
            "Library Strategy:",
            help="The strategy used to prepare the library, e.g. WGS, WES, amplicon, etc.",
        )
        library_source = st.text_input(
            "Library Source:",
            help="The source of the library, e.g. DNA, RNA, etc.",
        )
        library_selection = st.text_input(
            "Library Selection:",
            help="The selection method used to prepare the library, e.g. PCR, etc.",
        )
        # Optional fields - each field is individually optional
        st.subheader("Optional Fields")
        st.write(
            "The following fields are optional. Fill in only the ones you have information for."
        )

        library_kit = st.text_input(
            "Library Kit (Optional):",
            help="Name, version, and applicable cell or cycle numbers for the kit used to prepare libraries and load cells or chips for sequencing. If possible, include a part number, e.g. MiSeq Reagent Kit v3 (150-cycle), MS-102-3001.",
        )
        library_screen = st.text_input(
            "Library Screen (Optional):",
            help="Describe enrichment, screening, or normalization methods applied during amplification or library preparation, e.g. size selection 390bp, diluted to 1 ng DNA/sample.",
        )
        nucl_acid_amp = st.text_input(
            "Nucleic Acid Amplification (Optional):",
            help="Link to a reference or kit that describes the enzymatic amplification of nucleic acids.",
        )
        nucl_acid_ext = st.text_input(
            "Nucleic Acid Extraction (Optional):",
            help="Link to a reference or kit that describes the recovery of nucleic acids from the sample.",
        )
        nucl_acid_ext_date = st.date_input(
            "Nucleic Acid Extraction Date (Optional):",
            help="The date of the nucleoacide extraction.",
        )
        nucl_acid_amp_date = st.date_input(
            "Nucleic Acid Amplification Date (Optional):",
            help="The date of the nucleoacide amplification.",
        )
        pcr_cond = st.text_input(
            "PCR Conditions (Optional):",
            help="The method/conditions for PCR, List PCR cycles used to amplify the target.",
        )
        seq_center = st.text_input(
            "Sequencing Center (Optional):",
            help="Name of facility where sequencing was performed (lab, core facility, or company).",
        )
        seq_date = st.date_input(
            "Sequencing Date (Optional):",
            help="The date of sequencing, should be YYYY-MM or YYYY-MM-DD.",
        )

        # Store the values in seq_info
        self.seq_info["sequencing_info_name"] = self.seq_info["sequencing_info_name"]
        self.seq_info["seq_platform"] = seq_platform
        self.seq_info["seq_instrument_model"] = seq_instrument_model
        self.seq_info["seq_date"] = str(seq_date)
        self.seq_info["nucl_acid_ext"] = nucl_acid_ext
        self.seq_info["nucl_acid_amp"] = nucl_acid_amp
        self.seq_info["nucl_acid_ext_date"] = str(nucl_acid_ext_date)
        self.seq_info["nucl_acid_amp_date"] = str(nucl_acid_amp_date)
        self.seq_info["pcr_cond"] = pcr_cond
        self.seq_info["library_screen"] = library_screen
        self.seq_info["library_layout"] = library_layout
        self.seq_info["library_kit"] = library_kit
        self.seq_info["library_strategy"] = library_strategy
        self.seq_info["library_source"] = library_source
        self.seq_info["library_selection"] = library_selection
        self.seq_info["seq_center"] = seq_center

    def add_additional_fields(self):
        st.title("Add Additional Fields")

        # Add a toggle to enable additional fields
        add_fields_toggle = st.checkbox("Add Additional Fields")

        if add_fields_toggle:
            st.write("Fill in the additional fields below:")
            number_inputs = st.number_input(
                "Number of additional inputs", min_value=0, value=1
            )
            # Inputs for names and values
            cols = st.columns(2)
            with cols[0]:
                field_names = [
                    st.text_input(f"Field Name {i}", key=f"field_name_{i}")
                    for i in range(number_inputs)
                ]
            with cols[1]:
                field_values = [
                    st.text_input(f"Value {i}", key=f"value_{i}")
                    for i in range(number_inputs)
                ]

            # Save the additional fields
            for i in range(number_inputs):
                self.seq_info[field_names[i]] = field_values[i]

    def transform_and_save_data(self):
        seq_info = self.seq_info
        # Only require the essential fields - all others are optional
        if all(
            [
                seq_info.get("sequencing_info_name"),
                seq_info.get("seq_platform"),
                seq_info.get("seq_instrument_model"),
                seq_info.get("library_layout"),
                seq_info.get("library_strategy"),
                seq_info.get("library_source"),
                seq_info.get("library_selection"),
            ]
        ):
            st.subheader("Save Data")
            if st.button("Save Data"):
                # Filter out empty optional fields before saving
                filtered_seq_info = {
                    k: v for k, v in seq_info.items() if v is not None and v != ""
                }
                st.session_state["seq_info"] = {
                    seq_info["sequencing_info_name"]: filtered_seq_info
                }
                st.success("Sequencing information saved successfully!")
        else:
            st.warning("Please fill in all required fields before saving.")

    def display_info(self):
        if "seq_info" in st.session_state:
            st.subheader("Preview Sequencing Information")
            preview_toggle = st.toggle("Preview Sequencing Information")
            if preview_toggle:
                st.write("Current Sequencing Information:")
                st.json(st.session_state["seq_info"])

    def run(self):
        self.add_sequencing_information()
        self.add_additional_fields()
        self.transform_and_save_data()
        self.display_info()


# Initialize and run the page
if __name__ == "__main__":
    render_header()
    st.subheader("Sequencing Information", divider="gray")
    app = SeqInfoPage()
    app.run()
