"""
Tests for pmo_merger.py: read uploaded PMO files and merge them with pmotools.
"""

import gzip
import json
import tarfile
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest
from pmotools.pmo_builder.merge_to_pmo import merge_to_pmo
from pmotools.pmo_builder.metatable_to_pmo import specimen_info_table_to_pmo
from pmotools.pmo_builder.mhap_table_to_pmo import mhap_table_to_pmo
from pmotools.pmo_builder.panel_information_to_pmo import panel_info_table_to_pmo

import pmo_merger
from pmo_merger import (
    merge_pmos,
    read_pmo_uploads,
    summarise_pmo,
    unsupported_merge_reasons,
    validate_pmo,
)

PRIMERS = {"t1": ("ACGT", "TTGA"), "t2": ("GGCC", "AATT"), "t3": ("CCAA", "GGTT")}


class _Upload(BytesIO):
    def __init__(self, name, data):
        super().__init__(data)
        self.name = name


def _seq(target, sample):
    """A sequence unique to the target and sample, starting with the target's
    forward primer."""
    return PRIMERS[target][0] + "".join("ACGT"[int(c) % 4] for c in sample[1:])


def _make_pmo(samples, targets=("t1", "t2"), run_name="run1", methods_first=False):
    panel = panel_info_table_to_pmo(
        pd.DataFrame(
            [
                dict(target_name=t, fwd_primer=PRIMERS[t][0], rev_primer=PRIMERS[t][1])
                for t in targets
            ]
        ),
        "panelA",
    )
    mhaps = mhap_table_to_pmo(
        pd.DataFrame(
            [
                dict(library_sample_name=s, target_name=t, seq=_seq(t, s), reads=10)
                for s in samples
                for t in targets
            ]
        ),
        run_name,
    )
    specimens = specimen_info_table_to_pmo(
        pd.DataFrame(
            [
                dict(
                    specimen_name=s,
                    specimen_taxon_id=5833,
                    host_taxon_id=9606,
                    collection_date="2024-01-01",
                    collection_country="Kenya",
                    project_name="proj1",
                )
                for s in samples
            ]
        ),
        specimen_taxon_id_col="specimen_taxon_id",
        host_taxon_id_col="host_taxon_id",
        collection_date_col="collection_date",
        collection_country_col="collection_country",
        project_name_col="project_name",
    )
    methods = [{"methods": [{"program": "dada2", "program_version": "1.26"}]}]
    run_methods_id = 0
    if methods_first:
        methods.insert(0, {"methods": [{"program": "other", "program_version": "1"}]})
        run_methods_id = 1
    pmo = merge_to_pmo(
        mhap_info=mhaps,
        panel_target_info=panel,
        specimen_info=specimens,
        library_sample_info=[
            dict(library_sample_name=s, specimen_name=s, panel_name="panelA")
            for s in samples
        ],
        bioinfo_method_info=methods,
        bioinfo_run_info=[
            dict(
                bioinformatics_run_name=run_name,
                bioinformatics_methods_id=run_methods_id,
            )
        ],
        project_info=[dict(project_name="proj1", project_description="A project")],
    )
    return json.loads(json.dumps(pmo, default=str))


def _bytes(pmo, compress=False):
    data = json.dumps(pmo).encode()
    return gzip.compress(data) if compress else data


def test_read_json_gz_and_zip_folder():
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("pmos/b.json.gz", _bytes(_make_pmo(["S3"]), compress=True))
        archive.writestr("pmos/notes.txt", "notes")
        archive.writestr("__MACOSX/pmos/._b.json.gz", "junk")
    files = [
        _Upload("a.json", _bytes(_make_pmo(["S1", "S2"]))),
        _Upload("pmos.zip", buffer.getvalue()),
        _Upload("broken.json", b"{not json"),
        _Upload("table.json", b"[1, 2]"),
    ]
    pmos, ignored, errors = read_pmo_uploads(files)
    assert [name for name, _ in pmos] == ["a.json", "pmos/b.json.gz"]
    assert ignored == ["pmos/notes.txt"]
    assert set(errors) == {"broken.json", "table.json"}


def test_read_tar_gz_folder():
    buffer = BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, samples in (("a.json", ["S1"]), ("b.json", ["S2"])):
            data = _bytes(_make_pmo(samples))
            info = tarfile.TarInfo(f"pmos/{name}")
            info.size = len(data)
            archive.addfile(info, BytesIO(data))
    pmos, ignored, errors = read_pmo_uploads(
        [_Upload("pmos.tar.gz", buffer.getvalue())]
    )
    assert len(pmos) == 2 and ignored == [] and errors == {}


def test_merge_pmos_with_different_samples():
    pmos = [
        ("a.json", _make_pmo(["S1", "S2"], run_name="run1")),
        ("b.json", _make_pmo(["S3"], run_name="run2")),
        ("c.json", _make_pmo(["S4"], run_name="run3")),
    ]
    for _, pmo in pmos:
        assert validate_pmo(pmo) is None
    merged = merge_pmos(pmos)
    assert validate_pmo(merged) is None
    assert summarise_pmo(merged) == {
        "Panels": 1,
        "Targets": 2,
        "Specimens": 4,
        "Library samples": 4,
        "Bioinformatics runs": 3,
        "Library samples with microhaplotypes": 4,
    }
    assert len(merged["project_info"]) == 1
    assert pmos[0][1]["representative_microhaplotypes"]["targets"][0][
        "microhaplotypes"
    ] == [
        {"seq": _seq("t1", "S1")},
        {"seq": _seq("t1", "S2")},
    ]


def test_example_pmos_merge():
    example = Path(__file__).parent.parent / "example_data" / "pmos_to_merge.zip"
    pmos, ignored, errors = read_pmo_uploads(
        [_Upload(example.name, example.read_bytes())]
    )
    assert len(pmos) == 3 and ignored == [] and errors == {}
    merged = merge_pmos(pmos)
    assert validate_pmo(merged) is None
    assert summarise_pmo(merged)["Library samples"] == 49
    assert len(merged["project_info"]) == 1


def test_merge_needs_two_pmos():
    with pytest.raises(ValueError, match="at least two"):
        merge_pmos([("a.json", _make_pmo(["S1"]))])


def test_duplicate_library_samples_rejected():
    pmos = [("a.json", _make_pmo(["S1"])), ("b.json", _make_pmo(["S1"]))]
    with pytest.raises(Exception, match="Duplicate"):
        merge_pmos(pmos)


def test_validate_reports_errors():
    pmo = _make_pmo(["S1"])
    del pmo["panel_info"]
    assert "panel_info" in validate_pmo(pmo)


@pytest.mark.parametrize("fixed", [False, True])
def test_unsupported_merges_detected(monkeypatch, fixed):
    monkeypatch.setattr(pmo_merger, "PMOTOOLS_COMBINE_FIXED", fixed)
    new_targets = [
        ("a.json", _make_pmo(["S1"], targets=("t1", "t2"))),
        ("b.json", _make_pmo(["S2"], targets=("t3", "t1"), run_name="run2")),
    ]
    methods_order = [
        ("a.json", _make_pmo(["S1"])),
        ("b.json", _make_pmo(["S2"], run_name="run2", methods_first=True)),
    ]
    same_targets = [("a.json", _make_pmo(["S1"])), ("b.json", _make_pmo(["S2"]))]

    assert unsupported_merge_reasons(same_targets) == []
    if fixed:
        assert unsupported_merge_reasons(new_targets) == []
        assert unsupported_merge_reasons(methods_order) == []
    else:
        assert "wrong targets" in unsupported_merge_reasons(new_targets)[0]
        assert (
            "wrong bioinformatics methods"
            in unsupported_merge_reasons(methods_order)[0]
        )
        with pytest.raises(ValueError, match="newer version"):
            merge_pmos(new_targets)


@pytest.mark.skipif(
    not pmo_merger.PMOTOOLS_COMBINE_FIXED, reason="needs newer pmotools"
)
def test_merge_with_new_targets_and_methods_order():
    merged = merge_pmos(
        [
            ("a.json", _make_pmo(["S1"], targets=("t1", "t2"))),
            (
                "b.json",
                _make_pmo(
                    ["S2"], targets=("t3", "t1"), run_name="run2", methods_first=True
                ),
            ),
        ]
    )
    assert validate_pmo(merged) is None
    target_names = [t["target_name"] for t in merged["target_info"]]
    for rep in merged["representative_microhaplotypes"]["targets"]:
        name = target_names[rep["target_id"]]
        assert all(
            m["seq"].startswith(PRIMERS[name][0]) for m in rep["microhaplotypes"]
        )
    run2 = merged["bioinformatics_run_info"][1]
    methods = merged["bioinformatics_methods_info"][run2["bioinformatics_methods_id"]]
    assert methods["methods"][0]["program"] == "dada2"
