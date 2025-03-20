import streamlit as st
import json
import os
from src.format_page import render_header

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
    for check_key, source_page in check_dict.items():
        if check_key in st.session_state:
            st.success(f'Data from {source_page} tab has been successfully'
                ' loaded')
            print('key is', check_key, 'keys are', st.session_state[check_key].keys())
        else:
            st.error(f'Data from {source_page} tab not found. Please fill out'
            f' the {source_page} tab (the link is at the left side of this'
            ' page) before proceeding')
            all_passed=False
    return all_passed

def merge_data():
    # MERGE DATA
    st.subheader("Merge Components to Final PMO")
    panel_info = st.session_state["panel_info"]
    panel_id = ', '.join(panel_info["panel_info"].keys())
    bioinfo_id = ', '.join(st.session_state["mhap_data"]["microhaplotypes_detected"].keys())
    formatted_pmo = {
        "experiment_infos": st.session_state["experiment_info"],
        "sequencing_infos": st.session_state["seq_info"],
        "specimen_infos": st.session_state["specimen_info"],
        "taramp_bioinformatics_infos": st.session_state["bioinfo_infos"],
        **st.session_state["mhap_data"],
        **panel_info,
        **st.session_state["demultiplexed_data"],
    }
    file_string=json.dumps(formatted_pmo, indent=4)
    st.download_button('Download Final PMO', file_string, file_name='final_pmo.json')


# Initialize and run the app
if __name__ == "__main__":
    current_directory = os.getcwd()  # Get the current working directory
    SAVE_DIR = os.path.join(current_directory, "finished_PMO_files")
    os.makedirs(SAVE_DIR, exist_ok=True)
    render_header()
    st.subheader("Create Final PMO", divider="gray")
    st.subheader("Components")
    if check_all(check_dict):
        merge_data()