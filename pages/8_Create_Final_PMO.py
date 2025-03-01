import streamlit as st
import json
import os
from src.format_page import render_header

#the checks almost look like they could be generalized but they all have
#different print statements on success. If we could standardize these somewhat,
#it should be possible to generalize the check functions
#def check_missing(key_value, error_message, success_message)

check_dict={'panel_info':'Panel Information',
'specimen_info': 'Specimen Level Metadata',
'experiment_info':'Experiment Level Metadata',
'mhap_data':'Microhaplotype Information',
'demultiplexed_data':'Demultiplexed Samples',
'seq_info':'Sequencing Information',
'bioinfo_infos':'Bioinformatics Information'}

def check_all(check_dict):
    '''
    checks if outputs of a given page exists, and refers user to the page to
    populate if the page doesn't exist 
    '''
    all_passed=True
    for check_key in check_dict:
        source_page=check_dict[check_key]
        if check_key in st.session_state:
            st.write(f'Data from {source_page} tab has been successfully'
                ' loaded')
        else:
            st.error(f'Data from {source_page} tab not found. Please fill out'
            f' the {source_page} tab (the link is at the left side of this'
            ' page) before proceeding')
            all_passed=False
            break
    return all_passed

def merge_data():
    # MERGE DATA
    st.subheader("Merge Components to Final PMO")
    panel_info = st.session_state["panel_info"]
    panel_id = ', '.join(panel_info["panel_info"].keys())
    bioinfo_id = ', '.join(st.session_state["mhap_data"]["microhaplotypes_detected"].keys())
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

# Initialize and run the app
if __name__ == "__main__":
    current_directory = os.getcwd()  # Get the current working directory
    SAVE_DIR = os.path.join(current_directory, "finished_PMO_files")
    os.makedirs(SAVE_DIR, exist_ok=True)
    render_header()
    st.subheader("Create Final PMO", divider="gray")
    st.subheader("Components")
    all_passed=check_all(check_dict)
    if all_passed:
        merge_data()
