import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any
from src.format_page import render_header
from src.data_loader import load_csv
from src.field_matcher import load_data

# Constants
REQUIRED_FIELDS = ["project_name", "project_description"]
SEPARATOR_OPTIONS = {"newline": "\n", ",": ",", "tab": "\t"}
SUPPORTED_FILE_TYPES = ["csv", "tsv", "txt", "xlsx", "xls", "gz", "gzip"]


class ProjectInfoPage:
    """Handles project information collection and management."""

    def __init__(
        self,
        required_fields,
        required_alternate_fields,
        optional_fields,
        optional_alternate_fields,
    ) -> None:
        """Initialize the project info page."""
        self.project_info: Dict[str, Any] = {}
        self.required_fields = required_fields
        self.required_alternate_fields = required_alternate_fields
        self.optional_fields = optional_fields
        self.optional_alternate_fields = optional_alternate_fields

    def _get_contributors_from_text(self) -> List[str]:
        """Get contributors from text input."""
        col1, col2 = st.columns([3, 1])
        with col1:
            contributors = st.text_area(
                "",
                help="List collaborators separated by tab, comma, or newline "
                "(e.g., Alice  Bob Tony)",
            )
        with col2:
            sep = st.selectbox("Separator", SEPARATOR_OPTIONS.keys())

        if contributors:
            return [
                c.strip()
                for c in contributors.split(SEPARATOR_OPTIONS[sep])
                if c.strip()
            ]
        return []

    def _get_contributors_from_file(self) -> List[str]:
        """Get contributors from uploaded file."""
        uploaded_file = st.file_uploader(
            "Upload a CSV, TSV, TXT, or Excel file", type=SUPPORTED_FILE_TYPES
        )
        if not uploaded_file:
            return []

        try:
            uploaded_file.seek(0)
            is_text_file = uploaded_file.name.endswith((".csv", ".tsv", ".txt"))

            if is_text_file:
                uploaded_file.seek(0)
                content = uploaded_file.read().decode("utf-8")
                lines = [line.strip() for line in content.split("\n") if line.strip()]
                multi_value_lines = sum(
                    1 for line in lines if "," in line or "\t" in line
                )
                if lines and multi_value_lines / len(lines) < 0.2:
                    df = pd.DataFrame(lines, columns=["contributor"])
                else:
                    uploaded_file.seek(0)
                    df = load_csv(uploaded_file)

                if len(df.columns) == 1 and not df.empty:
                    column_name = str(df.columns[0]).lower()
                    common_headers = {
                        "name",
                        "names",
                        "contributor",
                        "contributors",
                        "person",
                        "people",
                        "author",
                        "authors",
                        "0",
                        "1",
                    }
                    if column_name not in common_headers and not column_name.isdigit():
                        uploaded_file.seek(0)
                        try:
                            df_no_header = pd.read_csv(
                                uploaded_file, sep=None, engine="python", header=None
                            )
                            if len(df_no_header) > len(df):
                                df = df_no_header
                                df.columns = [
                                    f"Column_{i+1}" for i in range(len(df.columns))
                                ]
                        except Exception:
                            pass
            else:
                df = load_csv(uploaded_file)

            if df.empty:
                st.warning("File appears to be empty or could not be parsed.")
                return []

            if len(df.columns) > 1:
                st.info(
                    f"File contains {len(df.columns)} columns. Please select which column contains the contributor names."
                )
                column = st.selectbox(
                    "Choose column for contributors",
                    df.columns,
                    key="contributor_column",
                )
                contributors = df[column].dropna().astype(str).tolist()
                contributors = [c.strip() for c in contributors if c.strip()]
                if contributors:
                    st.success(
                        f"Found {len(contributors)} contributor(s) in the selected column."
                    )
                    with st.expander("Preview contributors"):
                        st.write(contributors[:10])
                        if len(contributors) > 10:
                            st.write(f"... and {len(contributors) - 10} more")
                return contributors
            elif len(df.columns) == 1:
                contributors = df.iloc[:, 0].dropna().astype(str).tolist()
                contributors = [c.strip() for c in contributors if c.strip()]
                if contributors:
                    st.success(f"Found {len(contributors)} contributor(s) in the file.")
                    with st.expander("Preview contributors"):
                        st.write(contributors[:10])
                        if len(contributors) > 10:
                            st.write(f"... and {len(contributors) - 10} more")
                return contributors
            else:
                st.warning("File appears to be empty or could not be parsed.")
                return []
        except ValueError as e:
            st.error(f"Error reading file: {e}")
            return []
        except Exception as e:
            st.error(f"Unexpected error reading file: {e}")
            return []

    def _get_contributors(self) -> List[str]:
        """Get project contributors from user input or file upload."""
        st.text("Project Contributors:")
        upload_as_file = st.checkbox("Upload as file")
        if upload_as_file:
            return self._get_contributors_from_file()
        else:
            return self._get_contributors_from_text()

    def _add_optional_field(
        self, field_name: str, label: str, help_text: str
    ) -> Optional[str]:
        """Add an optional field and return its value if provided."""
        value = st.text_input(label, help=help_text)
        if value and value.strip():
            self.project_info[field_name] = value.strip()
            return value.strip()
        return None

    def add_manual_project_information(self) -> None:
        """Add project information via manual text inputs (original behaviour)."""
        st.subheader("Add Project Information")
        self.project_info["project_name"] = st.text_input(
            "Project Name:", help="A unique identifier for this project."
        )
        self.project_info["project_description"] = st.text_input(
            "Project Description:", help="A short description of the project."
        )

        st.subheader("Add Optional Fields")
        self._add_optional_field(
            "BioProject_accession",
            "BioProject Accession:",
            "An SRA bioproject accession e.g. PRJNA33823.",
        )
        self._add_optional_field(
            "project_collector_chief_scientist",
            "Project Collector Chief Scientist:",
            "Can be collection of names separated by a semicolon if multiple people involved.",
        )
        project_contributors = self._get_contributors()
        if project_contributors:
            self.project_info["project_contributors"] = project_contributors
        self._add_optional_field(
            "project_type",
            "Project Type:",
            "The type of project conducted, e.g. TES vs surveillance vs transmission.",
        )

    def add_upload_project_information(self):
        """Add project information via file upload and field mapping."""
        st.subheader("Add Project Information")
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
            key_suffix="project_info",
        )
        return df, mapped_fields, selected_optional_fields, selected_additional_fields

    def add_additional_fields(self) -> None:
        """Add custom additional fields (manual mode only)."""
        st.subheader("Add Additional Fields")
        add_fields_toggle = st.checkbox("Add Additional Fields")
        if not add_fields_toggle:
            return

        st.write("Fill in the additional fields below:")
        number_inputs = st.number_input(
            "Number of additional inputs", min_value=0, value=1, max_value=10
        )
        if number_inputs > 0:
            self._render_additional_field_inputs(number_inputs)

    def _render_additional_field_inputs(self, number_inputs: int) -> None:
        """Render input fields for additional custom fields."""
        cols = st.columns(2)
        with cols[0]:
            field_names = [
                st.text_input(f"Field Name {i+1}", key=f"field_name_{i}")
                for i in range(number_inputs)
            ]
        with cols[1]:
            field_values = [
                st.text_input(f"Value {i+1}", key=f"value_{i}")
                for i in range(number_inputs)
            ]
        for i in range(number_inputs):
            if field_names[i] and field_values[i]:
                self.project_info[field_names[i].strip()] = field_values[i].strip()

    def _validate_required_fields(self) -> bool:
        """Validate that all required fields are filled."""
        return all(
            self.project_info.get(field, "").strip() for field in REQUIRED_FIELDS
        )

    def transform_and_save_manual(self) -> None:
        """Save manually entered project data if validation passes."""
        st.subheader("Save Data")
        if st.button("Save Data", type="primary"):
            if not self._validate_required_fields():
                st.error(
                    "Please fill in all required fields (Project Name and Description)."
                )
                return
            st.session_state["project_info"] = [self.project_info]
            st.success("Project information saved successfully!")

    def transform_and_save_upload(
        self, df, mapped_fields, selected_optional_fields, selected_additional_fields
    ) -> None:
        """Save uploaded project data after field mapping."""
        st.subheader("Save Data")
        if st.button("Save Data", type="primary"):
            if df is None or mapped_fields is None:
                st.error(
                    "Please upload a file and complete field mapping before saving."
                )
                return
            try:
                project_info_list = []
                for _, row in df.iterrows():
                    entry = {}
                    for pmo_field, input_field in mapped_fields.items():
                        if input_field and input_field in df.columns:
                            entry[pmo_field] = row[input_field]
                    if selected_optional_fields:
                        for pmo_field, input_field in selected_optional_fields.items():
                            if input_field and input_field in df.columns:
                                entry[pmo_field] = row[input_field]
                    if selected_additional_fields:
                        for field in selected_additional_fields:
                            if field in df.columns:
                                entry[field] = row[field]
                    project_info_list.append(entry)
                st.session_state["project_info"] = project_info_list
                st.success(
                    f"Project information saved successfully! Loaded {len(project_info_list)} project(s)."
                )
            except Exception as e:
                st.error(f"Error saving project information: {e}")

    def display_info(self, key_suffix="") -> None:
        """Display saved project information preview."""
        if "project_info" not in st.session_state:
            return
        st.subheader("Preview Project Information")
        toggle_key = (
            f"preview_project_info_{key_suffix}"
            if key_suffix
            else "preview_project_info"
        )
        preview_toggle = st.toggle("Preview Project Information", key=toggle_key)
        if preview_toggle:
            st.write("Current Project Information:")
            st.json(st.session_state["project_info"])

    def run(self) -> None:
        """Run the complete project information page."""
        project_input_mode = st.radio(
            "Project information input method:",
            ["Enter Manually", "Upload File"],
            horizontal=True,
        )

        if project_input_mode == "Enter Manually":
            self.add_manual_project_information()
            self.add_additional_fields()
            self.transform_and_save_manual()
        else:
            (
                df,
                mapped_fields,
                selected_optional_fields,
                selected_additional_fields,
            ) = self.add_upload_project_information()
            self.transform_and_save_upload(
                df, mapped_fields, selected_optional_fields, selected_additional_fields
            )

        self.display_info()


# Initialize and run the page
if __name__ in ("__main__", "__page__"):
    render_header()
    st.subheader("Project Information", divider="gray")
    from src.utils import load_schema

    schema_fields = load_schema()
    required_fields = schema_fields["project_name"]["required"]
    required_alternate_fields = schema_fields["project_name"]["required_alternatives"]
    optional_fields = schema_fields["project_name"]["optional"]
    optional_alternate_fields = schema_fields["project_name"]["optional_alternatives"]

    app = ProjectInfoPage(
        required_fields,
        required_alternate_fields,
        optional_fields,
        optional_alternate_fields,
    )
    if "project_info" in st.session_state:
        st.success(
            "Your project information has already been saved during a previous run of this page"
        )
        if st.button("Clear Previous Info", type="secondary"):
            del st.session_state["project_info"]
            st.rerun()
        app.display_info(key_suffix="prev")
    app.run()
