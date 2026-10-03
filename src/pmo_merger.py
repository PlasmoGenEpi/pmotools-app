"""Read uploaded PMO files and merge them with pmotools-python."""

import copy
import gzip
import inspect
import json
from importlib import resources

from jsonschema import ValidationError
from pmotools.pmo_engine.pmo_checker import PMOChecker, load_schema_by_version
from pmotools.pmo_engine.pmo_reader import PMOReader

from src.upload_utils import iter_uploaded_files

UPLOAD_TYPES = ["json", "gz", "zip", "tgz", "tar"]
PMO_SUFFIXES = (".json", ".json.gz")

# pmotools 1.1.0 links merged bioinformatics runs to the wrong pipeline and
# merged microhaplotypes to the wrong target in some cases (fixed on develop).
PMOTOOLS_COMBINE_FIXED = "new_rep_target" in inspect.getsource(
    PMOReader.combine_multiple_pmos
)


def available_schema_versions():
    prefix, suffix = "portable_microhaplotype_object_v", ".schema.json"
    names = [p.name for p in resources.files("pmotools.schemas").iterdir()]
    versions = [n[len(prefix) : -len(suffix)] for n in names if n.startswith(prefix)]
    return sorted(versions, key=lambda v: [int(x) for x in v.split(".")])


def read_pmo_uploads(files):
    """Read PMO files from uploads, expanding zipped or tarred folders.

    Returns (pmos, ignored, errors): pmos is a list of (file name, PMO dict),
    ignored lists files that are not PMO files, and errors maps file names to
    the reason they could not be read.
    """
    pmos, ignored, errors = [], [], {}
    for name, data in iter_uploaded_files(files):
        lower = name.lower()
        if not lower.endswith(PMO_SUFFIXES):
            ignored.append(name)
            continue
        try:
            if lower.endswith(".gz"):
                data = gzip.decompress(data)
            pmo = json.loads(data)
        except (OSError, ValueError) as e:
            errors[name] = f"not a readable JSON file ({e})"
            continue
        if not isinstance(pmo, dict) or "target_info" not in pmo:
            errors[name] = "does not look like a PMO (no target_info)"
            continue
        pmos.append((name, pmo))
    return pmos, ignored, errors


def pmo_schema_version(pmo):
    """The schema version a PMO declares, if pmotools has that schema."""
    version = str(pmo.get("pmo_header", {}).get("pmo_version", "")).lstrip("v")
    return version if version in available_schema_versions() else None


def validate_pmo(pmo, version=None):
    """Return None if the PMO is valid against the schema, else the error."""
    version = version or pmo_schema_version(pmo) or available_schema_versions()[-1]
    try:
        PMOChecker(load_schema_by_version(version)).validate_pmo_json(pmo)
    except ValidationError as e:
        path = " -> ".join(str(p) for p in e.absolute_path) or "root"
        return f"{e.message} (at {path})"
    return None


def summarise_pmo(pmo):
    detected = pmo.get("detected_microhaplotypes", [])
    return {
        "Panels": len(pmo.get("panel_info", [])),
        "Targets": len(pmo.get("target_info", [])),
        "Specimens": len(pmo.get("specimen_info", [])),
        "Library samples": len(pmo.get("library_sample_info", [])),
        "Bioinformatics runs": len(pmo.get("bioinformatics_run_info", [])),
        "Library samples with microhaplotypes": sum(
            len(d.get("library_samples", [])) for d in detected
        ),
    }


def _target_name(pmo, target_id):
    return pmo["target_info"][target_id]["target_name"]


def unsupported_merge_reasons(pmos):
    """Reasons the installed pmotools would merge these PMOs incorrectly."""
    if PMOTOOLS_COMBINE_FIXED:
        return []
    reasons = []
    target_index = {}
    rep_target_names = set()
    for i, (name, pmo) in enumerate(pmos):
        for target in pmo["target_info"]:
            target_index.setdefault(target["target_name"], len(target_index))
        rep_targets = pmo.get("representative_microhaplotypes", {}).get("targets", [])
        for rep in rep_targets:
            target_name = _target_name(pmo, rep["target_id"])
            if (
                i > 0
                and target_name not in rep_target_names
                and target_index[target_name] != rep["target_id"]
            ):
                reasons.append(
                    f"{name} has targets that are not in the earlier files, so their"
                    " microhaplotypes would be linked to the wrong targets"
                )
                break
        rep_target_names.update(_target_name(pmo, r["target_id"]) for r in rep_targets)
        if i > 0:
            runs = pmo.get("bioinformatics_run_info", [])
            if any(r["bioinformatics_methods_id"] != j for j, r in enumerate(runs)):
                reasons.append(
                    f"{name} has bioinformatics runs that would be linked to the"
                    " wrong bioinformatics methods"
                )
    return reasons


def merge_pmos(pmos):
    """Merge a list of (file name, PMO) into one PMO with pmotools-python."""
    if len(pmos) < 2:
        raise ValueError("Upload at least two PMO files to merge.")
    reasons = unsupported_merge_reasons(pmos)
    if reasons:
        raise ValueError(
            "These PMOs can't be merged correctly with the installed version of"
            " pmotools; a newer version is needed:\n- " + "\n- ".join(reasons)
        )
    return PMOReader.combine_multiple_pmos([copy.deepcopy(pmo) for _, pmo in pmos])
