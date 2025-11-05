"""
Unit tests for transformer.py
"""
import pandas as pd
from unittest.mock import patch

from transformer import (
    transform_mhap_info,
    transform_panel_info,
    transform_specimen_info,
    transform_library_sample_info,
)


class TestTransformMhapInfo:
    """Test cases for transform_mhap_info function."""

    def test_transform_mhap_info_basic(self):
        """Test basic transformation of mhap info."""
        df = pd.DataFrame(
            {
                "sample_id": ["S1", "S2"],
                "target": ["T1", "T2"],
                "sequence": ["ATCG", "GCTA"],
                "reads": [100, 200],
            }
        )
        field_mapping = {
            "library_sample_name": "sample_id",
            "target_name": "target",
            "seq": "sequence",
            "reads": "reads",
        }
        optional_mapping = {}

        with patch("transformer.mhap_table_to_pmo") as mock_transform:
            mock_result = pd.DataFrame({"transformed": ["data"]})
            mock_transform.return_value = mock_result

            result = transform_mhap_info(
                df, "bioinfo_1", field_mapping, optional_mapping
            )

            assert result is not None
            mock_transform.assert_called_once()
            call_args = mock_transform.call_args
            assert call_args[0][0].equals(df)
            assert call_args[1]["library_sample_name_col"] == "sample_id"
            assert call_args[1]["target_name_col"] == "target"
            assert call_args[1]["seq_col"] == "sequence"
            assert call_args[1]["reads_col"] == "reads"

    def test_transform_mhap_info_with_optional_fields(self):
        """Test transformation with optional fields."""
        df = pd.DataFrame(
            {"sample_id": ["S1"], "target": ["T1"], "seq": ["ATCG"], "reads": [100]}
        )
        field_mapping = {
            "library_sample_name": "sample_id",
            "target_name": "target",
            "seq": "seq",
            "reads": "reads",
        }
        optional_mapping = {
            "umis": "umis_col",
            "chrom": "chrom_col",
            "start": "start_col",
        }

        with patch("transformer.mhap_table_to_pmo") as mock_transform:
            mock_result = pd.DataFrame({"transformed": ["data"]})
            mock_transform.return_value = mock_result

            transform_mhap_info(df, "bioinfo_1", field_mapping, optional_mapping)

            mock_transform.assert_called_once()
            call_args = mock_transform.call_args[1]
            assert call_args["umis_col"] == "umis_col"
            assert call_args["chrom_col"] == "chrom_col"
            assert call_args["start_col"] == "start_col"

    def test_transform_mhap_info_with_none_optional_fields(self):
        """Test transformation with None optional fields."""
        df = pd.DataFrame(
            {"sample_id": ["S1"], "target": ["T1"], "seq": ["ATCG"], "reads": [100]}
        )
        field_mapping = {
            "library_sample_name": "sample_id",
            "target_name": "target",
            "seq": "seq",
            "reads": "reads",
        }
        optional_mapping = {
            "umis": None,
            "chrom": None,
        }

        with patch("transformer.mhap_table_to_pmo") as mock_transform:
            mock_result = pd.DataFrame({"transformed": ["data"]})
            mock_transform.return_value = mock_result

            transform_mhap_info(df, "bioinfo_1", field_mapping, optional_mapping)

            mock_transform.assert_called_once()
            call_args = mock_transform.call_args[1]
            assert call_args["umis_col"] is None
            assert call_args["chrom_col"] is None


class TestTransformPanelInfo:
    """Test cases for transform_panel_info function."""

    def test_transform_panel_info_basic(self):
        """Test basic transformation of panel info."""
        df = pd.DataFrame(
            {
                "target": ["T1", "T2"],
                "forward": ["ATCG", "GCTA"],
                "reverse": ["CGAT", "TAGC"],
            }
        )
        field_mapping = {
            "target_name": "target",
            "forward_primer_seq": "forward",
            "reverse_primer_seq": "reverse",
        }
        optional_fields = {}
        target_genome_info = {"genome": "test"}

        with patch("transformer.panel_info_table_to_pmo") as mock_transform:
            mock_result = pd.DataFrame({"transformed": ["data"]})
            mock_transform.return_value = mock_result

            result = transform_panel_info(
                df, "panel_1", field_mapping, target_genome_info, optional_fields
            )

            assert result is not None
            mock_transform.assert_called_once()
            call_args = mock_transform.call_args[1]
            assert call_args["target_name_col"] == "target"
            assert call_args["forward_primers_seq_col"] == "forward"
            assert call_args["reverse_primers_seq_col"] == "reverse"

    def test_transform_panel_info_with_optional_fields(self):
        """Test transformation with optional fields."""
        df = pd.DataFrame({"target": ["T1"], "forward": ["ATCG"], "reverse": ["CGAT"]})
        field_mapping = {
            "target_name": "target",
            "forward_primer_seq": "forward",
            "reverse_primer_seq": "reverse",
        }
        optional_fields = {
            "gene_name": "gene_col",
            "target_attributes": "attrs_col",
        }
        target_genome_info = {"genome": "test"}

        with patch("transformer.panel_info_table_to_pmo") as mock_transform:
            mock_result = pd.DataFrame({"transformed": ["data"]})
            mock_transform.return_value = mock_result

            transform_panel_info(
                df, "panel_1", field_mapping, target_genome_info, optional_fields
            )

            mock_transform.assert_called_once()
            call_args = mock_transform.call_args[1]
            assert call_args["gene_name_col"] == "gene_col"
            assert call_args["target_attributes_col"] == "attrs_col"


class TestTransformSpecimenInfo:
    """Test cases for transform_specimen_info function."""

    def test_transform_specimen_info_basic(self):
        """Test basic transformation of specimen info."""
        df = pd.DataFrame(
            {
                "specimen": ["S1", "S2"],
                "specimen_taxon": [123, 456],
                "host_taxon": [789, 101],
            }
        )
        field_mapping = {
            "specimen_name": "specimen",
            "specimen_taxon_id": "specimen_taxon",
            "host_taxon_id": "host_taxon",
            "collection_date": "date_col",
            "collection_country": "country_col",
            "project_name": "project_col",
        }
        optional_field_mapping = {}

        with patch("transformer.specimen_info_table_to_pmo") as mock_transform:
            mock_result = pd.DataFrame({"transformed": ["data"]})
            mock_transform.return_value = mock_result

            result = transform_specimen_info(df, field_mapping, optional_field_mapping)

            assert result is not None
            mock_transform.assert_called_once()
            call_args = mock_transform.call_args[1]
            assert call_args["specimen_name_col"] == "specimen"
            assert call_args["specimen_taxon_id_col"] == "specimen_taxon"
            assert call_args["host_taxon_id_col"] == "host_taxon"

    def test_transform_specimen_info_with_optional_fields(self):
        """Test transformation with optional fields."""
        df = pd.DataFrame(
            {"specimen": ["S1"], "specimen_taxon": [123], "host_taxon": [789]}
        )
        field_mapping = {
            "specimen_name": "specimen",
            "specimen_taxon_id": "specimen_taxon",
            "host_taxon_id": "host_taxon",
            "collection_date": "date_col",
            "collection_country": "country_col",
            "project_name": "project_col",
        }
        optional_field_mapping = {
            "host_age": "age_col",
            "host_sex": "sex_col",
            "lat_lon": "location_col",
        }

        with patch("transformer.specimen_info_table_to_pmo") as mock_transform:
            mock_result = pd.DataFrame({"transformed": ["data"]})
            mock_transform.return_value = mock_result

            transform_specimen_info(df, field_mapping, optional_field_mapping)

            mock_transform.assert_called_once()
            call_args = mock_transform.call_args[1]
            assert call_args["host_age_col"] == "age_col"
            assert call_args["host_sex_col"] == "sex_col"
            assert call_args["lat_lon_col"] == "location_col"

    def test_transform_specimen_info_with_none_alternate_identifiers(self):
        """Test transformation with None alternate_identifiers."""
        df = pd.DataFrame(
            {"specimen": ["S1"], "specimen_taxon": [123], "host_taxon": [789]}
        )
        field_mapping = {
            "specimen_name": "specimen",
            "specimen_taxon_id": "specimen_taxon",
            "host_taxon_id": "host_taxon",
            "collection_date": "date_col",
            "collection_country": "country_col",
            "project_name": "project_col",
        }
        optional_field_mapping = {"alternate_identifiers": None}

        with patch("transformer.specimen_info_table_to_pmo") as mock_transform:
            mock_result = pd.DataFrame({"transformed": ["data"]})
            mock_transform.return_value = mock_result

            transform_specimen_info(df, field_mapping, optional_field_mapping)

            mock_transform.assert_called_once()
            call_args = mock_transform.call_args[1]
            assert call_args["list_values_specimen_columns"] == []

    def test_transform_specimen_info_with_alternate_identifiers(self):
        """Test transformation with alternate_identifiers provided."""
        df = pd.DataFrame(
            {"specimen": ["S1"], "specimen_taxon": [123], "host_taxon": [789]}
        )
        field_mapping = {
            "specimen_name": "specimen",
            "specimen_taxon_id": "specimen_taxon",
            "host_taxon_id": "host_taxon",
            "collection_date": "date_col",
            "collection_country": "country_col",
            "project_name": "project_col",
        }
        optional_field_mapping = {"alternate_identifiers": "alt_id_col"}

        with patch("transformer.specimen_info_table_to_pmo") as mock_transform:
            mock_result = pd.DataFrame({"transformed": ["data"]})
            mock_transform.return_value = mock_result

            transform_specimen_info(df, field_mapping, optional_field_mapping)

            mock_transform.assert_called_once()
            call_args = mock_transform.call_args[1]
            assert call_args["list_values_specimen_columns"] == "alt_id_col"


class TestTransformLibrarySampleInfo:
    """Test cases for transform_library_sample_info function."""

    def test_transform_library_sample_info_basic(self):
        """Test basic transformation of library sample info."""
        df = pd.DataFrame(
            {
                "library_sample": ["LS1", "LS2"],
                "sequencing_info": ["SI1", "SI2"],
                "specimen": ["S1", "S2"],
                "panel": ["P1", "P2"],
            }
        )
        field_mapping = {
            "library_sample_name": "library_sample",
            "sequencing_info_name": "sequencing_info",
            "specimen_name": "specimen",
            "panel_name": "panel",
        }
        optional_mapping = {}

        with patch("transformer.library_sample_info_table_to_pmo") as mock_transform:
            mock_result = pd.DataFrame({"transformed": ["data"]})
            mock_transform.return_value = mock_result

            result = transform_library_sample_info(df, field_mapping, optional_mapping)

            assert result is not None
            mock_transform.assert_called_once()
            call_args = mock_transform.call_args[1]
            assert call_args["library_sample_name_col"] == "library_sample"
            assert call_args["sequencing_info_name_col"] == "sequencing_info"
            assert call_args["specimen_name_col"] == "specimen"
            assert call_args["panel_name_col"] == "panel"

    def test_transform_library_sample_info_with_optional_fields(self):
        """Test transformation with optional fields."""
        df = pd.DataFrame(
            {
                "library_sample": ["LS1"],
                "sequencing_info": ["SI1"],
                "specimen": ["S1"],
                "panel": ["P1"],
            }
        )
        field_mapping = {
            "library_sample_name": "library_sample",
            "sequencing_info_name": "sequencing_info",
            "specimen_name": "specimen",
            "panel_name": "panel",
        }
        optional_mapping = {
            "accession": "accession_col",
            "library_prep_plate_name": "plate_name_col",
        }

        with patch("transformer.library_sample_info_table_to_pmo") as mock_transform:
            mock_result = pd.DataFrame({"transformed": ["data"]})
            mock_transform.return_value = mock_result

            transform_library_sample_info(df, field_mapping, optional_mapping)

            mock_transform.assert_called_once()
            call_args = mock_transform.call_args[1]
            assert call_args["accession_col"] == "accession_col"
            assert call_args["library_prep_plate_name_col"] == "plate_name_col"

    def test_transform_library_sample_info_with_none_optional_fields(self):
        """Test transformation with None optional fields."""
        df = pd.DataFrame(
            {
                "library_sample": ["LS1"],
                "sequencing_info": ["SI1"],
                "specimen": ["S1"],
                "panel": ["P1"],
            }
        )
        field_mapping = {
            "library_sample_name": "library_sample",
            "sequencing_info_name": "sequencing_info",
            "specimen_name": "specimen",
            "panel_name": "panel",
        }
        optional_mapping = {
            "accession": None,
            "library_prep_plate_name": None,
        }

        with patch("transformer.library_sample_info_table_to_pmo") as mock_transform:
            mock_result = pd.DataFrame({"transformed": ["data"]})
            mock_transform.return_value = mock_result

            transform_library_sample_info(df, field_mapping, optional_mapping)

            mock_transform.assert_called_once()
            call_args = mock_transform.call_args[1]
            assert call_args["accession_col"] is None
            assert call_args["library_prep_plate_name_col"] is None
