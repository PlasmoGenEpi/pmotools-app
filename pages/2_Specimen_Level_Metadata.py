import streamlit as st
from src.format_page import render_header
from src.data_loader import load_csv
from src.field_matcher import fuzzy_field_matching_page_section, interactive_field_mapping_page_section, interactive_field_mapping_page_section_optional
from src.transformer import transform_specimen_info
from src.utils import load_schema


class SpecimenMetadataPage:
    def __init__(self, target_schema, alternate_schema_names):
        self.target_schema = target_schema
        self.alternate_schema_names = alternate_schema_names

    def upload_csv(self):
        st.subheader("Upload File")
        return st.file_uploader("Upload a TSV file", type=["csv", "tsv", "xlsx", "xls", "txt"])

    def field_mapping(self, df):
        # Fuzzy field matching required arguments
        mapped_fields, unused_field_names = fuzzy_field_matching_page_section(
            df, self.target_schema, self.alternate_schema_names)

        # Interactive field mapping
        mapped_fields = interactive_field_mapping_page_section(
            mapped_fields, df.columns.tolist())
        return mapped_fields, unused_field_names

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

    def add_optional_fields(self, df, unused_field_names):
        st.subheader("Add Optional Fields")
        mapped_fields = {key:None for key in schema_fields["specimen_level_metadata"]["optional"]}
        if unused_field_names:
            new_df=df[unused_field_names]
            # Fuzzy field matching optional arguments
            mapped_fields, junk = fuzzy_field_matching_page_section(
                new_df, schema_fields["specimen_level_metadata"]["optional"], 
                schema_fields["specimen_level_metadata"]["optional_alternatives"])

            #Interactive field mapping optional arguments
            mapped_fields = interactive_field_mapping_page_section_optional(
                mapped_fields, new_df.columns.tolist())
        for key in mapped_fields:
            if mapped_fields[key]=='no match':
                mapped_fields[key]=None
        remaining_unused=list(set(unused_field_names)-set(mapped_fields.values()))
        return mapped_fields, remaining_unused

    def transform_and_save_data(self, df, mapped_fields, selected_optional_fields, selected_additional_fields):
        st.subheader("Transform Data")
        if st.button("Transform Data"):
            transformed_df = transform_specimen_info(
                df, mapped_fields, selected_optional_fields, selected_additional_fields)
            st.session_state["specimen_info"] = transformed_df
            try:
                st.success(
                    f"Specimen Information has been saved!")
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

            mapped_fields, unused_field_names = self.field_mapping(df)
            # Add optional fields
            selected_optional_fields, unused_field_names = self.add_optional_fields(df,
                unused_field_names)
            # Add additional fields
            selected_additional_fields = self.add_additional_fields(unused_field_names)

            # Transform and save data
            self.transform_and_save_data(
                df, mapped_fields, selected_optional_fields, selected_additional_fields)


if __name__ == "__main__":
    render_header()
    st.subheader("Specimen Level Metadata Converter", divider="gray")
    schema_fields = load_schema()
    target_schema = schema_fields["specimen_level_metadata"]["required"]
    alternate_schema_names = schema_fields["specimen_level_metadata"]["required_alternatives"]
    app = SpecimenMetadataPage(target_schema, alternate_schema_names)
    app.run()
