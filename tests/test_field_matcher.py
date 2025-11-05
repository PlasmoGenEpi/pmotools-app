import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from field_matcher import (
    fuzzy_match_fields,
    no_duplicates,
    interactive_field_mapping,
    field_mapping_json_to_table,
    additional_fields_section,
    field_mapping,
)


class TestFuzzyMatchFields:
    """Test cases for fuzzy_match_fields function."""

    def test_basic_matching(self):
        """Test basic field matching without alternates."""
        field_names = ["sample_id", "patient_name", "date_collected"]
        target_schema = ["sampleID", "patientName", "collectionDate"]

        matches, unused = fuzzy_match_fields(field_names, target_schema)

        # Should match all fields
        assert len(matches) == 3
        assert len(unused) == 0
        assert "sampleID" in matches
        assert "patientName" in matches
        assert "collectionDate" in matches

    def test_matching_swaps_with_alternates(self):
        """Test field matching with alternate schema names."""
        field_names = ["sample_id", "patient_name"]
        target_schema = ["sampleID", "patientName"]
        alternate_schema_names = {
            "sampleID": ["patient_name", "id"],
            "patientName": ["sample_id", "name"],
        }

        matches, unused = fuzzy_match_fields(
            field_names, target_schema, alternate_schema_names
        )

        assert len(matches) == 2
        assert matches["sampleID"] == "patient_name"
        assert matches["patientName"] == "sample_id"

    def test_required_fields_insufficient_input(self):
        """Test error when not enough input fields for required targets."""
        field_names = ["sample_id"]
        target_schema = ["sampleID", "patientName", "collectionDate"]

        with patch("streamlit.error") as mock_error:
            matches, unused = fuzzy_match_fields(
                field_names, target_schema, is_required=True
            )

            # Verify that st.error was called with the correct message
            mock_error.assert_called_once()
            error_call = mock_error.call_args[0][0]  # Get the error message
            assert "Not enough unique input fields" in error_call
            assert "Have 1 unique field(s) for 3 target(s)" in error_call

    def test_optional_fields_with_threshold(self):
        """Test optional field matching with threshold."""
        field_names = ["sample_id", "patient_name", "unrelated_field"]
        target_schema = ["sampleID", "patientName"]

        # Test with high threshold (should not match poor matches)
        matches, unused = fuzzy_match_fields(
            field_names, target_schema, is_required=False, match_threshold=90
        )

        # Should have some matches but not all
        assert len(matches) == 2
        assert len(unused) >= 1

    def test_one_to_one_mapping(self):
        """Test that each field is only used once."""
        field_names = ["field1", "field2", "field3"]
        target_schema = ["target1", "target2"]

        matches, unused = fuzzy_match_fields(field_names, target_schema)

        # Should use exactly 2 fields, leave 1 unused
        used_fields = [v for v in matches.values() if v is not None]
        assert len(used_fields) == 2
        assert len(unused) == 1
        assert len(set(used_fields)) == len(used_fields)  # No duplicates

    def test_empty_inputs(self):
        """Test with empty inputs."""
        matches, unused = fuzzy_match_fields([], [])
        assert matches == {}
        assert unused == []

        matches, unused = fuzzy_match_fields(["field1"], [])
        assert matches == {}
        assert unused == ["field1"]


class TestNoDuplicates:
    """Test cases for no_duplicates function."""

    def test_no_duplicates_valid(self):
        """Test with no duplicate values."""
        field_mapping = {"target1": "field1", "target2": "field2", "target3": None}

        with patch("streamlit.error") as mock_error:
            result = no_duplicates(field_mapping)
            assert result is True
            mock_error.assert_not_called()

    def test_duplicates_detected(self):
        """Test detection of duplicate values."""
        field_mapping = {
            "target1": "field1",
            "target2": "field1",  # Duplicate
            "target3": None,
        }

        with patch("streamlit.error") as mock_error:
            result = no_duplicates(field_mapping)
            assert result is False
            mock_error.assert_called_once()

    def test_none_values_ignored(self):
        """Test that None values are not considered duplicates."""
        field_mapping = {"target1": None, "target2": None, "target3": "field1"}

        with patch("streamlit.error") as mock_error:
            result = no_duplicates(field_mapping)
            assert result is True
            mock_error.assert_not_called()


class TestInteractiveFieldMapping:
    """Test cases for interactive_field_mapping function."""

    def test_required_fields_mapping(self):
        """Test mapping for required fields."""
        field_mapping = {"target1": "field1", "target2": "field2"}
        df_columns = ["field1", "field2", "field3"]

        # Mock streamlit selectbox to return the suggested match
        with patch("streamlit.selectbox") as mock_selectbox:
            mock_selectbox.side_effect = ["field1", "field2"]

            result = interactive_field_mapping(
                field_mapping, df_columns, is_required=True
            )

            assert result == {"target1": "field1", "target2": "field2"}
            assert mock_selectbox.call_count == 2

    def test_optional_fields_mapping(self):
        """Test mapping for optional fields with 'no match' option."""
        field_mapping = {"target1": "field1", "target2": None}
        df_columns = ["field1", "field2", "field3"]

        with patch("streamlit.selectbox") as mock_selectbox:
            mock_selectbox.side_effect = ["field1", "no match"]

            result = interactive_field_mapping(
                field_mapping, df_columns, is_required=False
            )

            assert result == {"target1": "field1", "target2": None}

    def test_list_suggested_match(self):
        """Test handling of list suggested matches."""
        field_mapping = {"target1": ["field1", "field2"]}
        df_columns = ["field1", "field2", "field3"]

        with patch("streamlit.selectbox") as mock_selectbox:
            mock_selectbox.return_value = "field1"

            result = interactive_field_mapping(field_mapping, df_columns)

            assert result == {"target1": "field1"}


class TestFieldMappingJsonToTable:
    """Test cases for field_mapping_json_to_table function."""

    def test_basic_conversion(self):
        """Test basic conversion to DataFrame."""
        mapping = {"target1": "field1", "target2": "field2", "target3": None}

        result = field_mapping_json_to_table(mapping)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ["PMO Field", "Input Field"]
        assert result.iloc[0]["PMO Field"] == "target1"
        assert result.iloc[0]["Input Field"] == "field1"
        assert result.iloc[2]["Input Field"] is None


class TestAdditionalFieldsSection:
    """Test cases for additional_fields_section function."""

    def test_no_unused_fields(self):
        """Test with no unused fields."""
        result = additional_fields_section([])
        assert result == []

    def test_with_unused_fields(self):
        """Test with unused fields."""
        unused_fields = ["field1", "field2", "field3"]

        with patch("streamlit.subheader"), patch("streamlit.write"), patch(
            "streamlit.columns"
        ) as mock_columns, patch("streamlit.checkbox") as mock_checkbox, patch(
            "streamlit.success"
        ):
            # Mock columns to return a list of column objects
            mock_col1 = MagicMock()
            mock_col2 = MagicMock()
            mock_columns.return_value = [mock_col1, mock_col2]

            # Mock checkbox to return True for first field, False for others
            mock_checkbox.side_effect = [True, False, False]

            result = additional_fields_section(unused_fields)

            assert result == ["field1"]


class TestFieldMapping:
    """Test cases for field_mapping function."""

    def test_basic_field_mapping(self):
        """Test basic field mapping workflow."""
        input_fields = ["field1", "field2", "field3"]
        target_schema = ["target1", "target2"]
        target_alternate_schema = {"target1": ["field1"]}

        with patch(
            "field_matcher.fuzzy_field_matching_page_section"
        ) as mock_fuzzy, patch(
            "field_matcher.interactive_field_mapping_page_section"
        ) as mock_interactive:
            # Mock fuzzy matching
            mock_fuzzy.return_value = (
                {"target1": "field1", "target2": "field2"},
                ["field3"],
            )

            # Mock interactive mapping (toggle off)
            mock_interactive.return_value = (
                {"target1": "field1", "target2": "field2"},
                input_fields,
            )

            result_mapping, result_unused = field_mapping(
                input_fields, target_schema, target_alternate_schema
            )

            assert result_mapping == {"target1": "field1", "target2": "field2"}
            assert result_unused == ["field3"]  # Should use original unused fields

    def test_interactive_mapping_used(self):
        """Test when interactive mapping is used."""
        input_fields = ["field1", "field2", "field3"]
        target_schema = ["target1", "target2"]

        with patch(
            "field_matcher.fuzzy_field_matching_page_section"
        ) as mock_fuzzy, patch(
            "field_matcher.interactive_field_mapping_page_section"
        ) as mock_interactive:
            # Mock fuzzy matching
            mock_fuzzy.return_value = (
                {"target1": "field1", "target2": "field2"},
                ["field3"],
            )

            # Mock interactive mapping (toggle on) - returns different unused fields
            mock_interactive.return_value = (
                {"target1": "field1", "target2": "field3"},
                ["field2"],  # Different unused fields
            )

            result_mapping, result_unused = field_mapping(
                input_fields, target_schema, {}
            )

            assert result_mapping == {"target1": "field1", "target2": "field3"}
            assert result_unused == ["field2"]  # Should use updated unused fields


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_fuzzy_match_fields_empty_schema(self):
        """Test fuzzy matching with empty target schema."""
        field_names = ["field1", "field2"]
        target_schema = []

        matches, unused = fuzzy_match_fields(field_names, target_schema)

        assert matches == {}
        assert set(unused) == set(field_names)  # Order-independent comparison

    def test_fuzzy_match_fields_no_matches(self):
        """Test fuzzy matching when no good matches exist."""
        field_names = ["completely_different_field"]
        target_schema = ["target1"]

        matches, unused = fuzzy_match_fields(
            field_names, target_schema, is_required=False
        )

        assert matches["target1"] is None
        assert unused == field_names

    def test_alternate_schema_names_empty(self):
        """Test with empty alternate schema names."""
        field_names = ["field1"]
        target_schema = ["target1"]
        alternate_schema_names = {}

        matches, unused = fuzzy_match_fields(
            field_names, target_schema, alternate_schema_names
        )

        assert len(matches) == 1
        assert "target1" in matches


class TestIntegration:
    """Integration tests for the field matching workflow."""

    def test_complete_workflow(self):
        """Test a complete field matching workflow."""
        # Setup test data
        field_names = ["sample_id", "patient_name", "collection_date", "extra_field"]
        required_schema = ["sampleID", "patientName"]
        optional_schema = ["collectionDate"]
        alternate_schema = {"sampleID": ["sample_id"]}

        # Test required field matching
        required_matches, required_unused = fuzzy_match_fields(
            field_names, required_schema, alternate_schema, is_required=True
        )

        assert len(required_matches) == 2
        assert "sampleID" in required_matches
        assert "patientName" in required_matches
        assert len(required_unused) == 2  # collection_date and extra_field

        # Test optional field matching with remaining fields
        optional_matches, optional_unused = fuzzy_match_fields(
            required_unused, optional_schema, {}, is_required=False
        )

        assert len(optional_matches) == 1
        assert "collectionDate" in optional_matches
        assert len(optional_unused) == 1  # extra_field

    def test_threshold_behavior(self):
        """Test threshold behavior for optional fields."""
        field_names = ["good_match", "poor_match"]
        target_schema = ["target1", "target2"]

        # Test with low threshold (should match both)
        matches_low, unused_low = fuzzy_match_fields(
            field_names, target_schema, is_required=False, match_threshold=30
        )

        # Test with high threshold (should match fewer)
        matches_high, unused_high = fuzzy_match_fields(
            field_names, target_schema, is_required=False, match_threshold=90
        )

        # High threshold should result in more unused fields
        assert len(unused_high) >= len(unused_low)


if __name__ == "__main__":
    pytest.main([__file__])
