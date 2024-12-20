import streamlit as st
from src.format_page import render_header
from src.format_page import BasicPage

# Initialize and run the app
if __name__ == "__main__":
    render_header()
    st.subheader("Specimen Level Metadata Converter", divider="gray")
    target_schema = ["specimen_id", "samp_taxon_id", "collection_date", "collection_country",
                     "collector", "samp_store_loc", "samp_collect_device", "project_name"]
    app = BasicPage(target_schema)
    app.run()
