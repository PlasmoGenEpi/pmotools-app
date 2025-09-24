import streamlit as st
from src.format_page import render_header


class SeqInfoPage:
    def __init__(self):
        self.seq_info = {}

    def add_required_seq_information(self):
        st.subheader("Add Sequencing Information")

        self.seq_info["sequencing_info_id"] = st.text_input(
            "Sequencing Information ID:", help='A unique identifier for this sequencing info.')
        seq_instrument = st.text_input(
            "Sequencing Instrument:", help='The sequencing instrument used to sequence the run, e.g. ILLUMINA, Illumina MiSeq.')
        seq_date = st.date_input(
            "Sequencing Date:", help='The date of sequencing, should be YYYY-MM or YYYY-MM-DD.')
        nucl_acid_ext = st.text_input(
            "Nucleic Acid Extraction:", help='Link to a reference or kit that describes the recovery of nucleic acids from the sample.')
        nucl_acid_amp = st.text_input(
            "Nucleic Acid Amplification:", help='Link to a reference or kit that describes the enzymatic amplification of nucleic acids.')
        nucl_acid_ext_date = st.date_input(
            "Nucleic Acid Extraction Date:", help='The date of the nucleoacide extraction.')
        nucl_acid_amp_date = st.date_input(
            "Nucleic Acid Amplification Date:", help='The date of the nucleoacide amplification.')
        pcr_cond = st.text_input(
            "PCR Conditions:", help='The method/conditions for PCR, List PCR cycles used to amplify the target.')
        lib_screen = st.text_input(
            "Library Screen:", help='Describe enrichment, screening, or normalization methods applied during amplification or library preparation, e.g. size selection 390bp, diluted to 1 ng DNA/sample.')
        lib_layout = st.text_input(
            "Library Layout:", help='Specify the configuration of reads, e.g. paired-end.')
        lib_kit = st.text_input(
            "Library Kit:", help='Name, version, and applicable cell or cycle numbers for the kit used to prepare libraries and load cells or chips for sequencing. If possible, include a part number, e.g. MiSeq Reagent Kit v3 (150-cycle), MS-102-3001.')
        seq_center = st.text_input(
            "Sequencing Center:", help='Name of facility where sequencing was performed (lab, core facility, or company).')

        # self.seq_info["sequencing_info_id"] = sequencing_info_id
        self.seq_info["seq_instrument"] = seq_instrument
        self.seq_info["seq_date"] = str(seq_date)
        self.seq_info["nucl_acid_ext"] = nucl_acid_ext
        self.seq_info["nucl_acid_amp"] = nucl_acid_amp
        self.seq_info["nucl_acid_ext_date"] = str(nucl_acid_ext_date)
        self.seq_info["nucl_acid_amp_date"] = str(nucl_acid_amp_date)
        self.seq_info["pcr_cond"] = pcr_cond
        self.seq_info["lib_screen"] = lib_screen
        self.seq_info["lib_layout"] = lib_layout
        self.seq_info["lib_kit"] = lib_kit
        self.seq_info["seq_center"] = seq_center

    def add_additional_fields(self):
        st.title("Add Additional Fields")

        # Add a toggle to enable additional fields
        add_fields_toggle = st.checkbox("Add Additional Fields")

        if add_fields_toggle:
            st.write("Fill in the additional fields below:")
            number_inputs = st.number_input("Number of additional inputs",
                                            min_value=0, value=1)
            # Inputs for names and values
            cols = st.columns(2)
            with cols[0]:
                field_names = [st.text_input(
                    f'Field Name {i}', key=f"field_name_{i}") for i in range(number_inputs)]
            with cols[1]:
                field_values = [st.text_input(
                    f'Value {i}', key=f"value_{i}") for i in range(number_inputs)]

            # Save the additional fields
            for i in range(number_inputs):
                self.seq_info[field_names[i]] = field_values[i]

    def transform_and_save_data(self):
        seq_info = self.seq_info
        if all([seq_info["sequencing_info_id"], seq_info["seq_instrument"], seq_info["seq_date"],
                seq_info["nucl_acid_ext"], seq_info["nucl_acid_amp"], seq_info["nucl_acid_ext_date"], seq_info["nucl_acid_amp_date"],
                seq_info["pcr_cond"], seq_info["lib_screen"], seq_info["lib_layout"], seq_info["lib_kit"],
                seq_info["seq_center"],]):
            st.subheader("Save Data")
            if st.button("Save Data"):
                st.session_state["seq_info"] = {
                    seq_info["sequencing_info_id"]: seq_info}

    def display_info(self):
        if "seq_info" in st.session_state:
            st.subheader("Preview Sequencing Information")
            preview_toggle = st.toggle("Preview Sequencing Information")
            if preview_toggle:
                st.write("Current Sequencing Information:")
                st.json(st.session_state["seq_info"])

    def run(self):
        self.add_required_seq_information()
        self.add_additional_fields()
        self.transform_and_save_data()
        self.display_info()


# Initialize and run the page
if __name__ == "__main__":
    render_header()
    st.subheader("Sequencing Information", divider="gray")
    app = SeqInfoPage()
    app.run()
