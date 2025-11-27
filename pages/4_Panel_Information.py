import streamlit as st
import json
import os
import pandas as pd
from src.field_matcher import load_data
from src.transformer import transform_panel_info
from src.format_page import render_header
from src.utils import load_schema

session_name = "panel_info"
title = "panel information"


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
        return [
            f.split(".json")[0]
            for f in os.listdir(self.save_dir)
            if f.endswith(".json")
        ]


class PanelPage:
    def __init__(
        self,
        save_dir,
        required_fields,
        required_alternate_fields,
        optional_fields,
        optional_alternate_fields,
    ):
        self.save_dir = save_dir
        self.panel_manager = PanelManager(self.save_dir)
        self.panel_manager.check_save_dir()
        self.required_fields = required_fields
        self.required_alternate_fields = required_alternate_fields
        self.optional_fields = optional_fields
        self.optional_alternate_fields = optional_alternate_fields

    def load_saved_panel(self):
        use_past = st.checkbox("Use a past version")
        if use_past:
            saved_panels = self.panel_manager.get_saved_panels()
            if saved_panels:
                selected_panel = st.selectbox("Select a saved panel:", saved_panels)
                if st.button("Load Panel"):
                    panel_data = self.panel_manager.load_panel(selected_panel)
                    st.session_state["panel_info"] = panel_data
                    st.success(f"Loaded panel: {selected_panel}")
            else:
                st.warning("No saved panels found.")

    def panel_id_input(self):
        st.subheader("Panel Name")

        # Get unique panel names from library_sample_info if available
        suggested_panels = []
        if "library_sample_info" in st.session_state:
            library_sample_info = st.session_state["library_sample_info"]
            try:
                # Handle DataFrame
                if isinstance(library_sample_info, pd.DataFrame):
                    if "panel_name" in library_sample_info.columns:
                        suggested_panels = sorted(
                            library_sample_info["panel_name"].dropna().unique().tolist()
                        )
                # Handle dict (could be a dict representation of DataFrame or nested structure)
                elif isinstance(library_sample_info, dict):
                    # Check if it's a dict with 'panel_name' as a key containing a list/Series
                    if "panel_name" in library_sample_info:
                        panel_data = library_sample_info["panel_name"]
                        if isinstance(panel_data, (list, pd.Series)):
                            if isinstance(panel_data, pd.Series):
                                suggested_panels = sorted(
                                    panel_data.dropna().unique().tolist()
                                )
                            else:
                                suggested_panels = sorted(
                                    list(set([p for p in panel_data if p]))
                                )
                    # Check if values in dict are DataFrames with panel_name column
                    else:
                        for value in library_sample_info.values():
                            if (
                                isinstance(value, pd.DataFrame)
                                and "panel_name" in value.columns
                            ):
                                suggested_panels.extend(
                                    value["panel_name"].dropna().unique().tolist()
                                )
                        suggested_panels = sorted(list(set(suggested_panels)))
                # Handle list of dicts
                elif isinstance(library_sample_info, list):
                    panel_names = [
                        item.get("panel_name")
                        for item in library_sample_info
                        if isinstance(item, dict) and item.get("panel_name")
                    ]
                    suggested_panels = sorted(list(set(panel_names)))
            except Exception:
                # If extraction fails, just continue without suggestions
                pass

        # If we have suggested panels, show a selectbox with option to enter custom
        if suggested_panels:
            panel_options = suggested_panels + ["Enter custom panel name"]
            selected_option = st.selectbox(
                "Select panel name or enter custom:",
                panel_options,
                index=0,  # Default to first panel
                help=f"Suggested panel names from library sample info: {', '.join(suggested_panels)}",
            )

            if selected_option == "Enter custom panel name":
                return st.text_input(
                    "Enter panel name:", help="Identifier name for the panel."
                )
            else:
                return selected_option
        else:
            return st.text_input(
                "Enter panel name:", help="Identifier name for the panel."
            )

    def add_genome_information(self):
        st.subheader("Add Genome Information")
        genome_name = st.text_input("Name:", help="Name of the genome.")
        taxon_id = st.text_input("Taxon ID:", help="The NCBI taxonomy number.")
        version = st.text_input("Genome Version:", help="The genome version.")
        genome_url = st.text_input("URL:", help="A link to the genome file.")
        gff_url = st.text_input(
            "GFF URL (Optional):", help="A link to the genome’s annotation file"
        )
        genome_info = {
            "name": genome_name,
            "taxon_id": taxon_id,
            "url": genome_url,
            "genome_version": version,
        }
        if gff_url:
            genome_info["gff_url"] = gff_url
        return genome_info

    def transform_and_save_data(
        self,
        df,
        panel_ID,
        field_mapping,
        genome_info,
        selected_optional_fields,
        selected_additional_fields,
    ):
        if (
            all(
                [
                    panel_ID,
                    field_mapping,
                    genome_info["name"],
                    genome_info["taxon_id"],
                    genome_info["genome_version"],
                    genome_info["url"],
                ]
            )
            and selected_optional_fields != "Error"
        ):
            st.subheader("Transform Data")
            if st.button("Transform Data"):
                transformed_df = transform_panel_info(
                    df,
                    panel_ID,
                    field_mapping,
                    genome_info,
                    selected_optional_fields,
                    selected_additional_fields,
                )
                # json_data = json.dumps(transformed_df, indent=4)
                st.session_state["panel_info"] = transformed_df
                try:
                    self.panel_manager.save_panel(panel_ID, transformed_df)
                    st.success(f"Panel '{panel_ID}' has been saved!")
                except Exception as e:
                    st.error(f"Error saving panel: {e}")

    def display_panel_info(self, toggle_text):
        if session_name in st.session_state:
            preview = st.toggle(toggle_text)
            if preview:
                st.write(f"Current {title}:")
                st.json(st.session_state[session_name])

    def run(self):
        # Load past panel if applicable
        self.load_saved_panel()
        # Input for panel ID
        panel_ID = self.panel_id_input()

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

        # Add genome information
        genome_info = self.add_genome_information()

        # Transform and save data
        self.transform_and_save_data(
            df,
            panel_ID,
            mapped_fields,
            genome_info,
            selected_optional_fields,
            selected_additional_fields,
        )

        # Display current panel information
        self.display_panel_info(f"Preview {title}")


# Initialize and run the app
if __name__ == "__main__":
    render_header()
    st.subheader("Panel Information Converter", divider="gray")
    schema_fields = load_schema()
    required_fields = schema_fields["panel_info"]["required"]
    required_alternate_fields = schema_fields["panel_info"]["required_alternatives"]
    optional_fields = schema_fields["panel_info"]["optional"]
    optional_alternate_fields = schema_fields["panel_info"]["optional_alternatives"]
    app = PanelPage(
        os.path.join(os.getcwd(), "saved_panels"),
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
