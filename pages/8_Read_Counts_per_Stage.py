import streamlit as st
from src.format_page import render_header
from src.field_matcher import load_data
from src.transformer import transform_read_counts_per_stage
from src.utils import load_schema

session_name = "read_counts_per_stage"
title = "read counts per stage"


class ReadCountsPerStagePage:
    def __init__(
        self,
        raw_counts_required_fields,
        raw_counts_required_alternate_fields,
        reads_by_stage_required_fields,
        reads_by_stage_required_alternate_fields,
    ):
        self.raw_counts_required_fields = raw_counts_required_fields
        self.raw_counts_required_alternate_fields = raw_counts_required_alternate_fields
        self.reads_by_stage_required_fields = reads_by_stage_required_fields
        self.reads_by_stage_required_alternate_fields = (
            reads_by_stage_required_alternate_fields
        )

    def transform_and_save_data(
        self,
        raw_counts_df,
        reads_by_stage_df,
        bioinfo_run_name,
        raw_counts_field_mapping,
        reads_by_stage_field_mapping,
        raw_counts_selected_additional_fields,
        reads_by_stage_selected_additional_fields,
    ):
        if (raw_counts_field_mapping != "Error") and (
            reads_by_stage_field_mapping != "Error"
        ):
            st.subheader("Transform Data")
            if st.button("Transform Data"):
                transformed_df = transform_read_counts_per_stage(
                    raw_counts_df,
                    reads_by_stage_df,
                    bioinfo_run_name,
                    raw_counts_field_mapping,
                    reads_by_stage_field_mapping,
                    raw_counts_selected_additional_fields,
                    reads_by_stage_selected_additional_fields,
                )
                st.session_state[session_name] = transformed_df
                try:
                    st.success("Specimen Information has been saved!")
                except Exception as e:
                    st.error(f"Error saving Specimen Information: {e}")

    def display_panel_info(self, toggle_text):
        if session_name in st.session_state:
            preview = st.toggle(toggle_text)
            if preview:
                st.write(f"Current {title}:")
                st.json(st.session_state[session_name])

    def run(self):
        st.subheader("Raw Read Counts per Sample", divider="gray")
        (
            raw_counts_df,
            raw_counts_mapped_fields,
            selected_optional_fields,
            raw_counts_selected_additional_fields,
        ) = load_data(
            self.raw_counts_required_fields,
            self.raw_counts_required_alternate_fields,
            [],
            [],
            key_suffix="raw_counts",
        )
        st.subheader("Read Counts per Stage", divider="gray")
        (
            reads_by_stage_df,
            reads_by_stage_mapped_fields,
            selected_optional_fields,
            reads_by_stage_selected_additional_fields,
        ) = load_data(
            self.reads_by_stage_required_fields,
            self.reads_by_stage_required_alternate_fields,
            [],
            [],
            key_suffix="reads_by_stage",
        )
        bioinfo_run_name = st.text_input(
            "Bioinformatics Run Name:", help="The name of the bioinformatics run."
        )
        # Transform and save data
        if raw_counts_mapped_fields and reads_by_stage_mapped_fields:
            self.transform_and_save_data(
                raw_counts_df,
                reads_by_stage_df,
                bioinfo_run_name,
                raw_counts_mapped_fields,
                reads_by_stage_mapped_fields,
                raw_counts_selected_additional_fields,
                reads_by_stage_selected_additional_fields,
            )
        # Display current panel information
        self.display_panel_info(f"Preview {title}")


if __name__ == "__main__":
    render_header()
    schema_fields = load_schema()
    raw_counts_required_fields = schema_fields["read_counts_perstage"]["raw_counts"][
        "required"
    ]
    raw_counts_required_alternate_fields = schema_fields["read_counts_perstage"][
        "raw_counts"
    ]["required_alternatives"]
    reads_by_stage_required_fields = schema_fields["read_counts_perstage"][
        "reads_by_stage"
    ]["required"]
    reads_by_stage_required_alternate_fields = schema_fields["read_counts_perstage"][
        "reads_by_stage"
    ]["required_alternatives"]
    app = ReadCountsPerStagePage(
        raw_counts_required_fields,
        raw_counts_required_alternate_fields,
        reads_by_stage_required_fields,
        reads_by_stage_required_alternate_fields,
    )
    if session_name in st.session_state:
        st.success(
            f"Your {title} has already been saved during a" " previous run of this page"
        )
        app.display_panel_info(f"Preview previously stored {title}")
    app.run()
