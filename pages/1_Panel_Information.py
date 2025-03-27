import streamlit as st
import json
import os
from src.data_loader import load_csv
from src.field_matcher import fuzzy_field_matching_page_section, interactive_field_mapping_page_section, add_additional_fields
from src.transformer import transform_panel_info
from src.format_page import render_header
from src.utils import load_schema

class PanelManager:
    def __init__(self, save_dir):
        self.save_dir = save_dir

    def check_save_dir(self):
        """Check dir exists or create it."""
        os.makedirs(self.save_dir, exist_ok=True)

    def save_panel(self, panel_name, panel_data):
        """Save panel data to a JSON file."""
        with open(os.path.join(self.save_dir, f"{panel_name}.json"), "w") as f:
            json.dump(panel_data, f)

    def load_panel(self, panel_name):
        """Load panel data from a JSON file."""
        with open(os.path.join(self.save_dir, f"{panel_name}.json"), "r") as f:
            return json.load(f)

    def get_saved_panels(self):
        """Get a list of saved panel names."""
        return [f.split(".json")[0] for f in os.listdir(self.save_dir) if f.endswith(".json")]


class PanelPage:
    def __init__(self, save_dir, target_schema, alternate_schema_names):
        self.save_dir = save_dir
        self.panel_manager = PanelManager(self.save_dir)
        self.panel_manager.check_save_dir()
        self.target_schema = target_schema
        self.alternate_schema_names = alternate_schema_names

    def load_saved_panel(self):
        use_past = st.checkbox("Use a past version")
        if use_past:
            saved_panels = self.panel_manager.get_saved_panels()
            if saved_panels:
                selected_panel = st.selectbox(
                    "Select a saved panel:", saved_panels)
                if st.button("Load Panel"):
                    panel_data = self.panel_manager.load_panel(selected_panel)
                    st.session_state["panel_info"] = panel_data
                    st.success(f"Loaded panel: {selected_panel}")
            else:
                st.warning("No saved panels found.")

    def panel_id_input(self):
        st.subheader("Panel ID")
        return st.text_input("Enter panel ID:", help='Identifier for the panel.')

    def upload_csv(self):
        st.subheader("Upload File")
        return st.file_uploader("Upload a TSV file", type=["csv", "tsv", "xlsx", "xls", "txt"])

    def field_mapping(self, df):
        # Fuzzy field matching
        field_mapping, unused_field_names = fuzzy_field_matching_page_section(
            df, self.target_schema, self.alternate_schema_names)

        # Interactive field mapping
        field_mapping = interactive_field_mapping_page_section(
            field_mapping, df.columns.tolist())
        return field_mapping, unused_field_names

    def add_genome_information(self):
        st.subheader("Add Genome Information")
        genome_name = st.text_input("Name:", help='Name of the genome.')
        taxon_id = st.text_input("Taxon ID:", help='The NCBI taxonomy number.')
        version = st.text_input("Version:", help='The genome version.')
        genome_url = st.text_input("URL:", help='A link to the genome file.')
        gff_url = st.text_input("GFF URL (Optional):",
                                help='A link to the genome’s annotation file')
        genome_info = {
            "name": genome_name,
            "taxon_id": taxon_id,
            "url": genome_url,
            "version": version,
        }
        if gff_url:
            genome_info["gff_url"] = gff_url
        return genome_info

    def transform_and_save_data(self, df, panel_ID, field_mapping, genome_info, selected_additional_fields):
        if all([panel_ID, genome_info["name"], genome_info["taxon_id"], genome_info["version"], genome_info["url"]]):
            st.subheader("Transform Data")
            if st.button("Transform Data"):
                transformed_df = transform_panel_info(
                    df, panel_ID, field_mapping, genome_info, selected_additional_fields)
                # json_data = json.dumps(transformed_df, indent=4)
                st.session_state["panel_info"] = transformed_df
                try:
                    self.panel_manager.save_panel(panel_ID, transformed_df)
                    st.success(f"Panel '{panel_ID}' has been saved!")
                except Exception as e:
                    st.error(f"Error saving panel: {e}")

    def display_panel_info(self):
        if "panel_info" in st.session_state:
            preview = st.toggle("Preview Panel Information")
            if preview:
                st.write("Current Panel Information:")
                st.json(st.session_state["panel_info"])

    def run(self):
        # Load past panel if applicable
        self.load_saved_panel()

        # Input for panel ID
        panel_ID = self.panel_id_input()

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
            selected_additional_fields = add_additional_fields(
                unused_field_names)

            # Add genome information
            genome_info = self.add_genome_information()

            # Transform and save data
            self.transform_and_save_data(
                df, panel_ID, field_mapping, genome_info, selected_additional_fields)

        # Display current panel information
        self.display_panel_info()


# Initialize and run the app
if __name__ == "__main__":
    render_header()
    st.subheader("Panel Information Converter", divider="gray")
    schema_fields = load_schema()
    target_schema = schema_fields["panel_info"]["required"]
    alternate_schema_names = schema_fields["panel_info"]["alternatives"]
    app = PanelPage(os.path.join(os.getcwd(), "saved_panels"),
                    target_schema, alternate_schema_names)
    app.run()
