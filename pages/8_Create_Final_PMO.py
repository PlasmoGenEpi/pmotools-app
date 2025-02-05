import streamlit as st
import json
import os
from src.format_page import render_header

current_directory = os.getcwd()  # Get the current working directory
SAVE_DIR = os.path.join(current_directory, "PMO")
os.makedirs(SAVE_DIR, exist_ok=True)

render_header()
st.subheader("Create Final PMO", divider="gray")

st.subheader("Components")
# PANEL INFO
if "panel_info" in st.session_state:
    panel_info = st.session_state["panel_info"]
    panel_id = ', '.join(panel_info["panel_info"].keys())
    st.write("**Current Panel Information:**", panel_id)
else:
    st.error(
        "No panel information found. Please go to the Panel Information tab before proceeding.")

# SPECIMEN INFO
if "specimen_info" in st.session_state:
    spec_samples = ', '.join(
        list(st.session_state["specimen_info"].keys())[:10])
    st.write("**Current Specimen Information for samples (showing first 10):** ",
             spec_samples, '...')
else:
    st.error(
        "No specimen information found. Please go to the Specimen Information tab before proceeding.")

# EXPERIMENT INFO
if "experiment_info" in st.session_state:
    experiment_samples = ', '.join(
        list(st.session_state["experiment_info"].keys())[:10])
    st.write("**Current Experiment Information for samples (showing first 10):** ",
             experiment_samples, '...')
else:
    st.error(
        "No experiment information found. Please go to the Experiment Information tab before proceeding.")

# MICROHAPLOTYPE INFO
if "mhap_data" in st.session_state:
    bioinfo_id = ', '.join(st.session_state["mhap_data"]["microhaplotypes_detected"].keys()
                           )
    st.write(
        "**Current Microhaplotype Information from bioinformatics run:**", bioinfo_id)
else:
    st.error(
        "No microhaplotype information found. Please go to the Microhaplotype Information tab before proceeding.")

# DEMULTIPLEXED INFO
if "demultiplexed_data" in st.session_state:
    # demultiplexed_data = st.session_state["demultiplexed_data"]
    demultiplexed_bioinfo_id = st.session_state["demultiplexed_data"].keys()
    st.write("**Current Demultiplexed Information from bioinformatics run:**",
             ', '.join(demultiplexed_bioinfo_id))
else:
    st.error(
        "No demultiplexed information found. Please go to the Demultiplexed Samples tab before proceeding.")

# SEQUENCING INFO
if "seq_info" in st.session_state:
    seq_info_id = st.session_state["seq_info"].keys(
    )
    st.write("**Current Sequencing Information had ID:**",
             ', '.join(seq_info_id))
else:
    st.error(
        "No sequencing information found. Please go to the Sequencing Information tab before proceeding.")

# BIOINFORMATICS INFO
if "bioinfo_infos" in st.session_state:
    bioinfo_info_id = st.session_state["bioinfo_infos"]["tar_amp_bioinformatics_info_id"]
    st.write("**Current Bioinformatics Information had ID:**", bioinfo_info_id)
else:
    st.error(
        "No bioinformatics information found. Please go to the Bioinformatics Information tab before proceeding.")

# MERGE DATA
st.subheader("Merge Components to Final PMO")
if st.button("Merge Data"):
    formatted_pmo = {
        "experiment_infos": st.session_state["experiment_info"],
        "sequencing_infos": st.session_state["seq_info"],
        "specimen_infos": st.session_state["specimen_info"],
        "taramp_bioinformatics_infos": st.session_state["bioinfo_infos"],
        **st.session_state["mhap_data"],
        **panel_info,
        **st.session_state["demultiplexed_data"],
    }
    output_path = os.path.join(SAVE_DIR, f"{panel_id}_{bioinfo_id}.json")
    with open(output_path, "w") as f:
        json.dump(formatted_pmo, f, indent=4)
    st.success(f"Your PMO has been saved! It can be found here: {output_path}")
