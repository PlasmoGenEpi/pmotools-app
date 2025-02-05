import streamlit as st
from src.data_loader import load_csv
from src.field_matcher import fuzzy_field_matching_page_section, interactive_field_mapping_page_section
from src.transformer import transform_demultiplexed_info
from src.format_page import render_header


class DemultiplexPage:
    def __init__(self):
        self.target_schema = ["sampleID",
                              "target_id", "raw_read_count"]

    def upload_csv(self):
        st.subheader("Upload File")
        return st.file_uploader("Upload a TSV file", type=["csv", "tsv", "xlsx", "xls", "txt"])

    def field_mapping(self, df):
        # Fuzzy field matching
        field_mapping, unused_field_names = fuzzy_field_matching_page_section(
            df, self.target_schema)

        # Interactive field mapping
        field_mapping = interactive_field_mapping_page_section(
            field_mapping, df.columns.tolist())
        return field_mapping, unused_field_names

    def add_additional_fields(self, unused_field_names):
        st.subheader("Add Additional Fields")
        selected_additional_fields = None
        if unused_field_names:
            optional_additional_fields = st.toggle("Add additional fields")
            if optional_additional_fields:
                checkbox_states = {}
                st.write("Select the extra columns you would like to include:")
                for item in unused_field_names:
                    checkbox_states[item] = st.checkbox(label=item)
                selected_additional_fields = [
                    key for key, value in checkbox_states.items() if value]
                st.write("You selected:", selected_additional_fields)
        return selected_additional_fields

    def bioinfo_id_input(self):
        st.subheader("Bioinformatics ID")
        return st.text_input("Enter bioinfo ID:", help='Identifier for the bioinformatics run.')

    def transform_and_save_data(self, df, bioinfo_ID, field_mapping, selected_additional_fields):
        if bioinfo_ID:
            st.subheader("Transform Data")
            if st.button("Transform Data"):
                transformed_df = transform_demultiplexed_info(
                    df, bioinfo_ID, field_mapping, selected_additional_fields)
                st.session_state["mhap_data"] = transformed_df
                try:
                    st.success(
                        f"Demultiplexed Information from Bioinformatics Run '{bioinfo_ID}' has been saved!")
                except Exception as e:
                    st.error(f"Error saving Microhaplotype Information: {e}")

    def run(self):
        # File upload
        uploaded_file = self.upload_csv()
        if uploaded_file:
            df = load_csv(uploaded_file)
            interactive_preview = st.toggle("Preview File")
            if interactive_preview:
                st.write("Uploaded File Preview:")
                st.dataframe(df)

            field_mapping, unused_field_names = self.field_mapping(df)

            # Add additional fields
            selected_additional_fields = self.add_additional_fields(
                unused_field_names)

            # Enter bioinformatics ID
            bioinfo_ID = self.bioinfo_id_input()

            self.transform_and_save_data(
                df, bioinfo_ID, field_mapping, selected_additional_fields)


# Initialize and run the app
if __name__ == "__main__":
    render_header()
    st.subheader("Microhaplotype Information Converter", divider="gray")
    app = DemultiplexPage()
    app.run()
