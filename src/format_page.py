# utils.py
from src.field_matcher import fuzzy_field_matching_page_section, interactive_field_mapping_page_section
from src.data_loader import load_csv
import streamlit as st


def render_header():
    """
    Render a header with a logo alongside text.
    """
    st.set_page_config(
        page_title="PMO Builder",
        page_icon="📂",
        layout="wide",
    )

    # Create two columns for layout: logo + text
    col1, col2 = st.columns([1, 4])

    with col1:
        st.image(
            "images/PGE_logo.png"
        )

    with col2:
        # Add title and subtitle
        st.title("PMO File Builder")
        st.markdown("**Streamlined Workflow for Generating PMO Files**")


class BasicPage:
    def __init__(self, target_schema):
        self.target_schema = target_schema

    def upload_csv(self):
        st.subheader("Upload File")
        return st.file_uploader("Upload a TSV file", type="csv")

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

            # TODO: Implement Transform and save data
