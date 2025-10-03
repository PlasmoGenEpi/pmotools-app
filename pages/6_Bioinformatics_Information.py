import streamlit as st
from src.format_page import render_header


class BioInfoPage:
    def __init__(self):
        self.bioinfo_infos = {}
        # Initialize bioinfo_methods_list in session state if it doesn't exist
        if "bioinfo_methods_list" not in st.session_state:
            st.session_state["bioinfo_methods_list"] = []

    def enter_bioinfo_run_vals(self, i=None):
        cols1 = st.columns(2)
        with cols1[0]:
            bioinfo_run_name = st.text_input(
                "Bioinformatics Run Name:",
                help="Name of the bioinformatics run.",
                key=f"run_name_{i}" if i else None,
            )
        with cols1[1]:
            # Create dropdown options for bioinformatics methods
            if st.session_state["bioinfo_methods_list"]:
                # Create options with index and method name
                options = []
                for idx, method in enumerate(st.session_state["bioinfo_methods_list"]):
                    method_name = method.get("bioinformatics_method_name", "")
                    if method_name:
                        options.append(f"{idx}: {method_name}")
                    else:
                        options.append(f"{idx}: unnamed method {idx}")

                selected_option = st.selectbox(
                    "Bioinformatics Methods ID:",
                    options=options,
                    help="Select the bioinformatics method to use for this run.",
                    key=f"method_select_{i}" if i else None,
                )
                # Extract just the index from the selected option
                bioinfo_methods_id = int(selected_option.split(":")[0])
            else:
                st.warning(
                    "No bioinformatics methods available. Please add a method(s) below."
                )
                bioinfo_methods_id = 0

        return {
            "bioinformatics_run_name": bioinfo_run_name,
            "bioinformatics_methods_id": bioinfo_methods_id,
        }

    def add_bioinfo_run_vals(self):
        bioinfo_run_vals = []
        number_inputs = st.number_input(
            "Number of bioinformatics runs", min_value=0, value=1
        )
        bioinfo_run_vals = [
            self.enter_bioinfo_run_vals(i=i) for i in range(number_inputs)
        ]
        if st.button("Save Bioinformatics Run Info", key="save_bioinfo_run_vals"):
            st.session_state["bioinfo_run_infos"] = bioinfo_run_vals
            st.success("Bioinformatics run values saved successfully!")

        if "bioinfo_run_infos" in st.session_state.keys():
            preview_toggle = st.toggle(
                "Preview Bioinformatics Run Values", key="preview_bioinfo_run_vals"
            )
            if preview_toggle:
                st.write("Current Bioinformatics Run Values:")
                st.json(st.session_state["bioinfo_run_infos"])
        return bioinfo_run_vals

    def enter_bioinfo_method_vals(self, method):
        # First row of columns
        cols1 = st.columns(2)
        with cols1[0]:
            program = st.text_input(
                "program",
                key=f"{method}_program",
                help="Name of the software program or tool used (e.g., 'DADA2')",
            )
        with cols1[1]:
            version = st.text_input(
                "version",
                key=f"{method}_version",
                help="Version number of the program (e.g., '1.16.0', '11.0.667')",
            )

        # Second row of columns
        cols2 = st.columns(2)
        with cols2[0]:
            description = st.text_input(
                "description (optional)",
                key=f"{method}_description",
                help="Brief description of what this method does or how it was used",
            )
        with cols2[1]:
            additional_argument = st.text_input(
                "additional arguments (optional)",
                key=f"{method}_additional_argument",
                help="Any additional command-line arguments or parameters used",
            )

        # Third row for program URL (full width)
        program_url = st.text_input(
            "program url (optional)",
            key=f"{method}_program_url",
            help="URL to the program's website, documentation, or publication",
        )

        method_dict = {"program": program, "program_version": version}
        if additional_argument:
            method_dict["additional_argument"] = additional_argument
        if description:
            method_dict["description"] = description
        if program_url:
            method_dict["program_url"] = program_url
        # Add user specified additional fields
        method_dict = self.add_additional_fields(method, method_dict)
        return method_dict

    def add_additional_fields(self, method, dict):
        additional_fields_toggle = st.toggle(
            f"Add additional fields to {method}", key=f"{method}_toggle"
        )
        if additional_fields_toggle:
            st.write("Fill in the additional fields below:")

            number_inputs = st.number_input(
                "Number of additional inputs",
                min_value=0,
                value=1,
                key=f"{method}_num_fields",
            )
            # Inputs for names and values
            cols = st.columns(2)
            with cols[0]:
                field_names = [
                    st.text_input(f"Field Name {i}", key=f"field_name_{method}_{i}")
                    for i in range(number_inputs)
                ]
            with cols[1]:
                field_values = [
                    st.text_input(f"Value {i}", key=f"value_{method}_{i}")
                    for i in range(number_inputs)
                ]

            # Save the additional fields
            for i in range(number_inputs):
                dict[field_names[i]] = field_values[i]
        return dict

    def check_method_required_fields(self, dict, fields=["program", "program_version"]):
        missing_fields = []
        for field in fields:
            if field not in dict.keys() or not dict[field] or dict[field].strip() == "":
                missing_fields.append(field)
        if missing_fields:
            return False, missing_fields
        return True, []

    def add_bioinfo_information(self):
        st.subheader("Add Bioinformatics Method Information", divider="gray")

        # Show current methods count
        if st.session_state["bioinfo_methods_list"]:
            st.info(f"Current methods: {len(st.session_state['bioinfo_methods_list'])}")

        # Toggle to show/hide the add method form
        add_method_toggle = st.checkbox(
            "Add New Bioinformatics Method",
            help="Check this box to add a new bioinformatics method",
        )

        if add_method_toggle:
            bioinfo_method_name = st.text_input(
                "Bioinformatics Method Name (Optional):",
                help="A unique identifier for this bioinformatics method.",
            )

            # Required Methods
            st.subheader("Demultiplexing Method")
            demultiplexing_method_data = self.enter_bioinfo_method_vals(
                "demultiplexing_method"
            )

            st.subheader("Denoising Method")
            denoising_method_data = self.enter_bioinfo_method_vals("denoising_method")

            # Custom Methods
            st.subheader("Additional Methods (Optional)")
            add_custom_methods = st.checkbox(
                "Add Custom Methods", help="Add your own custom bioinformatics methods"
            )

            custom_methods = {}
            if add_custom_methods:
                st.write("Add your own custom bioinformatics methods:")
                number_custom_methods = st.number_input(
                    "Number of custom methods",
                    min_value=1,
                    value=1,
                    help="How many custom methods would you like to add?",
                )

                for i in range(number_custom_methods):
                    method_name = st.text_input(
                        f"Method Name {i+1}:",
                        key=f"custom_method_name_{i}",
                        help="Enter a descriptive name for your custom method (e.g., 'Quality Filtering', 'Taxonomic Assignment')",
                    )

                    if method_name:
                        st.write(f"**{method_name}**")
                        custom_method_data = self.enter_bioinfo_method_vals(
                            f"custom_method_{i}"
                        )
                        custom_methods[method_name] = custom_method_data

            # Put basic info into dict with flat structure
            self.bioinfo_infos = {
                "demultiplexing_method": demultiplexing_method_data,
                "denoising_method": denoising_method_data,
                **custom_methods,  # Spread custom methods into the main dict
                "bioinformatics_method_name": bioinfo_method_name,
            }
        else:
            # Set empty structure when not adding methods
            self.bioinfo_infos = {}

    def transform_and_save_data(self):
        bioinfo_infos = self.bioinfo_infos

        # Only show save button if there's data to save
        if bioinfo_infos and st.button(
            "Save Bioinformatic Method Info", key="save_bioinfo_method_infos"
        ):
            # Check if required methods exist and have required fields
            (
                demultiplexing_valid,
                demultiplexing_missing_fields,
            ) = self.check_method_required_fields(
                bioinfo_infos.get("demultiplexing_method", {}),
                ["program", "program_version"],
            )
            (
                denoising_valid,
                denoising_missing_fields,
            ) = self.check_method_required_fields(
                bioinfo_infos.get("denoising_method", {}),
                ["program", "program_version"],
            )

            # Check custom methods if they exist
            custom_methods_validation = {}
            custom_methods_valid = True
            for method_name, method_data in bioinfo_infos.items():
                if method_name not in [
                    "demultiplexing_method",
                    "denoising_method",
                    "bioinformatics_method_name",
                ]:
                    (
                        method_valid,
                        method_missing_fields,
                    ) = self.check_method_required_fields(
                        method_data, ["program", "program_version"]
                    )
                    custom_methods_validation[method_name] = (
                        method_valid,
                        method_missing_fields,
                    )
                    if not method_valid:
                        custom_methods_valid = False

            if demultiplexing_valid and denoising_valid and custom_methods_valid:
                # Append to the list instead of replacing
                st.session_state["bioinfo_methods_list"].append(bioinfo_infos)
                st.success("Bioinformatics method added successfully!")
                st.info(
                    f"Total available methods: {len(st.session_state['bioinfo_methods_list'])}"
                )
            else:
                # Show specific errors only when save is clicked
                if not demultiplexing_valid:
                    st.error(
                        "Demultiplexing method is missing required fields: {}".format(
                            ", ".join(demultiplexing_missing_fields)
                        )
                    )
                if not denoising_valid:
                    st.error(
                        "Denoising method is missing required fields: {}".format(
                            ", ".join(denoising_missing_fields)
                        )
                    )
                for method_name, validation_output in custom_methods_validation.items():
                    if not validation_output[0]:
                        st.error(
                            f"Custom method '{method_name}' is missing required fields: {', '.join(validation_output[1])}"
                        )
                st.warning("Please fill in all required fields before saving.")

    def display_info(self):
        if (
            "bioinfo_methods_list" in st.session_state
            or "bioinfo_run_infos" in st.session_state
        ):
            st.subheader("Preview Bioinformatics Information", divider="gray")
            if "bioinfo_run_infos" in st.session_state:
                preview_toggle = st.toggle("Preview Bioinformatics Run Information")
                if preview_toggle:
                    st.write("Current Bioinformatics Run Information:")
                    st.json(st.session_state["bioinfo_run_infos"])
            if (
                "bioinfo_methods_list" in st.session_state
                and st.session_state["bioinfo_methods_list"]
            ):
                preview_toggle = st.toggle("Preview Bioinformatics Methods List")
                if preview_toggle:
                    st.write("Current Bioinformatics Methods:")
                    for idx, method in enumerate(
                        st.session_state["bioinfo_methods_list"]
                    ):
                        st.write(f"**Method {idx}:**")
                        st.json(method)
                        st.write("---")

    def run(self):
        # Add bioinformatics information
        self.add_bioinfo_run_vals()
        self.add_bioinfo_information()
        self.transform_and_save_data()
        self.display_info()


# Initialize and run the page
if __name__ == "__main__":
    render_header()
    st.subheader("Bioinformatics Run Information", divider="gray")
    app = BioInfoPage()
    app.run()
