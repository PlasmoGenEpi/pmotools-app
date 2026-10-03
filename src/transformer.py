import inspect

from pmotools.pmo_builder.mhap_table_to_pmo import mhap_table_to_pmo
from pmotools.pmo_builder.panel_information_to_pmo import panel_info_table_to_pmo
from pmotools.pmo_builder.read_count_by_stage_table_to_pmo import (
    read_count_by_stage_table_to_pmo,
)
from pmotools.pmo_builder.metatable_to_pmo import (
    library_sample_info_table_to_pmo,
    specimen_info_table_to_pmo,
)

PSEUDOCIGAR_LOCATION_FIELDS = [
    "pseudocigar_chrom",
    "pseudocigar_start",
    "pseudocigar_end",
    "pseudocigar_ref_seq",
    "pseudocigar_strand",
    "pseudocigar_generation_description",
]
PMOTOOLS_SUPPORTS_PSEUDOCIGAR_LOCATION = (
    "pseudocigar_start_col" in inspect.signature(mhap_table_to_pmo).parameters
)


def _fill_blanks(df, cols):
    """Replace missing values with empty strings in the given columns.

    pmotools (<= 1.1.0 and develop) calls string methods on these columns
    without checking for missing values, so partly filled columns crash.
    """
    cols = [c for c in cols if c and c in df.columns]
    if not cols:
        return df
    df = df.copy()
    df[cols] = df[cols].fillna("")
    return df


def _pseudocigar_kwargs(optional_mapping):
    kwargs = {
        f"{field}_col": optional_mapping.get(field)
        for field in PSEUDOCIGAR_LOCATION_FIELDS
    }
    if PMOTOOLS_SUPPORTS_PSEUDOCIGAR_LOCATION:
        return kwargs
    if optional_mapping.get("pseudocigar"):
        raise ValueError(
            "Including pseudocigars requires a newer version of pmotools than "
            "the one installed. Set the pseudocigar field to 'no match' to continue."
        )
    return {}


def transform_mhap_info(
    df, bioinfo_id, field_mapping, optional_mapping, additional_mhap_detected_cols=None
):
    """Reformat the DataFrame based on the provided field mapping."""
    transformed_df = mhap_table_to_pmo(
        df,
        bioinfo_id,
        library_sample_name_col=field_mapping["library_sample_name"],
        target_name_col=field_mapping["target_name"],
        seq_col=field_mapping["seq"],
        reads_col=field_mapping["reads"],
        umis_col=optional_mapping.get("umis"),
        chrom_col=optional_mapping.get("chrom"),
        start_col=optional_mapping.get("start"),
        end_col=optional_mapping.get("end"),
        ref_seq_col=optional_mapping.get("ref_seq"),
        strand_col=optional_mapping.get("strand"),
        alt_annotations_col=optional_mapping.get("alt_annotations"),
        masking_seq_start_col=optional_mapping.get("masking_seq_start"),
        masking_seq_segment_size_col=optional_mapping.get("masking_seq_segment_size"),
        masking_replacement_size_col=optional_mapping.get("masking_replacement_size"),
        microhaplotype_name_col=optional_mapping.get("microhaplotype_name"),
        pseudocigar_col=optional_mapping.get("pseudocigar"),
        **_pseudocigar_kwargs(optional_mapping),
        quality_col=optional_mapping.get("quality"),
        additional_representative_mhap_cols=optional_mapping.get(
            "additional_representative_mhap"
        ),
        additional_mhap_detected_cols=additional_mhap_detected_cols,
    )
    return transformed_df


def transform_panel_info(
    df,
    panel_id,
    field_mapping,
    target_genome_info,
    optional_fields,
    additional_target_info_cols=None,
):
    """Reformat the DataFrame based on the provided field mapping."""
    transformed_df = panel_info_table_to_pmo(
        _fill_blanks(df, [optional_fields.get("target_attributes")]),
        panel_id,
        target_genome_info,
        target_name_col=field_mapping["target_name"],
        forward_primers_seq_col=field_mapping["forward_primer_seq"],
        reverse_primers_seq_col=field_mapping["reverse_primer_seq"],
        reaction_name_col=optional_fields.get("reaction_name"),
        forward_primers_start_col=optional_fields.get("forward_primers_start"),
        forward_primers_end_col=optional_fields.get("forward_primers_end"),
        reverse_primers_start_col=optional_fields.get("reverse_primers_start"),
        reverse_primers_end_col=optional_fields.get("reverse_primers_end"),
        insert_start_col=optional_fields.get("insert_start"),
        insert_end_col=optional_fields.get("insert_end"),
        chrom_col=optional_fields.get("chrom"),
        strand_col=optional_fields.get("strand"),
        ref_seq_col=optional_fields.get("ref_seq"),
        genome_id_col=optional_fields.get("genome_id"),
        gene_name_col=optional_fields.get("gene_name"),
        target_attributes_col=optional_fields.get("target_attributes"),
        additional_target_info_cols=additional_target_info_cols,
    )
    for target in transformed_df.get("target_info", []):
        if target.get("target_attributes") == [""]:
            del target["target_attributes"]
        # pmotools 1.1.0 swaps the forward primer start and end
        location = target.get("forward_primer", {}).get("location")
        if location and location["start"] > location["end"]:
            location["start"], location["end"] = location["end"], location["start"]
    return transformed_df


def transform_specimen_info(
    df, field_mapping, optional_field_mapping, additional_fields=None
):
    df = _fill_blanks(
        df,
        [
            optional_field_mapping.get("storage_plate_name"),
            optional_field_mapping.get("storage_plate_row"),
        ],
    )
    transformed_df = specimen_info_table_to_pmo(
        df,
        specimen_name_col=field_mapping["specimen_name"],
        specimen_taxon_id_col=optional_field_mapping.get("specimen_taxon_id"),
        host_taxon_id_col=optional_field_mapping.get("host_taxon_id"),
        collection_date_col=optional_field_mapping.get("collection_date"),
        collection_country_col=optional_field_mapping.get("collection_country"),
        project_name_col=optional_field_mapping.get("project_name"),
        # optional fields - only pass if not None
        alternate_identifiers_col=optional_field_mapping.get("alternate_identifiers"),
        blood_meal_col=optional_field_mapping.get("blood_meal"),
        drug_usage_col=optional_field_mapping.get("drug_usage"),
        env_broad_scale_col=optional_field_mapping.get("env_broad_scale"),
        env_local_scale_col=optional_field_mapping.get("env_local_scale"),
        env_medium_col=optional_field_mapping.get("env_medium"),
        geo_admin1_col=optional_field_mapping.get("geo_admin1"),
        geo_admin2_col=optional_field_mapping.get("geo_admin2"),
        geo_admin3_col=optional_field_mapping.get("geo_admin3"),
        gravid_col=optional_field_mapping.get("gravid"),
        gravidity_col=optional_field_mapping.get("gravidity"),
        has_travel_out_six_month_col=optional_field_mapping.get(
            "has_travel_out_six_month"
        ),
        host_age_col=optional_field_mapping.get("host_age"),
        host_sex_col=optional_field_mapping.get("host_sex"),
        host_subject_id=optional_field_mapping.get("host_subject_name"),
        lat_lon_col=optional_field_mapping.get("lat_lon"),
        parasite_density_col=optional_field_mapping.get("parasite_density"),
        parasite_density_method_col=optional_field_mapping.get(
            "parasite_density_method"
        ),
        storage_plate_col_col=optional_field_mapping.get("storage_plate_col"),
        storage_plate_name_col=optional_field_mapping.get("storage_plate_name"),
        storage_plate_row_col=optional_field_mapping.get("storage_plate_row"),
        storage_plate_position_col=optional_field_mapping.get("storage_plate_position"),
        specimen_collect_device_col=optional_field_mapping.get(
            "specimen_collect_device"
        ),
        specimen_comments_col=optional_field_mapping.get("specimen_comments"),
        specimen_store_loc_col=optional_field_mapping.get("specimen_store_loc"),
        specimen_type_col=optional_field_mapping.get("specimen_type"),
        treatment_status_col=optional_field_mapping.get("treatment_status"),
        additional_specimen_cols=additional_fields,
        list_values_specimen_values_delimiter=",",
    )
    # pmotools writes host_subject_id; the PMO schema field is host_subject_name
    for specimen in transformed_df:
        if "host_subject_id" in specimen:
            specimen["host_subject_name"] = specimen.pop("host_subject_id")

    return transformed_df


def transform_library_sample_info(
    df, field_mapping, optional_mapping, additional_fields=None
):
    library_col = field_mapping["library_sample_name"]
    specimen_col = field_mapping["specimen_name"]
    plate_and_density_cols = [
        optional_mapping.get(field)
        for field in [
            "library_prep_plate_name",
            "library_prep_plate_row",
            "library_prep_plate_col",
            "library_prep_plate_position",
            "parasite_density",
            "parasite_density_method",
        ]
    ]
    # pmotools 1.1.0 looks up plate and parasite density values by specimen name,
    # which picks the wrong row when a specimen has several library samples, so
    # match on library sample name and restore the specimen names afterwards.
    specimen_by_library = None
    if any(plate_and_density_cols):
        specimen_by_library = dict(zip(df[library_col], df[specimen_col]))
        df = df.copy()
        df[specimen_col] = df[library_col]
    df = _fill_blanks(
        df,
        [
            optional_mapping.get("library_prep_plate_name"),
            optional_mapping.get("library_prep_plate_row"),
        ],
    )

    transformed_df = library_sample_info_table_to_pmo(
        df,
        library_sample_name_col=library_col,
        sequencing_info_name_col=optional_mapping.get("sequencing_info_name"),
        specimen_name_col=specimen_col,
        panel_name_col=field_mapping["panel_name"],
        alternate_identifiers_col=optional_mapping.get("alternate_identifiers"),
        experiment_accession_col=optional_mapping.get("experiment_accession"),
        fastqs_loc_col=optional_mapping.get("fastqs_loc"),
        library_prep_plate_name_col=optional_mapping.get("library_prep_plate_name"),
        library_prep_plate_col_col=optional_mapping.get("library_prep_plate_col"),
        library_prep_plate_row_col=optional_mapping.get("library_prep_plate_row"),
        library_prep_plate_position_col=optional_mapping.get(
            "library_prep_plate_position"
        ),
        parasite_density_col=optional_mapping.get("parasite_density"),
        parasite_density_method_col=optional_mapping.get("parasite_density_method"),
        run_accession_col=optional_mapping.get("run_accession"),
        additional_library_sample_info_cols=additional_fields,
    )
    for library_sample in transformed_df:
        if specimen_by_library is not None:
            library_sample["specimen_name"] = specimen_by_library[
                library_sample["library_sample_name"]
            ]
        # pmotools 1.1.0 writes parasite_density_info; the PMO schema field for
        # library samples is qpcr_parasite_density_info
        if "parasite_density_info" in library_sample:
            library_sample["qpcr_parasite_density_info"] = library_sample.pop(
                "parasite_density_info"
            )

    return transformed_df


def transform_read_counts_per_stage(
    raw_counts_df,
    reads_by_stage_df,
    bioinfo_run_name,
    raw_counts_field_mapping,
    reads_by_stage_field_mapping,
    raw_counts_selected_additional_fields=None,
    reads_by_stage_selected_additional_fields=None,
):
    transformed_df = read_count_by_stage_table_to_pmo(
        bioinformatics_run_name=bioinfo_run_name,
        total_raw_count_table=raw_counts_df,
        reads_by_stage_table=reads_by_stage_df,
        library_sample_name_col=raw_counts_field_mapping["library_sample_name"],
        total_raw_count_col=raw_counts_field_mapping["total_raw_count"],
        target_name_col=reads_by_stage_field_mapping["target_name"],
        stage_col=reads_by_stage_field_mapping["stage"],
        read_count_col=reads_by_stage_field_mapping["read_count"],
        additional_library_sample_cols=raw_counts_selected_additional_fields,
        additional_target_cols=reads_by_stage_selected_additional_fields,
    )
    return transformed_df
