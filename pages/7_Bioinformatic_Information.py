import streamlit as st
from src.format_page import render_header


class BioInfoPage:
    def __init__(self):
        self.bioinfo_infos = {}

    def enter_bioinfo_method_vals(self, method):
        cols = st.columns(4)
        with cols[0]:
            program = st.text_input(f'program', key=f"{method}_program")
        with cols[1]:
            purpose = st.text_input(f'purpose', key=f"{method}_purpose")
        with cols[2]:
            version = st.text_input(f'version', key=f"{method}_version")
        with cols[3]:
            additional_argument = st.text_input(
                f'additional argument (optional)', key=f"{method}_additional_argument")
        method_dict = {"program": program,
                       "purpose": purpose,
                       "version": version}
        if additional_argument:
            method_dict["additional_argument"] = additional_argument
        # Add user specified additional fields
        method_dict = self.add_additional_fields(method, method_dict)
        return method_dict

    def add_additional_fields(self, method, dict):
        additional_fields_toggle = st.toggle(
            f"Add additional fields to {method}", key=f"{method}_toggle")
        if additional_fields_toggle:
            st.write("Fill in the additional fields below:")

            number_inputs = st.number_input("Number of additional inputs",
                                            min_value=0, value=1, key=f"{method}_num_fields")
            # Inputs for names and values
            cols = st.columns(2)
            with cols[0]:
                field_names = [st.text_input(
                    f'Field Name {i}', key=f"field_name_{method}_{i}") for i in range(number_inputs)]
            with cols[1]:
                field_values = [st.text_input(
                    f'Value {i}', key=f"value_{method}_{i}") for i in range(number_inputs)]

            # Save the additional fields
            for i in range(number_inputs):
                dict[field_names[i]] = field_values[i]
        return dict

    def check_method_required_fields(self, dict, fields=["program", "purpose", "version"]):
        for field in fields:
            if field not in dict.keys():
                return False
        return True

    def add_bioinfo_information(self):
        st.subheader("Add Bioinformatics Information")

        bioinfo_info_id = st.text_input(
            "Bioinformatics Information ID:", help='A unique identifier for this targeted amplicon bioinformatics pipeline run.')

        # Required Methods
        st.subheader("Demultiplexing Method")
        demultiplexing_method_dict = {
            "demultiplexing_method": self.enter_bioinfo_method_vals("demultiplexing_method")}
        st.subheader("Denoising Method")
        denoising_method_dict = {
            "denoising_method": self.enter_bioinfo_method_vals("denoising_method")}
        # Put basic info into dict
        self.bioinfo_infos = {
            "demultiplexing_method": demultiplexing_method_dict,
            "denoising_method": denoising_method_dict,
            "tar_amp_bioinformatics_info_id": bioinfo_info_id
        }

        # # Optional
        # st.subheader("Add Optional Methods")
        # pop_clust_method_dict = {}
        # pop_clust_box = st.checkbox(label="Population Clustering Method")
        # if pop_clust_box:
        #     pop_clust_method_dict["pop_clust_method"] = self.enter_bioinfo_method_vals(
        #         "pop_clust_method")
        # # if self.check_method_required_fields(pop_clust_method_dict):
        # self.bioinfo_infos["pop_clust_method"] = pop_clust_method_dict

        # # Add additional methods
        # st.subheader("Additional Methods")
        # additional_methods = st.toggle("Add additional Method Definitions")
        # if additional_methods:
        #     st.write(
        #         "Fill in the additional methods you would like to add the details of:")

        #     number_extra_methods = st.number_input(
        #         "Number of additional inputs", min_value=0, value=1, key=f"number_extra_methods")
        #     additional_methods = [st.text_input(
        #         f'Method Name {i}', key=f"method_name_{i}") for i in range(number_extra_methods)]

        #     for method in additional_methods:
        #         if method:
        #             st.subheader(method)
        #             new_method_dict = self.enter_bioinfo_method_vals(method)
        #             self.bioinfo_infos[method] = new_method_dict

    def display_info(self):
        if "bioinfo_infos" in st.session_state:
            st.subheader("Preview Bioinformatics Information")
            preview_toggle = st.toggle("Preview Bioinformatics Information")
            if preview_toggle:
                st.write("Current Bioinformatics Information:")
                st.json(st.session_state["bioinfo_infos"])

    def transform_and_save_data(self):
        bioinfo_infos = self.bioinfo_infos
        if all([bioinfo_infos["demultiplexing_method"], bioinfo_infos["denoising_method"], bioinfo_infos["tar_amp_bioinformatics_info_id"],]):
            st.subheader("Save Data")
            if st.button("Save Data"):
                st.session_state["bioinfo_infos"] = bioinfo_infos

    def run(self):
        # Add bioinformatics information
        self.add_bioinfo_information()
        self.transform_and_save_data()
        self.display_info()


# Initialize and run the page
if __name__ == "__main__":
    render_header()
    st.subheader("Bioinformatics Information", divider="gray")
    app = BioInfoPage()
    app.run()
