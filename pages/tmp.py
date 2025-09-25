import streamlit as st
from src.field_matcher import load_data
from src.transformer import transform_demultiplexed_info
from src.format_page import render_header
from src.utils import load_schema

session_name = "demultiplexed_data"
title = "demultiplexed samples"


class DemultiplexPage:
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

    def bioinfo_id_input(self):
        st.subheader("Bioinformatics ID")
        return st.text_input(
            "Enter bioinfo ID:", help="Identifier for the bioinformatics run."
        )

    def transform_and_save_data(
        self,
        df,
        bioinfo_ID,
        mapped_fields,
        selected_optional_fields,
        selected_additional_fields,
    ):
        if bioinfo_ID and mapped_fields and selected_optional_fields != "Error":
            st.subheader("Transform Data")
            if st.button("Transform Data"):
                transformed_df = transform_demultiplexed_info(
                    df,
                    bioinfo_ID,
                    mapped_fields,
                    selected_optional_fields,
                    selected_additional_fields,
                )
                st.session_state["demultiplexed_data"] = transformed_df
                try:
                    st.success(
                        f"Demultiplexed Information from Bioinformatics Run '{bioinfo_ID}' has been saved!"
                    )
                except Exception as e:
                    st.error(f"Error saving demultiplexed samples: {e}")

    def display_panel_info(self, toggle_text):
        if session_name in st.session_state:
            preview = st.toggle(toggle_text)
            if preview:
                st.write(f"Current {title}:")
                st.json(st.session_state[session_name])

    def run(self):
        # File upload
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
        # Enter bioinformatics ID
        bioinfo_ID = self.bioinfo_id_input()
        self.transform_and_save_data(
            df,
            bioinfo_ID,
            mapped_fields,
            selected_optional_fields,
            selected_additional_fields,
        )
        # Display current panel information
        self.display_panel_info(f"Preview {title}")


# Initialize and run the app
if __name__ == "__main__":
    render_header()
    st.subheader("Demultiplexed Sample Read Count Converter", divider="gray")
    schema_fields = load_schema()
    required_fields = schema_fields["demultiplexed_samples"]["required"]
    required_alternate_fields = schema_fields["demultiplexed_samples"][
        "required_alternatives"
    ]
    optional_fields = schema_fields["demultiplexed_samples"]["optional"]
    optional_alternate_fields = schema_fields["demultiplexed_samples"][
        "optional_alternatives"
    ]
    app = DemultiplexPage(
        required_fields,
        required_alternate_fields,
        optional_fields,
        optional_alternate_fields,
    )
    if session_name in st.session_state:
        st.success(
            f"Your {title} has already been saved during a" " previous run of this page"
        )
        app.display_panel_info(f"Preview previously stored {title}")
    app.run()
