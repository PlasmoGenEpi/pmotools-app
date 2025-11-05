"""
Unit tests for data_loader.py
"""
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from data_loader import load_csv


class TestLoadCSV:
    """Test cases for load_csv function."""

    def test_load_csv_file(self):
        """Test loading a CSV file successfully."""
        # Create a mock file object
        csv_content = "col1,col2\nvalue1,value2\nvalue3,value4"
        mock_file = MagicMock()
        mock_file.name = "test.csv"
        mock_file.read.return_value = csv_content.encode()

        with patch("data_loader.pd.read_csv") as mock_read_csv:
            mock_df = pd.DataFrame(
                {"col1": ["value1", "value3"], "col2": ["value2", "value4"]}
            )
            mock_read_csv.return_value = mock_df

            result = load_csv(mock_file)

            assert isinstance(result, pd.DataFrame)
            mock_read_csv.assert_called_once_with(mock_file, sep="\t")

    def test_load_tsv_file(self):
        """Test loading a TSV file successfully."""
        mock_file = MagicMock()
        mock_file.name = "test.tsv"

        with patch("data_loader.pd.read_csv") as mock_read_csv:
            mock_df = pd.DataFrame({"col1": ["value1"], "col2": ["value2"]})
            mock_read_csv.return_value = mock_df

            result = load_csv(mock_file)

            assert isinstance(result, pd.DataFrame)
            mock_read_csv.assert_called_once_with(mock_file, sep="\t")

    def test_load_txt_file(self):
        """Test loading a TXT file successfully."""
        mock_file = MagicMock()
        mock_file.name = "test.txt"

        with patch("data_loader.pd.read_csv") as mock_read_csv:
            mock_df = pd.DataFrame({"col1": ["value1"], "col2": ["value2"]})
            mock_read_csv.return_value = mock_df

            result = load_csv(mock_file)

            assert isinstance(result, pd.DataFrame)
            mock_read_csv.assert_called_once_with(mock_file, sep="\t")

    def test_load_xlsx_file(self):
        """Test loading an Excel file successfully."""
        mock_file = MagicMock()
        mock_file.name = "test.xlsx"

        with patch("data_loader.pd.read_excel") as mock_read_excel:
            mock_df = pd.DataFrame({"col1": ["value1"], "col2": ["value2"]})
            mock_read_excel.return_value = mock_df

            result = load_csv(mock_file)

            assert isinstance(result, pd.DataFrame)
            mock_read_excel.assert_called_once_with(mock_file)

    def test_load_xls_file(self):
        """Test loading an old Excel file successfully."""
        mock_file = MagicMock()
        mock_file.name = "test.xls"

        with patch("data_loader.pd.read_excel") as mock_read_excel:
            mock_df = pd.DataFrame({"col1": ["value1"], "col2": ["value2"]})
            mock_read_excel.return_value = mock_df

            result = load_csv(mock_file)

            assert isinstance(result, pd.DataFrame)
            mock_read_excel.assert_called_once_with(mock_file)

    def test_unsupported_file_format(self):
        """Test error handling for unsupported file format."""
        mock_file = MagicMock()
        mock_file.name = "test.pdf"

        with pytest.raises(ValueError) as exc_info:
            load_csv(mock_file)

        assert "Unsupported file format" in str(exc_info.value)
        assert "CSV, TSV, or Excel file" in str(exc_info.value)

    def test_csv_read_error(self):
        """Test error handling when CSV reading fails."""
        mock_file = MagicMock()
        mock_file.name = "test.csv"

        with patch("data_loader.pd.read_csv") as mock_read_csv:
            mock_read_csv.side_effect = Exception("File not found")

            with pytest.raises(ValueError) as exc_info:
                load_csv(mock_file)

            assert "Failed to read CSV" in str(exc_info.value)
            assert "File not found" in str(exc_info.value)

    def test_excel_read_error(self):
        """Test error handling when Excel reading fails."""
        mock_file = MagicMock()
        mock_file.name = "test.xlsx"

        with patch("data_loader.pd.read_excel") as mock_read_excel:
            mock_read_excel.side_effect = Exception("Invalid Excel file")

            with pytest.raises(ValueError) as exc_info:
                load_csv(mock_file)

            assert "Failed to read CSV" in str(exc_info.value)
            assert "Invalid Excel file" in str(exc_info.value)
