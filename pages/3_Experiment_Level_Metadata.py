import streamlit as st
from src.format_page import render_header
from src.field_matcher import load_data
from src.transformer import transform_experiment_info
from src.utils import load_schema


class ExperimentMetadataPage:
    def __init__(self, required_fields, required_alternate_fields,
        optional_fields, optional_alternate_fields):
        self.required_fields = required_fields
        self.required_alternate_fields = required_alternate_fields
        self.optional_fields = optional_fields
        self.optional_alternate_fields = optional_alternate_fields

    def transform_and_save_data(self, df, field_mapping, 
        selected_optional_fields, selected_additional_fields):
        st.subheader("Transform Data")
        if st.button("Transform Data"):
            transformed_df = transform_experiment_info(df, field_mapping,
                selected_optional_fields, selected_additional_fields)
            st.session_state["experiment_info"] = transformed_df
            try:
                st.success(
                    f"Experiment Information has been saved!")
            except Exception as e:
                st.error(f"Error saving Experiment Information: {e}")

    def run(self):
        # File upload
        df, mapped_fields, selected_optional_fields, selected_additional_fields=load_data(
            required_fields, required_alternate_fields, optional_fields,
            optional_alternate_fields)
            # Transform and save data
        self.transform_and_save_data(df, mapped_fields,
            selected_optional_fields, selected_additional_fields)

if __name__ == "__main__":
    render_header()
    st.subheader("Experiment Level Metadata Converter", divider="gray")
    schema_fields = load_schema()
    required_fields = schema_fields["experiment_level_metadata"]["required"]
    required_alternate_fields = schema_fields["experiment_level_metadata"]["required_alternatives"]
    optional_fields = schema_fields["experiment_level_metadata"]["optional"]
    optional_alternate_fields = schema_fields["experiment_level_metadata"]["optional_alternatives"]
    app = ExperimentMetadataPage(required_fields, required_alternate_fields, optional_fields, optional_alternate_fields)
    app.run()