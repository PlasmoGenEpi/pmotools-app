import streamlit as st
from src.field_matcher import load_data
from src.field_matcher import fuzzy_field_matching_page_section, interactive_field_mapping_page_section
from src.transformer import transform_mhap_info
from src.format_page import render_header
from src.utils import load_schema


class MhapPage:
    def __init__(self, required_fields, required_alternate_fields,
        optional_fields, optional_alternate_fields):
        self.required_fields = required_fields
        self.required_alternate_fields = required_alternate_fields
        self.optional_fields = optional_fields
        self.optional_alternate_fields = optional_alternate_fields

    def bioinfo_id_input(self):
        st.subheader("Bioinformatics ID")
        return st.text_input("Enter bioinfo ID:", help='Identifier for the bioinformatics run.')

    def transform_and_save_data(self, df, bioinfo_ID, field_mapping, 
        selected_optional_fields, selected_additional_fields):
        #there are currently no optional fields but the field is passed anyway
        #for compatibility with any future optional fields.
        if bioinfo_ID:
            st.subheader("Transform Data")
            if st.button("Transform Data"):
                transformed_df = transform_mhap_info(df, bioinfo_ID,
                    field_mapping, selected_optional_fields,
                    selected_additional_fields)
                # json_data = json.dumps(transformed_df, indent=4)
                st.session_state["mhap_data"] = transformed_df
                try:
                    st.success(
                        f"Microhaplotype Information from Bioinformatics Run '{bioinfo_ID}' has been saved!")
                except Exception as e:
                    st.error(f"Error saving Microhaplotype Information: {e}")

    def run(self):
        # File upload
        df, mapped_fields, selected_optional_fields, selected_additional_fields=load_data(
            required_fields, required_alternate_fields, optional_fields,
            optional_alternate_fields)
            # Enter bioinformatics ID
        bioinfo_ID = self.bioinfo_id_input()
        self.transform_and_save_data(
            df, bioinfo_ID, mapped_fields, selected_optional_fields, selected_additional_fields)

# Initialize and run the app
if __name__ == "__main__":
    render_header()
    st.subheader("Microhaplotype Information Converter", divider="gray")
    schema_fields = load_schema()

    required_fields = schema_fields["mhap_info"]["required"]
    required_alternate_fields = schema_fields["mhap_info"]["required_alternatives"]
    optional_fields = schema_fields["mhap_info"]["optional"]
    optional_alternate_fields = schema_fields["mhap_info"]["optional_alternatives"]
    app = MhapPage(required_fields, required_alternate_fields, optional_fields,
        optional_alternate_fields)
    app.run()
