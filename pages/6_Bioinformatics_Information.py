import streamlit as st
from src.format_page import render_header


class ValidationHelper:
    """Helper class for validation logic."""

    REQUIRED_FIELDS = ["program", "program_version"]

    @staticmethod
    def check_method_required_fields(method_dict, fields=None):
        """Check if required fields are present and not empty."""
        if fields is None:
            fields = ValidationHelper.REQUIRED_FIELDS

        missing_fields = []
        for field in fields:
            if (
                field not in method_dict.keys()
                or not method_dict[field]
                or method_dict[field].strip() == ""
            ):
                missing_fields.append(field)

        return (True, []) if not missing_fields else (False, missing_fields)

    @staticmethod
    def validate_runs(bioinfo_run_vals, methods_list):
        """Validate bioinformatics runs."""
        if not methods_list:
            return False, [
                "No bioinformatics methods available. Please add at least one bioinformatics method before saving run information."
            ]

        missing_names = []
        missing_methods = []
        invalid_methods = []
        methods_count = len(methods_list)

        for i, run_val in enumerate(bioinfo_run_vals):
            run_name = run_val.get("bioinformatics_run_name", "")
            if not run_name or not run_name.strip():
                missing_names.append(i + 1)

            methods_id = run_val.get("bioinformatics_methods_id")
            if methods_id is None:
                missing_methods.append(i + 1)
            elif not (0 <= methods_id < methods_count):
                invalid_methods.append(i + 1)

        errors = []
        if missing_names:
            if len(missing_names) == 1:
                errors.append(f"Run {missing_names[0]} is missing a required run name.")
            else:
                errors.append(
                    f"Runs {', '.join(map(str, missing_names))} are missing required run names."
                )

        if missing_methods:
            if len(missing_methods) == 1:
                errors.append(
                    f"Run {missing_methods[0]} is missing a required bioinformatics methods ID."
                )
            else:
                errors.append(
                    f"Runs {', '.join(map(str, missing_methods))} are missing required bioinformatics methods IDs."
                )

        if invalid_methods:
            if len(invalid_methods) == 1:
                errors.append(
                    f"Run {invalid_methods[0]} has an invalid bioinformatics methods ID."
                )
            else:
                errors.append(
                    f"Runs {', '.join(map(str, invalid_methods))} have invalid bioinformatics methods IDs."
                )

        return len(errors) == 0, errors

    @staticmethod
    def validate_methods(bioinfo_method_infos):
        """Validate all bioinformatics methods."""
        methods_validation = {}
        all_methods_valid = True
        method_count = 0

        if "methods" in bioinfo_method_infos.keys():
            for method_data in bioinfo_method_infos["methods"]:
                (
                    method_valid,
                    method_missing,
                ) = ValidationHelper.check_method_required_fields(method_data)
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


class BioinformaticsRunManager:
    """Manages bioinformatics run information."""

    def __init__(self):
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
            if i is not None
            else f"method_select_{methods_count}"
        )

        selected_option = st.selectbox(
            "Bioinformatics Methods ID:",
            options=options,
            help="Select the bioinformatics method to use for this run (required).",
            key=key,
        )
        return int(selected_option.split(":")[0])

    def _enter_run_values(self, i=None):
        """Enter bioinformatics run values."""
        cols1 = st.columns(3)

        with cols1[0]:
            bioinfo_run_name = st.text_input(
                "Bioinformatics Run Name:",
                help="Name of the bioinformatics run (required).",
                key=f"run_name_{i}" if i is not None else None,
            )
        with cols1[1]:
            bioinfo_methods_id = self._get_method_selection(i)

        with cols1[2]:
            bioinfo_run_date = st.date_input(
                "Bioinformatics Run Date (Optional):",
                value=None,
                help="The date the bioinformatics pipeline was run.",
                key=f"run_date_{i}" if i is not None else None,
            )

        bioinfo_run_dict = {
            "bioinformatics_run_name": bioinfo_run_name,
            "bioinformatics_methods_id": bioinfo_methods_id,
        }
        if bioinfo_run_date:
            bioinfo_run_dict["run_date"] = bioinfo_run_date

        return bioinfo_run_dict

    def _save_runs(self, bioinfo_run_vals):
        """Save bioinformatics run values to session state."""
        if st.button("Save Bioinformatics Run Info", key="save_bioinfo_run_vals"):
            methods_list = st.session_state.get("bioinfo_methods_list", [])
            is_valid, errors = ValidationHelper.validate_runs(
                bioinfo_run_vals, methods_list
            )

            if not is_valid:
                for error in errors:
                    st.error(error)
                if len(errors) > 1 or "No bioinformatics methods" not in errors[0]:
                    st.warning("Please fill in all required fields before saving.")
            else:
                st.session_state["bioinfo_run_infos"] = bioinfo_run_vals
                st.success("Bioinformatics run values saved successfully!")

    def add_runs(self):
        """Add bioinformatics run values section."""
        number_inputs = st.number_input(
            "Number of bioinformatics runs",
            min_value=0,
            value=1,
            key="num_bioinfo_runs",
        )
        bioinfo_run_vals = [self._enter_run_values(i=i) for i in range(number_inputs)]

        self._save_runs(bioinfo_run_vals)
        return bioinfo_run_vals

    def preview_runs(self):
        """Preview bioinformatics run information."""
        if "bioinfo_run_infos" in st.session_state:
            preview_toggle = st.toggle(
                "Preview Bioinformatics Run Information",
                key="preview_bioinfo_runs_toggle",
            )
            if preview_toggle:
                st.write("Current Bioinformatics Run Information:")
                st.json(st.session_state["bioinfo_run_infos"])


class BioinformaticsMethodManager:
    """Manages bioinformatics method information."""

    def __init__(self):
        self.bioinfo_method_infos = {}

    def _show_methods_count(self):
        """Show current methods count."""
        if st.session_state.get("bioinfo_methods_list"):
            st.info(f"Current methods: {len(st.session_state['bioinfo_methods_list'])}")

    def _get_method_name_input(self):
        """Get optional pipeline name input."""
        st.subheader("Pipeline (Optional)")
        st.write(
            "Putting in the pipeline information is optional. If you add information you must add both program and program version."
        )
        pipeline_dict = self._create_method_step_input_fields(0)
        return pipeline_dict["program"], pipeline_dict

    def _create_method_step_input_fields(self, method):
        """Create input fields for a bioinformatics method."""
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
        for name, value in zip(field_names, field_values):
            if name and name.strip():
                method_dict[name] = value

    def _add_additional_fields(self, method, method_dict):
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

    def _enter_method_step_info(self, method):
        """Enter bioinformatics method values."""
        inputs = self._create_method_step_input_fields(method)
        method_dict = self._build_method_step_dict(method, inputs)
        method_dict = self._add_additional_fields(method, method_dict)
        return method_dict

    def _create_methods_steps(self):
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
            method_data = self._enter_method_step_info(f"method_{i}")
            method_steps.append(method_data)

        return method_steps

    def _build_method_dict(self, method_name, methods):
        """Build the bioinfo_infos dictionary."""
        method_dict = {"methods": methods}
        if method_name and method_name.strip():
            method_dict["bioinformatics_method_name"] = method_name
        return method_dict

    def add_methods_information(self):
        """Add bioinformatics method information section."""
        st.subheader("Add Bioinformatics Method Information", divider="gray")
        self._show_methods_count()

        add_method_toggle = st.checkbox(
            "Add New Bioinformatics Method",
            help="Check this box to add a new bioinformatics method",
            key="add_new_bioinfo_method_checkbox",
        )

        if add_method_toggle:
            method_name, pipeline_dict = self._get_method_name_input()
            method_steps = self._create_methods_steps()
            self.bioinfo_method_infos = self._build_method_dict(
                method_name, method_steps
            )
        else:
            self.bioinfo_method_infos = {}

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

    def save_method(self):
        """Transform and save bioinformatics method data."""
        bioinfo_method_infos = self.bioinfo_method_infos

        if st.button("Save Bioinformatics Method", key="save_bioinfo_method_infos"):
            methods_validation, all_methods_valid = ValidationHelper.validate_methods(
                bioinfo_method_infos
            )

            if all_methods_valid:
                self._save_valid_method(bioinfo_method_infos)
            else:
                self._display_validation_errors(methods_validation)

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
        return sorted(indices_to_remove, reverse=True)

    def _update_run_info_indices(self, removed_indices):
        """Update bioinformatics run info indices after method removal."""
        if "bioinfo_run_infos" not in st.session_state:
            return

        updated_run_infos = []
        affected_runs = []

        for i, run_info in enumerate(st.session_state["bioinfo_run_infos"]):
            current_method_id = run_info.get("bioinformatics_methods_id", 0)
            run_name = run_info.get("bioinformatics_run_name", f"Run {i+1}")

            if current_method_id in removed_indices:
                affected_runs.append(run_name)

            adjustment = sum(
                1 for removed_idx in removed_indices if removed_idx < current_method_id
            )

            new_method_id = current_method_id - adjustment
            max_method_id = len(st.session_state["bioinfo_methods_list"]) - 1
            if new_method_id > max_method_id:
                new_method_id = max(0, max_method_id)

            updated_run_info = run_info.copy()
            updated_run_info["bioinformatics_methods_id"] = new_method_id
            updated_run_infos.append(updated_run_info)

        st.session_state["bioinfo_run_infos"] = updated_run_infos

        if affected_runs:
            st.warning(
                f"Updated method references for affected runs: {', '.join(affected_runs)}"
            )

    def _remove_selected_methods(self, indices_to_remove):
        """Remove methods at specified indices."""
        original_indices = sorted(indices_to_remove)

        for idx in indices_to_remove:
            if 0 <= idx < len(st.session_state["bioinfo_methods_list"]):
                removed_method = st.session_state["bioinfo_methods_list"].pop(idx)
                method_name = removed_method.get(
                    "bioinformatics_method_name", f"Method {idx}"
                )
                st.success(f"Removed method: {method_name}")

        self._update_run_info_indices(original_indices)
        st.info(f"Remaining methods: {len(st.session_state['bioinfo_methods_list'])}")
        st.rerun()

    def remove_methods_section(self):
        """Display the remove methods section."""
        if not st.session_state.get("bioinfo_methods_list"):
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

    def preview_methods(self):
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


class BioInfoPage:
    """Main page class that coordinates bioinformatics information management."""

    def __init__(self):
        self.run_manager = BioinformaticsRunManager()
        self.method_manager = BioinformaticsMethodManager()

    def display_info(self):
        """Display preview information for bioinformatics data."""
        if (
            "bioinfo_methods_list" in st.session_state
            or "bioinfo_run_infos" in st.session_state
        ):
            st.subheader("Preview Bioinformatics Information", divider="gray")
            self.run_manager.preview_runs()
            self.method_manager.preview_methods()

    def run(self):
        """Run the complete bioinformatics information page."""
        self.run_manager.add_runs()
        self.method_manager.add_methods_information()
        self.method_manager.save_method()
        self.method_manager.remove_methods_section()
        self.display_info()


# Initialize and run the app
if __name__ == "__main__":
    render_header()
    st.subheader("Bioinformatics Run Information", divider="gray")
    app = BioInfoPage()
    app.run()
