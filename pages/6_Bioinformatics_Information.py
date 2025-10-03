import streamlit as st
from src.format_page import render_header


class BioInfoPage:
    # Constants
    REQUIRED_FIELDS = ["program", "program_version"]
    METHOD_TYPES = ["demultiplexing_method", "denoising_method"]

    def __init__(self):
        self.bioinfo_infos = {}
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize session state variables if they don't exist."""
        if "bioinfo_methods_list" not in st.session_state:
            st.session_state["bioinfo_methods_list"] = []

    def _create_method_dropdown_options(self):
        """Create dropdown options for bioinformatics methods."""
        options = []
        for idx, method in enumerate(st.session_state["bioinfo_methods_list"]):
            method_name = method.get("bioinformatics_method_name", "")
            if method_name:
                options.append(f"{idx}: {method_name}")
            else:
                options.append(f"{idx}: unnamed method {idx+1}")
        return options

    def _get_method_selection(self, i=None):
        """Get method selection from dropdown or show warning."""
        if not st.session_state["bioinfo_methods_list"]:
            st.warning(
                "No bioinformatics methods available. Please add a method(s) below."
            )
            return 0

        options = self._create_method_dropdown_options()
        methods_count = len(st.session_state["bioinfo_methods_list"])
        key = (
            f"method_select_{i}_{methods_count}"
            if i
            else f"method_select_{methods_count}"
        )

        selected_option = st.selectbox(
            "Bioinformatics Methods ID:",
            options=options,
            help="Select the bioinformatics method to use for this run.",
            key=key,
        )
        return int(selected_option.split(":")[0])

    def enter_bioinfo_run_vals(self, i=None):
        """Enter bioinformatics run values."""
        cols1 = st.columns(2)
        with cols1[0]:
            bioinfo_run_name = st.text_input(
                "Bioinformatics Run Name:",
                help="Name of the bioinformatics run.",
                key=f"run_name_{i}" if i else None,
            )
        with cols1[1]:
            bioinfo_methods_id = self._get_method_selection(i)

        return {
            "bioinformatics_run_name": bioinfo_run_name,
            "bioinformatics_methods_id": bioinfo_methods_id,
        }

    def _save_bioinfo_runs(self, bioinfo_run_vals):
        """Save bioinformatics run values to session state."""
        if st.button("Save Bioinformatics Run Info", key="save_bioinfo_run_vals"):
            st.session_state["bioinfo_run_infos"] = bioinfo_run_vals
            st.success("Bioinformatics run values saved successfully!")

    def _preview_bioinfo_runs(self):
        """Show preview of bioinformatics run values."""
        if "bioinfo_run_infos" in st.session_state:
            preview_toggle = st.toggle(
                "Preview Bioinformatics Run Values", key="preview_bioinfo_run_vals"
            )
            if preview_toggle:
                st.write("Current Bioinformatics Run Values:")
                st.json(st.session_state["bioinfo_run_infos"])

    def add_bioinfo_run_vals(self):
        """Add bioinformatics run values section."""
        number_inputs = st.number_input(
            "Number of bioinformatics runs",
            min_value=0,
            value=1,
            key="num_bioinfo_runs",
        )
        bioinfo_run_vals = [
            self.enter_bioinfo_run_vals(i=i) for i in range(number_inputs)
        ]

        self._save_bioinfo_runs(bioinfo_run_vals)
        return bioinfo_run_vals

    def _create_method_input_fields(self, method):
        """Create input fields for a bioinformatics method."""
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

        return {
            "program": program,
            "program_version": version,
            "description": description,
            "additional_argument": additional_argument,
            "program_url": program_url,
        }

    def _build_method_dict(self, method, inputs):
        """Build method dictionary from inputs, filtering out empty values."""
        method_dict = {
            "program": inputs["program"],
            "program_version": inputs["program_version"],
        }

        # Add optional fields only if they have values
        for field in ["additional_argument", "description", "program_url"]:
            if inputs[field] and inputs[field].strip():
                method_dict[field] = inputs[field]

        return method_dict

    def enter_bioinfo_method_vals(self, method):
        """Enter bioinformatics method values."""
        inputs = self._create_method_input_fields(method)
        method_dict = self._build_method_dict(method, inputs)

        # Add user specified additional fields
        method_dict = self.add_additional_fields(method, method_dict)
        return method_dict

    def _create_additional_fields_inputs(self, method, number_inputs):
        """Create input fields for additional custom fields."""
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
        return field_names, field_values

    def _add_custom_fields_to_dict(self, method_dict, field_names, field_values):
        """Add custom fields to the method dictionary."""
        for i, (name, value) in enumerate(zip(field_names, field_values)):
            if name and name.strip():  # Only add if field name is not empty
                method_dict[name] = value

    def add_additional_fields(self, method, method_dict):
        """Add additional custom fields to a method."""
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

            field_names, field_values = self._create_additional_fields_inputs(
                method, number_inputs
            )
            self._add_custom_fields_to_dict(method_dict, field_names, field_values)

        return method_dict

    def check_method_required_fields(self, method_dict, fields=None):
        """Check if required fields are present and not empty."""
        if fields is None:
            fields = self.REQUIRED_FIELDS

        missing_fields = []
        for field in fields:
            if (
                field not in method_dict.keys()
                or not method_dict[field]
                or method_dict[field].strip() == ""
            ):
                missing_fields.append(field)

        return (True, []) if not missing_fields else (False, missing_fields)

    def _show_methods_count(self):
        """Show current methods count."""
        if st.session_state["bioinfo_methods_list"]:
            st.info(f"Current methods: {len(st.session_state['bioinfo_methods_list'])}")

    def _get_method_name_input(self):
        """Get optional method name input."""
        return st.text_input(
            "Bioinformatics Method Name (Optional):",
            help="A unique identifier for this bioinformatics method.",
        )

    def _create_required_methods_section(self):
        """Create the required methods section (demultiplexing and denoising)."""
        st.subheader("Demultiplexing Method")
        demultiplexing_method_data = self.enter_bioinfo_method_vals(
            "demultiplexing_method"
        )

        st.subheader("Denoising Method")
        denoising_method_data = self.enter_bioinfo_method_vals("denoising_method")

        return demultiplexing_method_data, denoising_method_data

    def _create_custom_methods_section(self):
        """Create the custom methods section."""
        st.subheader("Additional Methods (Optional)")
        add_custom_methods = st.checkbox(
            "Add Custom Methods",
            help="Add your own custom bioinformatics methods",
            key="add_custom_methods_checkbox",
        )

        custom_methods = {}
        if add_custom_methods:
            st.write("Add your own custom bioinformatics methods:")
            number_custom_methods = st.number_input(
                "Number of custom methods",
                min_value=1,
                value=1,
                help="How many custom methods would you like to add?",
                key="num_custom_methods",
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

        return custom_methods

    def _build_bioinfo_infos_dict(
        self, method_name, demultiplexing_data, denoising_data, custom_methods
    ):
        """Build the bioinfo_infos dictionary."""
        bioinfo_infos = {
            "demultiplexing_method": demultiplexing_data,
            "denoising_method": denoising_data,
            **custom_methods,  # Spread custom methods into the main dict
        }

        # Only add bioinformatics_method_name if it's populated
        if method_name and method_name.strip():
            bioinfo_infos["bioinformatics_method_name"] = method_name

        return bioinfo_infos

    def add_bioinfo_information(self):
        """Add bioinformatics method information section."""
        st.subheader("Add Bioinformatics Method Information", divider="gray")

        self._show_methods_count()

        # Toggle to show/hide the add method form
        add_method_toggle = st.checkbox(
            "Add New Bioinformatics Method",
            help="Check this box to add a new bioinformatics method",
            key="add_new_bioinfo_method_checkbox",
        )

        if add_method_toggle:
            method_name = self._get_method_name_input()
            (
                demultiplexing_data,
                denoising_data,
            ) = self._create_required_methods_section()
            custom_methods = self._create_custom_methods_section()

            self.bioinfo_infos = self._build_bioinfo_infos_dict(
                method_name, demultiplexing_data, denoising_data, custom_methods
            )
        else:
            # Set empty structure when not adding methods
            self.bioinfo_infos = {}

    def _validate_required_methods(self, bioinfo_infos):
        """Validate demultiplexing and denoising methods."""
        (
            demultiplexing_valid,
            demultiplexing_missing,
        ) = self.check_method_required_fields(
            bioinfo_infos.get("demultiplexing_method", {})
        )
        denoising_valid, denoising_missing = self.check_method_required_fields(
            bioinfo_infos.get("denoising_method", {})
        )
        return (demultiplexing_valid, demultiplexing_missing), (
            denoising_valid,
            denoising_missing,
        )

    def _validate_custom_methods(self, bioinfo_infos):
        """Validate custom methods."""
        custom_methods_validation = {}
        custom_methods_valid = True

        for method_name, method_data in bioinfo_infos.items():
            if method_name not in self.METHOD_TYPES + ["bioinformatics_method_name"]:
                method_valid, method_missing = self.check_method_required_fields(
                    method_data
                )
                custom_methods_validation[method_name] = (method_valid, method_missing)
                if not method_valid:
                    custom_methods_valid = False

        return custom_methods_validation, custom_methods_valid

    def _save_valid_method(self, bioinfo_infos):
        """Save a valid bioinformatics method."""
        st.session_state["bioinfo_methods_list"].append(bioinfo_infos)
        st.success("Bioinformatics method added successfully!")
        st.info(
            f"Total available methods: {len(st.session_state['bioinfo_methods_list'])}"
        )
        st.rerun()

    def _display_validation_errors(
        self, demultiplexing_result, denoising_result, custom_methods_validation
    ):
        """Display validation errors for invalid methods."""
        demultiplexing_valid, demultiplexing_missing = demultiplexing_result
        denoising_valid, denoising_missing = denoising_result

        if not demultiplexing_valid:
            st.error(
                f"Demultiplexing method is missing required fields: {', '.join(demultiplexing_missing)}"
            )

        if not denoising_valid:
            st.error(
                f"Denoising method is missing required fields: {', '.join(denoising_missing)}"
            )

        for method_name, (
            method_valid,
            method_missing,
        ) in custom_methods_validation.items():
            if not method_valid:
                st.error(
                    f"Custom method '{method_name}' is missing required fields: {', '.join(method_missing)}"
                )

        st.warning("Please fill in all required fields before saving.")

    def transform_and_save_data(self):
        """Transform and save bioinformatics method data."""
        bioinfo_infos = self.bioinfo_infos

        # Only show save button if there's data to save
        if bioinfo_infos and st.button(
            "Save Bioinformatic Method Info", key="save_bioinfo_method_infos"
        ):
            # Validate all methods
            demultiplexing_result, denoising_result = self._validate_required_methods(
                bioinfo_infos
            )
            (
                custom_methods_validation,
                custom_methods_valid,
            ) = self._validate_custom_methods(bioinfo_infos)

            demultiplexing_valid, _ = demultiplexing_result
            denoising_valid, _ = denoising_result

            if demultiplexing_valid and denoising_valid and custom_methods_valid:
                self._save_valid_method(bioinfo_infos)
            else:
                self._display_validation_errors(
                    demultiplexing_result, denoising_result, custom_methods_validation
                )

        self._remove_methods_section()

    def _create_remove_options(self):
        """Create options for method removal."""
        remove_options = []
        for idx, method in enumerate(st.session_state["bioinfo_methods_list"]):
            method_name = method.get("bioinformatics_method_name", "")
            if method_name:
                remove_options.append(f"{idx}: {method_name}")
            else:
                remove_options.append(f"{idx}: unnamed method {idx+1}")
        return remove_options

    def _extract_removal_indices(self, selected_options):
        """Extract indices from selected removal options."""
        indices_to_remove = []
        for option in selected_options:
            idx = int(option.split(":")[0])
            indices_to_remove.append(idx)
        return sorted(
            indices_to_remove, reverse=True
        )  # Sort descending for safe removal

    def _remove_selected_methods(self, indices_to_remove):
        """Remove methods at specified indices."""
        for idx in indices_to_remove:
            if 0 <= idx < len(st.session_state["bioinfo_methods_list"]):
                removed_method = st.session_state["bioinfo_methods_list"].pop(idx)
                method_name = removed_method.get(
                    "bioinformatics_method_name", f"Method {idx}"
                )
                st.success(f"Removed method: {method_name}")

        st.info(f"Remaining methods: {len(st.session_state['bioinfo_methods_list'])}")
        st.rerun()

    def _remove_methods_section(self):
        """Display the remove methods section."""
        if not st.session_state["bioinfo_methods_list"]:
            return

        st.subheader("Remove Methods")
        remove_method_toggle = st.checkbox(
            "Remove Existing Methods",
            help="Check this box to remove existing bioinformatics methods",
            key="remove_existing_methods_checkbox",
        )

        if remove_method_toggle:
            remove_options = self._create_remove_options()

            if remove_options:
                selected_methods_to_remove = st.multiselect(
                    "Select methods to remove:",
                    options=remove_options,
                    help="Select one or more methods to remove",
                    key="select_methods_to_remove_multiselect",
                )

                if selected_methods_to_remove and st.button(
                    "Remove Selected Methods",
                    type="secondary",
                    key="remove_selected_methods_button",
                ):
                    indices_to_remove = self._extract_removal_indices(
                        selected_methods_to_remove
                    )
                    self._remove_selected_methods(indices_to_remove)
            else:
                st.warning("No methods available to remove.")

    def _preview_bioinfo_runs(self):
        """Preview bioinformatics run information."""
        if "bioinfo_run_infos" in st.session_state:
            preview_toggle = st.toggle(
                "Preview Bioinformatics Run Information",
                key="preview_bioinfo_runs_toggle",
            )
            if preview_toggle:
                st.write("Current Bioinformatics Run Information:")
                st.json(st.session_state["bioinfo_run_infos"])

    def _preview_bioinfo_methods(self):
        """Preview bioinformatics methods list."""
        if (
            "bioinfo_methods_list" in st.session_state
            and st.session_state["bioinfo_methods_list"]
        ):
            preview_toggle = st.toggle(
                "Preview Bioinformatics Methods List",
                key="preview_bioinfo_methods_toggle",
            )
            if preview_toggle:
                st.write("Current Bioinformatics Methods:")
                for idx, method in enumerate(st.session_state["bioinfo_methods_list"]):
                    st.write(f"**Method {idx}:**")
                    st.json(method)
                    st.write("---")

    def display_info(self):
        """Display preview information for bioinformatics data."""
        if (
            "bioinfo_methods_list" in st.session_state
            or "bioinfo_run_infos" in st.session_state
        ):
            st.subheader("Preview Bioinformatics Information", divider="gray")
            self._preview_bioinfo_runs()
            self._preview_bioinfo_methods()

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
