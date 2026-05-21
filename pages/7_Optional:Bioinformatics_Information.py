import streamlit as st
import pandas as pd
from src.format_page import render_header
from src.field_matcher import load_data
from src.utils import load_schema


def parse_list_field(value):
    """
    Parse a string that looks like a list into an actual list.
    Splits on commas but respects quoted substrings (single or double quotes).
    Parses character by character, toggling in_quote when a quote is encountered.

    Examples:
        "[--illumina, '--qualThres 25,20']" -> ["--illumina", "--qualThres 25,20"]
        "--illumina, --paired" -> ["--illumina", "--paired"]
        "single_value" -> "single_value" (returned as-is if no list-like structure)
    """
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        stripped = stripped[1:-1].strip()
    elif "," not in stripped:
        return value

    tokens = []
    current = []
    in_quote = False
    quote_char = None

    for char in stripped:
        if char in ('"', "'"):
            if not in_quote:
                # entering a quoted section
                in_quote = True
                quote_char = char
                # don't append the quote char itself
            elif char == quote_char:
                # closing the quoted section
                in_quote = False
                quote_char = None
                # don't append the quote char itself
            else:
                # different quote char inside a quoted section — treat as literal
                current.append(char)
        elif char == "," and not in_quote:
            token = "".join(current).strip()
            if token:
                tokens.append(token)
            current = []
        else:
            current.append(char)

    # Don't forget the last token
    last = "".join(current).strip()
    if last:
        tokens.append(last)

    return tokens if len(tokens) > 1 else (tokens[0] if tokens else value)


class ValidationHelper:
    """Helper class for validation logic."""

    REQUIRED_FIELDS = ["program", "program_version"]

    @staticmethod
    def check_method_required_fields(method_dict, fields=None):
        if fields is None:
            fields = ValidationHelper.REQUIRED_FIELDS
        missing_fields = [
            f
            for f in fields
            if f not in method_dict
            or not method_dict[f]
            or str(method_dict[f]).strip() == ""
        ]
        return (True, []) if not missing_fields else (False, missing_fields)

    @staticmethod
    def validate_runs(bioinfo_run_vals, methods_list):
        if not methods_list:
            return False, [
                "No bioinformatics methods available. Please add at least one bioinformatics method before saving run information."
            ]
        missing_names, missing_methods, invalid_methods = [], [], []
        methods_count = len(methods_list)
        for i, run_val in enumerate(bioinfo_run_vals):
            if not run_val.get("bioinformatics_run_name", "").strip():
                missing_names.append(i + 1)
            methods_id = run_val.get("bioinformatics_methods_id")
            if methods_id is None:
                missing_methods.append(i + 1)
            elif not (0 <= methods_id < methods_count):
                invalid_methods.append(i + 1)

        errors = []
        if missing_names:
            errors.append(
                f"Run(s) {', '.join(map(str, missing_names))} missing a run name."
            )
        if missing_methods:
            errors.append(
                f"Run(s) {', '.join(map(str, missing_methods))} missing a methods ID."
            )
        if invalid_methods:
            errors.append(
                f"Run(s) {', '.join(map(str, invalid_methods))} have an invalid methods ID."
            )
        return len(errors) == 0, errors

    @staticmethod
    def validate_methods(bioinfo_method_infos):
        methods_validation = {}
        all_methods_valid = True
        method_count = 0
        if "methods" in bioinfo_method_infos:
            for method_data in bioinfo_method_infos["methods"]:
                valid, missing = ValidationHelper.check_method_required_fields(
                    method_data
                )
                methods_validation[method_count] = (valid, missing)
                method_count += 1
                if not valid:
                    all_methods_valid = False
        if method_count == 0:
            all_methods_valid = False
            methods_validation["_no_methods"] = (
                False,
                ["At least one method is required"],
            )
        return methods_validation, all_methods_valid


class BioinformaticsRunManager:
    """Manages bioinformatics run information."""

    def __init__(
        self,
        required_fields,
        required_alternate_fields,
        optional_fields,
        optional_alternate_fields,
    ):
        self.required_fields = required_fields
        self.required_alternate_fields = required_alternate_fields
        self.optional_fields = optional_fields
        self.optional_alternate_fields = optional_alternate_fields
        self._initialize_session_state()

    def _initialize_session_state(self):
        if "bioinfo_methods_list" not in st.session_state:
            st.session_state["bioinfo_methods_list"] = []

    def _create_method_dropdown_options(self):
        options = []
        for idx, method in enumerate(st.session_state["bioinfo_methods_list"]):
            name = method.get("bioinformatics_method_name", f"unnamed method {idx+1}")
            options.append(f"{idx}: {name}")
        return options

    def _get_method_selection(self, i=None):
        if not st.session_state["bioinfo_methods_list"]:
            st.warning(
                "No bioinformatics methods available. Please add a method below."
            )
            return 0
        options = self._create_method_dropdown_options()
        key = (
            f"method_select_{i}_{len(options)}"
            if i is not None
            else f"method_select_{len(options)}"
        )
        selected = st.selectbox("Bioinformatics Methods ID:", options=options, key=key)
        return int(selected.split(":")[0])

    def _get_unique_bioinfo_run_names(self):
        unique_names = []
        if "microhaplotype_info" in st.session_state:
            try:
                mhap = st.session_state["microhaplotype_info"]
                if isinstance(mhap, dict) and "detected_microhaplotypes" in mhap:
                    detected = mhap["detected_microhaplotypes"]
                    if isinstance(detected, list):
                        names = [
                            item.get("bioinformatics_run_name")
                            for item in detected
                            if isinstance(item, dict)
                            and item.get("bioinformatics_run_name")
                        ]
                        unique_names = sorted(set(names))
            except Exception:
                pass
        return unique_names

    def _enter_run_values(self, i=None, prefill_name=None):
        cols = st.columns(3)
        with cols[0]:
            bioinfo_run_name = st.text_input(
                "Bioinformatics Run Name:",
                value=prefill_name or "",
                help="Name of the bioinformatics run (required).",
                key=f"run_name_{i}" if i is not None else "run_name",
            )
        with cols[1]:
            bioinfo_methods_id = self._get_method_selection(i)
        with cols[2]:
            bioinfo_run_date = st.date_input(
                "Bioinformatics Run Date (Optional):",
                value=None,
                key=f"run_date_{i}" if i is not None else "run_date",
            )
        run_dict = {
            "bioinformatics_run_name": bioinfo_run_name,
            "bioinformatics_methods_id": bioinfo_methods_id,
        }
        if bioinfo_run_date:
            run_dict["run_date"] = str(bioinfo_run_date)
        return run_dict

    def _save_runs(self, bioinfo_run_vals):
        if st.button("Save Bioinformatics Run Info", key="save_bioinfo_run_vals"):
            methods_list = st.session_state.get("bioinfo_methods_list", [])
            is_valid, errors = ValidationHelper.validate_runs(
                bioinfo_run_vals, methods_list
            )
            if not is_valid:
                for error in errors:
                    st.error(error)
            else:
                st.session_state["bioinfo_run_infos"] = bioinfo_run_vals
                st.success("Bioinformatics run values saved successfully!")

    def _save_upload_runs(
        self, df, mapped_fields, selected_optional_fields, selected_additional_fields
    ):
        """Save uploaded run info rows, associating each with a chosen method."""
        if df is None or mapped_fields is None:
            return

        methods_list = st.session_state.get("bioinfo_methods_list", [])
        if not methods_list:
            st.error("No bioinformatics methods available. Please add a method first.")
            return

        method_options = self._create_method_dropdown_options()

        # Determine the run name column for display
        run_name_col = mapped_fields.get("bioinformatics_run_name")

        # Assignment mode
        assignment_mode = st.radio(
            "Method assignment mode:",
            ["Assign one method to all runs", "Assign method per run"],
            horizontal=True,
            key="run_method_assignment_mode",
        )

        if assignment_mode == "Assign one method to all runs":
            methods_id = self._get_method_selection(i="upload")
            per_run_method_ids = None
        else:
            # Build a per-row assignment table
            st.write("**Assign a method to each run:**")
            per_run_method_ids = []
            for i, (_, row) in enumerate(df.iterrows()):
                run_label = (
                    str(row[run_name_col])
                    if run_name_col and run_name_col in df.columns
                    else f"Row {i + 1}"
                )
                col_label, col_select = st.columns([2, 3])
                with col_label:
                    st.markdown(f"**{run_label}**")
                with col_select:
                    selected = st.selectbox(
                        "Method:",
                        options=method_options,
                        key=f"per_run_method_{i}",
                        label_visibility="collapsed",
                    )
                    per_run_method_ids.append(int(selected.split(":")[0]))
            methods_id = None

        if st.button(
            "Save Bioinformatics Run Info", key="save_bioinfo_run_vals_upload"
        ):
            try:
                new_runs = []
                for i, (_, row) in enumerate(df.iterrows()):
                    entry = {}
                    for pmo_field, input_field in mapped_fields.items():
                        if input_field and input_field in df.columns:
                            val = row[input_field]
                            entry[pmo_field] = str(val) if pd.notna(val) else None
                    if selected_optional_fields:
                        for pmo_field, input_field in selected_optional_fields.items():
                            if input_field and input_field in df.columns:
                                val = row[input_field]
                                entry[pmo_field] = str(val) if pd.notna(val) else None
                    if selected_additional_fields:
                        for field in selected_additional_fields:
                            if field in df.columns:
                                val = row[field]
                                entry[field] = str(val) if pd.notna(val) else None
                    entry = {
                        k: v for k, v in entry.items() if v is not None and v != ""
                    }
                    entry["bioinformatics_methods_id"] = (
                        per_run_method_ids[i]
                        if per_run_method_ids is not None
                        else methods_id
                    )
                    new_runs.append(entry)

                existing = st.session_state.get("bioinfo_run_infos", [])
                st.session_state["bioinfo_run_infos"] = existing + new_runs
                st.success(f"Added {len(new_runs)} run(s) successfully!")
                st.info(
                    f"Total sequencing runs: {len(st.session_state['bioinfo_run_infos'])}"
                )
            except Exception as e:
                st.error(f"Error saving run information: {e}")

    def add_runs(self):
        st.subheader("Add Bioinformatics Run Information")
        run_input_mode = st.radio(
            "Run information input method:",
            ["Enter Manually", "Upload File"],
            horizontal=True,
            key="run_input_mode",
        )

        if run_input_mode == "Enter Manually":
            unique_run_names = self._get_unique_bioinfo_run_names()
            default_num = len(unique_run_names) if unique_run_names else 1
            if unique_run_names:
                st.info(
                    f"Found {len(unique_run_names)} unique run name(s) in microhaplotype data — pre-filled below."
                )
            number_inputs = st.number_input(
                "Number of bioinformatics runs",
                min_value=0,
                value=default_num,
                key="num_bioinfo_runs",
            )
            bioinfo_run_vals = [
                self._enter_run_values(
                    i=i,
                    prefill_name=unique_run_names[i]
                    if i < len(unique_run_names)
                    else None,
                )
                for i in range(number_inputs)
            ]
            self._save_runs(bioinfo_run_vals)

        else:  # Upload File
            (
                df,
                mapped_fields,
                selected_optional_fields,
                selected_additional_fields,
            ) = load_data(
                self.required_fields,
                self.required_alternate_fields,
                self.optional_fields,
                self.optional_alternate_fields,
                key_suffix="bioinfo_run",
            )
            self._save_upload_runs(
                df, mapped_fields, selected_optional_fields, selected_additional_fields
            )

    def preview_runs(self):
        if "bioinfo_run_infos" in st.session_state:
            preview_toggle = st.toggle(
                "Preview Bioinformatics Run Information",
                key="preview_bioinfo_runs_toggle",
            )
            if preview_toggle:
                st.json(st.session_state["bioinfo_run_infos"])


class BioinformaticsMethodManager:
    """Manages bioinformatics method information."""

    def __init__(
        self,
        required_fields,
        required_alternate_fields,
        optional_fields,
        optional_alternate_fields,
    ):
        self.required_fields = required_fields
        self.required_alternate_fields = required_alternate_fields
        self.optional_fields = optional_fields
        self.optional_alternate_fields = optional_alternate_fields
        self.bioinfo_method_infos = {}

    def _show_methods_count(self):
        if st.session_state.get("bioinfo_methods_list"):
            st.info(f"Current methods: {len(st.session_state['bioinfo_methods_list'])}")

    def _get_method_name_input(self):
        st.subheader("Pipeline (Optional)")
        st.write(
            "Putting in the pipeline information is optional. If you add information you must add both program and program version."
        )
        pipeline_dict = self._create_method_step_input_fields(0)
        return pipeline_dict["program"], pipeline_dict

    def _create_method_step_input_fields(self, method):
        cols1 = st.columns(2)
        with cols1[0]:
            program = st.text_input(
                "program",
                key=f"{method}_program",
                help="Name of the software tool (e.g. 'DADA2')",
            )
        with cols1[1]:
            version = st.text_input(
                "program version",
                key=f"{method}_version",
                help="Version number (e.g. '1.16.0')",
            )
        cols2 = st.columns(2)
        with cols2[0]:
            description = st.text_input(
                "program description (optional)", key=f"{method}_description"
            )
        with cols2[1]:
            additional_argument = st.text_input(
                "additional arguments (optional)", key=f"{method}_additional_argument"
            )
        program_url = st.text_input(
            "program url (optional)", key=f"{method}_program_url"
        )
        return {
            "program": program,
            "program_version": version,
            "program_description": description,
            "additional_argument": additional_argument,
            "program_url": program_url,
        }

    def _build_method_step_dict(self, inputs):
        step_dict = {
            "program": inputs["program"],
            "program_version": inputs["program_version"],
        }
        for field in ["additional_argument", "program_description", "program_url"]:
            if inputs.get(field, "").strip():
                step_dict[field] = inputs[field]
        return step_dict

    def _add_additional_fields(self, method, method_dict):
        if st.toggle(f"Add additional fields to {method}", key=f"{method}_toggle"):
            number_inputs = st.number_input(
                "Number of additional inputs",
                min_value=0,
                value=1,
                key=f"{method}_num_fields",
            )
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
            for name, value in zip(field_names, field_values):
                if name and name.strip():
                    method_dict[name] = value
        return method_dict

    def _enter_method_step_info(self, method):
        inputs = self._create_method_step_input_fields(method)
        method_dict = self._build_method_step_dict(inputs)
        return self._add_additional_fields(method, method_dict)

    def _create_methods_steps(self):
        st.subheader("Bioinformatics Method Steps")
        number_of_steps = st.number_input(
            "Number of bioinformatics steps:",
            min_value=1,
            value=1,
            key="num_bioinformatics_methods",
        )
        return [
            self._enter_method_step_info(f"method_{i}") for i in range(number_of_steps)
        ]

    def _build_methods_from_upload(
        self,
        df,
        mapped_fields,
        selected_optional_fields,
        selected_additional_fields,
        grouping_col,
    ):
        """
        Build a list of method dicts from an uploaded file.
        If grouping_col is set, each unique value becomes a separate method entry
        (bioinformatics_method_name = group value, methods = rows in that group).
        Otherwise all rows go into one method entry.
        """

        def _row_to_step(row):
            step = {}
            for pmo_field, input_field in mapped_fields.items():
                if input_field and input_field in df.columns:
                    val = row[input_field]
                    step[pmo_field] = str(val) if pd.notna(val) else None
            if selected_optional_fields:
                for pmo_field, input_field in selected_optional_fields.items():
                    if input_field and input_field in df.columns:
                        val = row[input_field]
                        if pd.notna(val):
                            parsed = parse_list_field(str(val))
                            # Apply list parsing only to additional_argument field
                            step[pmo_field] = (
                                parsed
                                if pmo_field == "additional_argument"
                                else str(val)
                            )
                        else:
                            step[pmo_field] = None
            if selected_additional_fields:
                for field in selected_additional_fields:
                    if field in df.columns and field != grouping_col:
                        val = row[field]
                        step[field] = str(val) if pd.notna(val) else None
            return {k: v for k, v in step.items() if v is not None and v != ""}

        if grouping_col and grouping_col in df.columns:
            method_list = []
            for group_val, group_df in df.groupby(grouping_col, sort=False):
                steps = [_row_to_step(row) for _, row in group_df.iterrows()]
                method_entry = {
                    "bioinformatics_method_name": str(group_val),
                    "methods": steps,
                }
                method_list.append(method_entry)
            return method_list
        else:
            steps = [_row_to_step(row) for _, row in df.iterrows()]
            return [{"methods": steps}]

    def add_methods_information(self):
        st.subheader("Add Bioinformatics Method Information", divider="gray")
        self._show_methods_count()

        method_input_mode = st.radio(
            "Method information input method:",
            ["Enter Manually", "Upload File"],
            horizontal=True,
            key="method_input_mode",
        )

        if method_input_mode == "Enter Manually":
            add_method_toggle = st.checkbox(
                "Add New Bioinformatics Method",
                key="add_new_bioinfo_method_checkbox",
            )
            if add_method_toggle:
                method_name, _ = self._get_method_name_input()
                method_steps = self._create_methods_steps()
                self.bioinfo_method_infos = {"methods": method_steps}
                if method_name and method_name.strip():
                    self.bioinfo_method_infos[
                        "bioinformatics_method_name"
                    ] = method_name
            else:
                self.bioinfo_method_infos = {}

        else:  # Upload File
            (
                df,
                mapped_fields,
                selected_optional_fields,
                selected_additional_fields,
            ) = load_data(
                self.required_fields,
                self.required_alternate_fields,
                self.optional_fields,
                self.optional_alternate_fields,
                key_suffix="bioinfo_methods",
            )
            self.bioinfo_method_infos = {}
            self._upload_df = df
            self._upload_mapped = mapped_fields
            self._upload_optional = selected_optional_fields
            self._upload_additional = selected_additional_fields

            if df is not None:
                # Grouping column selector — shown after file is loaded
                st.write("**Optional: select a grouping column**")
                st.write(
                    "If selected, each unique value in this column becomes a separate method entry "
                    "and its value is used as the `bioinformatics_method_name`."
                )
                grouping_options = ["None"] + df.columns.tolist()
                grouping_col = st.selectbox(
                    "Grouping column:",
                    grouping_options,
                    key="methods_grouping_col",
                )
                self._grouping_col = None if grouping_col == "None" else grouping_col
            else:
                self._grouping_col = None

    def save_method(self):
        """Save method — handles both manual and upload paths."""
        # Detect which mode we're in by checking for upload state
        if hasattr(self, "_upload_df") and self._upload_df is not None:
            # Upload path
            if st.button(
                "Save Bioinformatics Method(s)", key="save_bioinfo_method_infos"
            ):
                try:
                    method_list = self._build_methods_from_upload(
                        self._upload_df,
                        self._upload_mapped,
                        self._upload_optional,
                        self._upload_additional,
                        self._grouping_col,
                    )
                    # Validate each method entry
                    all_valid = True
                    for entry in method_list:
                        for step in entry.get("methods", []):
                            (
                                valid,
                                missing,
                            ) = ValidationHelper.check_method_required_fields(step)
                            if not valid:
                                st.error(
                                    f"Step missing required fields {missing} in method '{entry.get('bioinformatics_method_name', 'unnamed')}'"
                                )
                                all_valid = False

                    if all_valid:
                        existing = st.session_state.get("bioinfo_methods_list", [])
                        st.session_state["bioinfo_methods_list"] = (
                            existing + method_list
                        )
                        st.success(
                            f"Added {len(method_list)} method group(s) successfully!"
                        )
                        st.info(
                            f"Total available methods: {len(st.session_state['bioinfo_methods_list'])}"
                        )
                        st.rerun()
                except Exception as e:
                    st.error(f"Error saving methods: {e}")

        elif self.bioinfo_method_infos:
            # Manual path
            if st.button("Save Bioinformatics Method", key="save_bioinfo_method_infos"):
                methods_validation, all_valid = ValidationHelper.validate_methods(
                    self.bioinfo_method_infos
                )
                if all_valid:
                    st.session_state["bioinfo_methods_list"].append(
                        self.bioinfo_method_infos
                    )
                    st.success("Bioinformatics method added successfully!")
                    st.info(
                        f"Total available methods: {len(st.session_state['bioinfo_methods_list'])}"
                    )
                    st.rerun()
                else:
                    for method_id, (valid, missing) in methods_validation.items():
                        if not valid:
                            if method_id == "_no_methods":
                                st.error(
                                    "At least one bioinformatics method is required."
                                )
                            else:
                                st.error(
                                    f"Step '{method_id+1}' missing required fields: {', '.join(missing)}"
                                )
                    st.warning("Please fill in all required fields before saving.")

    def _create_remove_options(self):
        return [
            f"{idx}: {m.get('bioinformatics_method_name', f'unnamed method {idx+1}')}"
            for idx, m in enumerate(st.session_state["bioinfo_methods_list"])
        ]

    def _update_run_info_indices(self, removed_indices):
        if "bioinfo_run_infos" not in st.session_state:
            return
        updated, affected = [], []
        for i, run in enumerate(st.session_state["bioinfo_run_infos"]):
            current_id = run.get("bioinformatics_methods_id", 0)
            if current_id in removed_indices:
                affected.append(run.get("bioinformatics_run_name", f"Run {i+1}"))
            adjustment = sum(1 for r in removed_indices if r < current_id)
            new_id = max(0, current_id - adjustment)
            updated_run = run.copy()
            updated_run["bioinformatics_methods_id"] = new_id
            updated.append(updated_run)
        st.session_state["bioinfo_run_infos"] = updated
        if affected:
            st.warning(f"Updated method references for runs: {', '.join(affected)}")

    def remove_methods_section(self):
        if not st.session_state.get("bioinfo_methods_list"):
            return
        st.subheader("Remove Methods")
        if st.checkbox(
            "Remove Existing Methods", key="remove_existing_methods_checkbox"
        ):
            options = self._create_remove_options()
            selected = st.multiselect(
                "Select methods to remove:",
                options=options,
                key="select_methods_to_remove_multiselect",
            )
            if selected and st.button(
                "Remove Selected Methods",
                type="secondary",
                key="remove_selected_methods_button",
            ):
                indices = sorted([int(o.split(":")[0]) for o in selected], reverse=True)
                original = sorted(indices)
                for idx in indices:
                    if 0 <= idx < len(st.session_state["bioinfo_methods_list"]):
                        removed = st.session_state["bioinfo_methods_list"].pop(idx)
                        st.success(
                            f"Removed: {removed.get('bioinformatics_method_name', f'Method {idx}')}"
                        )
                self._update_run_info_indices(original)
                st.info(
                    f"Remaining methods: {len(st.session_state['bioinfo_methods_list'])}"
                )
                st.rerun()

    def preview_methods(self):
        if st.session_state.get("bioinfo_methods_list"):
            if st.toggle(
                "Preview Bioinformatics Methods List",
                key="preview_bioinfo_methods_toggle",
            ):
                for idx, method in enumerate(st.session_state["bioinfo_methods_list"]):
                    st.write(f"**Method Set {idx}:**")
                    st.json(method)
                    st.write("---")


class BioInfoPage:
    def __init__(
        self,
        run_required,
        run_required_alt,
        run_optional,
        run_optional_alt,
        methods_required,
        methods_required_alt,
        methods_optional,
        methods_optional_alt,
    ):
        self.run_manager = BioinformaticsRunManager(
            run_required, run_required_alt, run_optional, run_optional_alt
        )
        self.method_manager = BioinformaticsMethodManager(
            methods_required,
            methods_required_alt,
            methods_optional,
            methods_optional_alt,
        )

    def display_info(self):
        if st.session_state.get("bioinfo_methods_list") or st.session_state.get(
            "bioinfo_run_infos"
        ):
            st.subheader("Preview Bioinformatics Information", divider="gray")
            self.run_manager.preview_runs()
            self.method_manager.preview_methods()

    def run(self):
        self.run_manager.add_runs()
        self.method_manager.add_methods_information()
        self.method_manager.save_method()
        self.method_manager.remove_methods_section()
        self.display_info()


# Initialize and run the app
if __name__ == "__main__":
    render_header()
    st.subheader("Bioinformatics Run Information", divider="gray")
    schema_fields = load_schema()

    run_required = schema_fields["bioinformatics_run_info"]["required"]
    run_required_alt = schema_fields["bioinformatics_run_info"]["required_alternatives"]
    run_optional = schema_fields["bioinformatics_run_info"]["optional"]
    run_optional_alt = schema_fields["bioinformatics_run_info"]["optional_alternatives"]

    methods_required = schema_fields["bioinformatics_methods_info"]["required"]
    methods_required_alt = schema_fields["bioinformatics_methods_info"][
        "required_alternatives"
    ]
    methods_optional = schema_fields["bioinformatics_methods_info"]["optional"]
    methods_optional_alt = schema_fields["bioinformatics_methods_info"][
        "optional_alternatives"
    ]

    app = BioInfoPage(
        run_required,
        run_required_alt,
        run_optional,
        run_optional_alt,
        methods_required,
        methods_required_alt,
        methods_optional,
        methods_optional_alt,
    )
    app.run()
