import streamlit as st
from src.format_page import render_header


class BioInfoPage:
    # Constants
    REQUIRED_FIELDS = ["program", "program_version"]

    def __init__(self):
        self.bioinfo_method_infos = {}
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
        cols1 = st.columns(3)

        with cols1[0]:
            bioinfo_run_name = st.text_input(
                "Bioinformatics Run Name:",
                help="Name of the bioinformatics run.",
                key=f"run_name_{i}" if i else None,
            )
        with cols1[1]:
            bioinfo_methods_id = self._get_method_selection(i)

        with cols1[2]:
            bioinfo_run_date = st.date_input(
                "Bioinformatics Run Date (Optional):",
                value=None,
                help="The date the bioinformatics pipeline was run.",
            )
        bioinfo_run_dict = {
            "bioinformatics_run_name": bioinfo_run_name,
            "bioinformatics_methods_id": bioinfo_methods_id,
        }
        if bioinfo_run_date:
            bioinfo_run_dict["run_date"] = bioinfo_run_date

        return bioinfo_run_dict

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

    def _create_method_step_input_fields(self, method):
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
                "program version",
                key=f"{method}_version",
                help="Version number of the program (e.g., '1.16.0', '11.0.667')",
            )

        # Second row of columns
        cols2 = st.columns(2)
        with cols2[0]:
            program_description = st.text_input(
                "program description (optional)",
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
            "program_description": program_description,
            "additional_argument": additional_argument,
            "program_url": program_url,
        }

    def _build_method_step_dict(self, method, inputs):
        """Build method dictionary from inputs, filtering out empty values."""
        step_dict = {
            "program": inputs["program"],
            "program_version": inputs["program_version"],
        }

        # Add optional fields only if they have values
        for field in ["additional_argument", "program_description", "program_url"]:
            if inputs[field] and inputs[field].strip():
                step_dict[field] = inputs[field]

        return step_dict

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

    def enter_bioinfo_method_step_info(self, method):
        """Enter bioinformatics method values."""
        inputs = self._create_method_step_input_fields(method)
        method_dict = self._build_method_step_dict(method, inputs)

        # Add user specified additional fields
        method_dict = self.add_additional_fields(method, method_dict)
        return method_dict

    def _create_bioinformatics_methods_steps(self):
        """Create the bioinformatics methods section with at least one required."""
        st.subheader("Bioinformatics Method Steps")
        st.write(
            "Add at least one bioinformatics step to this method. You can add multiple steps as needed."
        )

        number_of_steps = st.number_input(
            "Number of bioinformatics steps:",
            min_value=1,
            value=1,
            help="You must add at least one bioinformatics step.",
            key="num_bioinformatics_methods",
        )

        method_steps = []
        for i in range(number_of_steps):
            st.write(f"**Step {i+1}**")

            method_data = self.enter_bioinfo_method_step_info(f"method_{i}")
            method_steps.append(method_data)

        return method_steps

    def _build_bioinfo_infos_method_dict(self, method_name, methods):
        """Build the bioinfo_infos dictionary."""
        # bioinfo_infos = methods.copy()
        method_dict = {"methods": methods}
        # Only add bioinformatics_method_name if it's populated
        if method_name and method_name.strip():
            method_dict["bioinformatics_method_name"] = method_name

        return method_dict

    def add_bioinfo_methods_information(self):
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
            method_steps = self._create_bioinformatics_methods_steps()

            self.bioinfo_method_infos = self._build_bioinfo_infos_method_dict(
                method_name, method_steps
            )
        else:
            # Set empty structure when not adding methods
            self.bioinfo_method_infos = {}

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

    def _validate_bioinformatics_methods(self, bioinfo_method_infos):
        """Validate all bioinformatics methods."""
        methods_validation = {}
        all_methods_valid = True

        # Check that at least one method is provided
        method_count = 0
        if "methods" in bioinfo_method_infos.keys():
            for method_data in bioinfo_method_infos["methods"]:
                # if method_name != "bioinformatics_method_name" and isinstance(
                #     method_data, dict
                # ):
                method_valid, method_missing = self.check_method_required_fields(
                    method_data
                )
                methods_validation[method_count] = (method_valid, method_missing)
                method_count += 1
                if not method_valid:
                    all_methods_valid = False

        if method_count == 0:
            all_methods_valid = False
            methods_validation["_no_methods"] = (
                False,
                ["At least one bioinformatics method is required"],
            )

        return methods_validation, all_methods_valid

    def _save_valid_method(self, bioinfo_method_infos):
        """Save a valid bioinformatics method."""
        st.session_state["bioinfo_methods_list"].append(bioinfo_method_infos)
        st.success("Bioinformatics method added successfully!")
        st.info(
            f"Total available methods: {len(st.session_state['bioinfo_methods_list'])}"
        )
        st.rerun()

    def _display_validation_errors(self, methods_validation):
        """Display validation errors for invalid methods."""
        for method_id, (method_valid, method_missing) in methods_validation.items():
            if not method_valid:
                if method_id == "_no_methods":
                    st.error("At least one bioinformatics method is required.")
                else:
                    st.error(
                        f"Step '{method_id+1}' is missing required fields: {', '.join(method_missing)}"
                    )

        st.warning("Please fill in all required fields before saving.")

    def transform_and_save_data(self):
        """Transform and save bioinformatics method data."""
        bioinfo_method_infos = self.bioinfo_method_infos

        # Only show save button if there's data to save
        # TODO: make this button only appear when add method toggle is on
        if st.button("Save Bioinformatics Method", key="save_bioinfo_method_infos"):
            # Validate all methods
            (
                methods_validation,
                all_methods_valid,
            ) = self._validate_bioinformatics_methods(bioinfo_method_infos)

            if all_methods_valid:
                self._save_valid_method(bioinfo_method_infos)
            else:
                self._display_validation_errors(methods_validation)

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

    def _update_run_info_indices(self, removed_indices):
        """Update bioinformatics run info indices after method removal."""
        if "bioinfo_run_infos" not in st.session_state:
            return

        updated_run_infos = []
        affected_runs = []

        for i, run_info in enumerate(st.session_state["bioinfo_run_infos"]):
            current_method_id = run_info.get("bioinformatics_methods_id", 0)
            run_name = run_info.get("bioinformatics_run_name", f"Run {i+1}")

            # Check if this run was using one of the removed methods
            if current_method_id in removed_indices:
                affected_runs.append(run_name)

            # Count how many removed indices are less than the current method ID
            # This tells us how much to subtract from the current method ID
            adjustment = sum(
                1 for removed_idx in removed_indices if removed_idx < current_method_id
            )

            # Update the method ID
            new_method_id = current_method_id - adjustment

            # If the new method ID is out of bounds, set it to a valid value
            max_method_id = len(st.session_state["bioinfo_methods_list"]) - 1
            if new_method_id > max_method_id:
                new_method_id = max(0, max_method_id)

            # Update the run info
            updated_run_info = run_info.copy()
            updated_run_info["bioinformatics_methods_id"] = new_method_id
            updated_run_infos.append(updated_run_info)

        st.session_state["bioinfo_run_infos"] = updated_run_infos

        # Show warning if any runs were affected
        if affected_runs:
            st.warning(
                f"Updated method references for affected runs: {', '.join(affected_runs)}"
            )

    def _remove_selected_methods(self, indices_to_remove):
        """Remove methods at specified indices."""
        # Store original indices before removal for updating run info
        original_indices = sorted(indices_to_remove)

        for idx in indices_to_remove:
            if 0 <= idx < len(st.session_state["bioinfo_methods_list"]):
                removed_method = st.session_state["bioinfo_methods_list"].pop(idx)
                method_name = removed_method.get(
                    "bioinformatics_method_name", f"Method {idx}"
                )
                st.success(f"Removed method: {method_name}")

        # Update run info indices after method removal
        self._update_run_info_indices(original_indices)

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
        self.add_bioinfo_methods_information()
        self.transform_and_save_data()
        self.display_info()


# Initialize and run the page
if __name__ == "__main__":
    render_header()
    st.subheader("Bioinformatics Run Information", divider="gray")
    app = BioInfoPage()
    app.run()
