import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any
from src.format_page import render_header

# Constants
REQUIRED_FIELDS = ["project_name", "project_description"]
SEPARATOR_OPTIONS = {"newline": "\n", ",": ",", "tab": "\t"}
SUPPORTED_FILE_TYPES = ["csv", "txt"]


class ProjectInfoPage:
    """Handles project information collection and management."""

    def __init__(self) -> None:
        """Initialize the project info page."""
        self.project_info: Dict[str, Any] = {}

    def add_required_project_information(self) -> None:
        """Add required project information fields."""
        st.subheader("Add Project Information")

        self.project_info["project_name"] = st.text_input(
            "Project Name:", help="A unique identifier for this project."
        )
        self.project_info["project_description"] = st.text_input(
            "Project Description:", help="A short description of the project."
        )

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
            "Upload a CSV or TXT", type=SUPPORTED_FILE_TYPES
        )
        if not uploaded_file:
            return []

        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                column = st.selectbox("Choose column for contributors", df.columns)
                return df[column].dropna().astype(str).tolist()
            elif uploaded_file.name.endswith(".txt"):
                text = uploaded_file.read().decode("utf-8")
                return [c.strip() for c in text.splitlines() if c.strip()]
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return []

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

    def add_optional_info(self) -> None:
        """Add optional project information fields."""
        st.subheader("Add Optional Fields")

        # BioProject accession
        self._add_optional_field(
            "BioProject_accession",
            "BioProject Accession:",
            "An SRA bioproject accession e.g. PRJNA33823.",
        )

        # Chief scientist
        self._add_optional_field(
            "project_collector_chief_scientist",
            "Project Collector Chief Scientist:",
            "Can be collection of names separated by a semicolon if multiple people involved or can just be the name of the primary person managing the specimen.",
        )

        # Project contributors
        project_contributors = self._get_contributors()
        if project_contributors:
            self.project_info["project_contributors"] = project_contributors

        # Project type
        self._add_optional_field(
            "project_type",
            "Project Type:",
            "The type of project conducted, e.g. TES vs surveillance vs transmission.",
        )

    def add_additional_fields(self) -> None:
        """Add custom additional fields."""
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

        # Save the additional fields
        for i in range(number_inputs):
            if field_names[i] and field_values[i]:
                self.project_info[field_names[i].strip()] = field_values[i].strip()

    def _validate_required_fields(self) -> bool:
        """Validate that all required fields are filled."""
        return all(
            self.project_info.get(field, "").strip() for field in REQUIRED_FIELDS
        )

    def transform_and_save_data(self) -> None:
        """Save project data if validation passes."""
        if not self._validate_required_fields():
            st.warning(
                "Please fill in all required fields (Project Name and Description)."
            )
            return

        st.subheader("Save Data")
        if st.button("Save Data", type="primary"):
            st.session_state["project_info"] = [self.project_info]
            st.success("Project information saved successfully!")

    def display_info(self) -> None:
        """Display saved project information preview."""
        if "project_info" not in st.session_state:
            return

        st.subheader("Preview Project Information")
        preview_toggle = st.toggle("Preview Project Information")
        if preview_toggle:
            st.write("Current Project Information:")
            st.json(st.session_state["project_info"])

    def run(self) -> None:
        """Run the complete project information page."""
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
