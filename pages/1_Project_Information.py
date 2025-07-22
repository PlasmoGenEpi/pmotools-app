import streamlit as st
from src.format_page import render_header


class ProjectInfoPage:
    def __init__(self):
        self.project_info = {}

    def add_required_project_information(self):
        st.subheader("Add Project Information")

        self.project_info["project_name"] = st.text_input(
            "Project Name:", help='A unique identifier for this project.')
        self.project_info["project_description"] = st.text_input(
            "Project Description:", help='A short description of the project.')

    def add_optional_info(self):
        st.subheader("Add Optional Fields")
        bioproject = st.text_input(
            "BioProject Accession:", help='An SRA bioproject accession e.g. PRJNA33823.')

        chief_scientist = st.text_input(
            "Project Collector Chief Scientist:", help='Can be collection of names separated by a semicolon if multiple people involved or can just be the name of the primary person managing the specimen.')
        contributors = st.text_input(
            "Project Contributors:", help='A list of collaborators who contributed to this project.')
        project_type = st.text_input(
            "Project Type:", help='the type of project conducted, e.g. TES vs surveillance vs transmission.')
        if bioproject:
            self.project_info["BioProject_accession"] = bioproject
        if chief_scientist:
            self.project_info["project_collector_chief_scientist"] = chief_scientist
        if contributors:
            self.project_info["project_contributors"] = contributors
        if project_type:
            self.project_info["project_type"] = project_type

    def add_additional_fields(self):
        st.subheader("Add Additional Fields")

        # Add a toggle to enable additional fields
        add_fields_toggle = st.checkbox("Add Additional Fields")

        if add_fields_toggle:
            st.write("Fill in the additional fields below:")
            number_inputs = st.number_input("Number of additional inputs",
                                            min_value=0, value=1)
            # Inputs for names and values
            cols = st.columns(2)
            with cols[0]:
                field_names = [st.text_input(
                    f'Field Name {i}', key=f"field_name_{i}") for i in range(number_inputs)]
            with cols[1]:
                field_values = [st.text_input(
                    f'Value {i}', key=f"value_{i}") for i in range(number_inputs)]

            # Save the additional fields
            for i in range(number_inputs):
                self.project_info[field_names[i]] = field_values[i]

    def transform_and_save_data(self):
        project_info = self.project_info
        if all([project_info["project_name"], project_info["project_description"]]):
            st.subheader("Save Data")
            if st.button("Save Data"):
                st.session_state["project_info"] = [project_info]

    def display_info(self):
        if "project_info" in st.session_state:
            st.subheader("Preview Project Information")
            preview_toggle = st.toggle("Preview Project Information")
            if preview_toggle:
                st.write("Current Project Information:")
                st.json(st.session_state["project_info"])

    def run(self):
        self.add_required_project_information()
        self.add_optional_info()
        self.add_additional_fields()
        self.transform_and_save_data()
        self.display_info()


# Initialize and run the page
if __name__ == "__main__":
    render_header()
    st.subheader("Project Information", divider="gray")
    app = ProjectInfoPage()
    app.run()
