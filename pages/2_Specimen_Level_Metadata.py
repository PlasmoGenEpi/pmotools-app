import streamlit as st
from src.format_page import render_header
from src.field_matcher import load_data
from src.transformer import transform_specimen_info
from src.utils import load_schema

class SpecimenMetadataPage:
    def __init__(self, required_fields, required_alternate_fields,
        optional_fields, optional_alternate_fields):
        self.required_fields = required_fields
        self.required_alternate_fields = required_alternate_fields
        self.optional_fields = optional_fields
        self.optional_alternate_fields = optional_alternate_fields

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
                st.error(f"Error saving Specimen Information: {e}")

    def run(self):
        df, mapped_fields, selected_optional_fields, selected_additional_fields=load_data(
            required_fields, required_alternate_fields, optional_fields,
            optional_alternate_fields)
        # Transform and save data
        if mapped_fields:
            self.transform_and_save_data(df, mapped_fields,
                selected_optional_fields, selected_additional_fields)

if __name__ == "__main__":
    render_header()
    st.subheader("Specimen Level Metadata Converter", divider="gray")
    schema_fields = load_schema()
    required_fields = schema_fields["specimen_level_metadata"]["required"]
    required_alternate_fields = schema_fields["specimen_level_metadata"]["required_alternatives"]
    optional_fields = schema_fields["specimen_level_metadata"]["optional"]
    optional_alternate_fields = schema_fields["specimen_level_metadata"]["optional_alternatives"]
    app = SpecimenMetadataPage(required_fields, required_alternate_fields,
        optional_fields, optional_alternate_fields)
    app.run()