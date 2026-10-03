"""
End-to-end tests running the transformers against the installed pmotools,
covering the pmotools issues the transformers work around.
"""
import json

import numpy as np
import pandas as pd
import pytest
from pmotools.pmo_builder.merge_to_pmo import merge_to_pmo
from pmotools.pmo_engine.pmo_checker import PMOChecker, load_schema_by_version

from transformer import (
    PMOTOOLS_SUPPORTS_PSEUDOCIGAR_LOCATION,
    transform_library_sample_info,
    transform_mhap_info,
    transform_panel_info,
    transform_specimen_info,
)

GENOME = {
    "name": "Pf3D7",
    "taxon_id": [5833],
    "genome_version": "2020",
    "url": "https://plasmodb.org/Pf3D7.fasta",
}
PANEL_REQUIRED = {
    "target_name": "target_name",
    "forward_primer_seq": "forward_primer_seq",
    "reverse_primer_seq": "reverse_primer_seq",
}


def _identity(df, fields):
    return {f: (f if f in df.columns else None) for f in fields}


def _panel(**extra_cols):
    df = pd.DataFrame(
        {
            "target_name": ["t1", "t2"],
            "forward_primer_seq": ["ACGT", "GGCC"],
            "reverse_primer_seq": ["TTGA", "AATT"],
            **extra_cols,
        }
    ).astype(object)
    return transform_panel_info(
        df, "panelA", PANEL_REQUIRED, GENOME, _identity(df, extra_cols)
    )


def _mhap():
    df = pd.DataFrame(
        {
            "library_sample_name": ["L1", "L2", "L3"],
            "target_name": ["t1", "t1", "t2"],
            "seq": ["AAAA", "AAAT", "CCCC"],
            "reads": [10, 7, 5],
        }
    ).astype(object)
    return transform_mhap_info(df, "run1", _identity(df, df.columns), {})


def _validate(**sections):
    pmo = merge_to_pmo(
        sections.pop("mhap", _mhap()),
        sections.pop("panel", _panel()),
        bioinfo_run_info=[
            {"bioinformatics_run_name": "run1", "bioinformatics_methods_id": 0}
        ],
        bioinfo_method_info=[{"methods": [{"program": "x", "program_version": "1"}]}],
        **sections,
    )
    pmo = json.loads(json.dumps(pmo, default=str))
    PMOChecker(load_schema_by_version("1.1.0")).validate_pmo_json(pmo)
    return pmo


def test_partly_blank_target_attributes():
    panel = _panel(target_attributes=["drug,diversity", np.nan])
    targets = {t["target_name"]: t for t in panel["target_info"]}
    assert targets["t1"]["target_attributes"] == ["drug", "diversity"]
    assert "target_attributes" not in targets["t2"]
    _validate(panel=panel)


def test_forward_primer_location_order():
    panel = _panel(
        chrom=["chr1", "chr2"],
        forward_primers_start=[10, 20],
        forward_primers_end=[14, 24],
    )
    location = panel["target_info"][0]["forward_primer"]["location"]
    assert (location["start"], location["end"]) == (10, 14)


def test_specimen_partly_blank_plate_and_host_subject_name():
    df = pd.DataFrame(
        {
            "specimen_name": ["S1", "S2", "S3"],
            "host_subject_name": ["P1", "P2", "P3"],
            "storage_plate_name": ["plate1", np.nan, "plate1"],
            "storage_plate_row": ["a", np.nan, "B"],
            "storage_plate_col": [1, np.nan, 2],
        }
    ).astype(object)
    specimens = transform_specimen_info(
        df, {"specimen_name": "specimen_name"}, _identity(df, df.columns[1:])
    )
    by_name = {s["specimen_name"]: s for s in specimens}
    assert by_name["S1"]["storage_plate_info"] == {
        "plate_name": "plate1",
        "plate_row": "A",
        "plate_col": 1,
    }
    assert "storage_plate_info" not in by_name["S2"]
    assert by_name["S1"]["host_subject_name"] == "P1"
    assert "host_subject_id" not in by_name["S1"]
    _validate(specimen_info=specimens)


def test_library_plate_and_density_matched_per_library_sample():
    df = pd.DataFrame(
        {
            "library_sample_name": ["L1", "L2", "L3"],
            "specimen_name": ["S1", "S1", "S2"],
            "panel_name": ["panelA"] * 3,
            "library_prep_plate_name": ["LP1", "LP1", "LP1"],
            "library_prep_plate_row": ["A", "B", "C"],
            "library_prep_plate_col": [1, 2, 3],
            "parasite_density": [100.0, 200.0, 300.0],
            "parasite_density_method": ["qPCR"] * 3,
        }
    ).astype(object)
    required = _identity(df, ["library_sample_name", "specimen_name", "panel_name"])
    libraries = transform_library_sample_info(
        df, required, _identity(df, df.columns[3:])
    )
    by_name = {lib["library_sample_name"]: lib for lib in libraries}
    assert by_name["L2"]["specimen_name"] == "S1"
    assert by_name["L2"]["library_prep_plate_info"]["plate_row"] == "B"
    assert by_name["L2"]["qpcr_parasite_density_info"] == [
        {"parasite_density": 200.0, "parasite_density_method": "qPCR"}
    ]
    assert "parasite_density_info" not in by_name["L2"]

    specimens = [{"specimen_name": "S1"}, {"specimen_name": "S2"}]
    _validate(library_sample_info=libraries, specimen_info=specimens)


def test_pseudocigar():
    df = pd.DataFrame(
        {
            "library_sample_name": ["L1"],
            "target_name": ["t1"],
            "seq": ["AAAA"],
            "reads": [10],
            "pseudocigar": ["2A"],
            "pseudocigar_chrom": ["chr1"],
            "pseudocigar_start": [10],
            "pseudocigar_end": [14],
        }
    ).astype(object)
    required = _identity(df, ["library_sample_name", "target_name", "seq", "reads"])
    optional = _identity(df, df.columns[4:])
    if not PMOTOOLS_SUPPORTS_PSEUDOCIGAR_LOCATION:
        with pytest.raises(ValueError, match="newer version of pmotools"):
            transform_mhap_info(df, "run1", required, optional)
        return
    mhap = transform_mhap_info(df, "run1", required, optional)
    mhap_entry = mhap["representative_microhaplotypes"]["targets"][0][
        "microhaplotypes"
    ][0]
    assert mhap_entry["pseudocigar"]["pseudocigar_seq"] == "2A"
    assert mhap_entry["pseudocigar"]["ref_loc"]["start"] == 10
