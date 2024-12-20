import streamlit as st
from src.format_page import render_header
from src.format_page import BasicPage

# Initialize and run the app
if __name__ == "__main__":
    render_header()
    st.subheader("Experiment Level Metadata Converter", divider="gray")
    target_schema = ["sequencing_info_id", "specimen_id",
                     "panel_id", "experiment_sample_id",]
    app = BasicPage(target_schema)
    app.run()
