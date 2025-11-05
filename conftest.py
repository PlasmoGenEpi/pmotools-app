"""
Pytest configuration for pmotools-app
"""
import pytest
import sys
import os

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


@pytest.fixture
def sample_field_names():
    """Sample field names for testing."""
    return ["sample_id", "patient_name", "collection_date", "extra_field"]


@pytest.fixture
def sample_target_schema():
    """Sample target schema for testing."""
    return ["sampleID", "patientName", "collectionDate"]


@pytest.fixture
def sample_alternate_schema():
    """Sample alternate schema names for testing."""
    return {
        "sampleID": ["sample_id", "id"],
        "patientName": ["patient_name", "name"],
        "collectionDate": ["collection_date", "date"],
    }


@pytest.fixture
def sample_field_mapping():
    """Sample field mapping for testing."""
    return {
        "sampleID": "sample_id",
        "patientName": "patient_name",
        "collectionDate": None,
    }
