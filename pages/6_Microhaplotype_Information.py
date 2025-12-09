import streamlit as st
from src.format_page import render_header
from src.field_matcher import load_data
from src.transformer import transform_mhap_info
from src.utils import load_schema

session_name = "microhaplotype_info"
title = "microhaplotype information"


class MicrohaplotypeInfoPage:
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

    def bioinfo_id_input(self, df):
        """Get bioinformatics ID from user - either from a column or as a string."""
        st.subheader("Bioinformatics ID")

        if df is not None and not df.empty:
            # Option to select from column or enter manually
            input_method = st.radio(
                "Select bioinformatics ID source:",
                ["Select from column", "Enter manually"],
                horizontal=True,
                key="bioinfo_id_method",
            )

            if input_method == "Select from column":
                column = st.selectbox(
                    "Select column containing bioinformatics ID:",
                    df.columns.tolist(),
                    key="bioinfo_id_column",
                )
                return column
            else:
                return st.text_input(
                    "Enter bioinformatics ID:",
                    help="Identifier for the bioinformatics run.",
                    key="bioinfo_id_text",
                )
        else:
            # No file uploaded, only allow manual entry
            return st.text_input(
                "Enter bioinformatics ID:",
                help="Identifier for the bioinformatics run.",
                key="bioinfo_id_text",
            )

    def transform_and_save_data(
        self,
        df,
        bioinfo_id,
        mapped_fields,
        selected_optional_fields,
        selected_additional_fields,
    ):
        st.subheader("Transform Data")
        if st.button("Transform Data"):
            # Validate required fields
            errors = []

            if not bioinfo_id or (
                isinstance(bioinfo_id, str) and not bioinfo_id.strip()
            ):
                errors.append("Bioinformatics ID is required.")

            if not mapped_fields:
                errors.append(
                    "Field mapping is required. Please upload a file and map the fields."
                )

            if selected_optional_fields == "Error":
                errors.append("There was an error with the optional fields selection.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # All validations passed, proceed with transformation
                transformed_df = transform_mhap_info(
                    df.astype(object) if df is not None else None,
                    bioinfo_id,
                    mapped_fields,
                    selected_optional_fields,
                    selected_additional_fields,
                )
                st.session_state[session_name] = transformed_df
                try:
                    st.success("Microhaplotype Information has been saved!")
                except Exception as e:
                    st.error(f"Error saving Microhaplotype Information: {e}")

    def display_microhaplotype_info(self, toggle_text):
        if session_name in st.session_state:
            preview = st.toggle(toggle_text)
            if preview:
                st.write(f"Current {title}:")
                st.json(st.session_state[session_name])

    def run(self):
        (
            df,
            mapped_fields,
            selected_optional_fields,
            selected_additional_fields,
        ) = load_data(
            required_fields,
            required_alternate_fields,
            optional_fields,
            optional_alternate_fields,
        )
        # Get bioinformatics ID input
        bioinfo_id = self.bioinfo_id_input(df)
        # Transform and save data
        self.transform_and_save_data(
            df,
            bioinfo_id,
            mapped_fields,
            selected_optional_fields,
            selected_additional_fields,
        )
        # Display current panel information
        self.display_microhaplotype_info(f"Preview {title}")


if __name__ == "__main__":
    render_header()
    st.subheader("Microhaplotype Information Converter", divider="gray")
    schema_fields = load_schema()
    required_fields = schema_fields["mhap_info"]["required"]
    required_alternate_fields = schema_fields["mhap_info"]["required_alternatives"]
    optional_fields = schema_fields["mhap_info"]["optional"]
    optional_alternate_fields = schema_fields["mhap_info"]["optional_alternatives"]
    app = MicrohaplotypeInfoPage(
        required_fields,
        required_alternate_fields,
        optional_fields,
        optional_alternate_fields,
    )
    if session_name in st.session_state:
        st.success(
            f"Your {title} has already been saved during a" " previous run of this page"
        )
        app.display_microhaplotype_info(f"Preview previously stored {title}")
    app.run()
