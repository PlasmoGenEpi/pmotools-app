"""
Unit tests for utils.py
"""
import pytest
import pandas as pd
import json
import tempfile
import os
from unittest.mock import patch, mock_open

from utils import save_to_csv, load_schema


class TestSaveToCSV:
    """Test cases for save_to_csv function."""

    def test_save_to_csv_success(self):
        """Test successfully saving a DataFrame to CSV."""
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as tmp_file:
            output_path = tmp_file.name

        try:
            result_path = save_to_csv(df, output_path)

            assert result_path == output_path
            assert os.path.exists(output_path)

            # Verify the file content
            loaded_df = pd.read_csv(output_path)
            assert len(loaded_df) == 3
            assert list(loaded_df.columns) == ["col1", "col2"]
            assert loaded_df.iloc[0]["col1"] == 1
            assert loaded_df.iloc[0]["col2"] == "a"

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_save_to_csv_empty_dataframe(self):
        """Test saving an empty DataFrame to CSV."""
        df = pd.DataFrame({"col1": []})

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as tmp_file:
            output_path = tmp_file.name

        try:
            result_path = save_to_csv(df, output_path)

            assert result_path == output_path
            assert os.path.exists(output_path)

            # Verify the file exists and can be read
            loaded_df = pd.read_csv(output_path)
            assert len(loaded_df) == 0
            assert "col1" in loaded_df.columns

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_save_to_csv_with_index(self):
        """Test that index is not saved (index=False)."""
        df = pd.DataFrame({"col1": [1, 2, 3]}, index=["a", "b", "c"])

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as tmp_file:
            output_path = tmp_file.name

        try:
            save_to_csv(df, output_path)

            # Verify index is not in the CSV
            loaded_df = pd.read_csv(output_path)
            assert "index" not in loaded_df.columns

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)


class TestLoadSchema:
    """Test cases for load_schema function."""

    def test_load_schema_success(self):
        """Test successfully loading a schema file."""
        mock_schema = {
            "specimen_level_metadata": {
                "required": ["specimen_name"],
                "optional": ["host_age"],
            }
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_schema))):
            with patch("utils.open", mock_open(read_data=json.dumps(mock_schema))):
                result = load_schema()

                assert isinstance(result, dict)
                assert "specimen_level_metadata" in result
                assert result["specimen_level_metadata"]["required"] == [
                    "specimen_name"
                ]

    def test_load_schema_file_not_found(self):
        """Test error handling when schema file is not found."""
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError):
                load_schema()

    def test_load_schema_invalid_json(self):
        """Test error handling when schema file contains invalid JSON."""
        with patch("builtins.open", mock_open(read_data="invalid json content")):
            with pytest.raises(json.JSONDecodeError):
                load_schema()

    def test_load_schema_empty_file(self):
        """Test loading an empty schema file."""
        with patch("builtins.open", mock_open(read_data="{}")):
            result = load_schema()
            assert result == {}
