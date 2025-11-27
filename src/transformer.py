from pmotools.pmo_builder.mhap_table_to_pmo import mhap_table_to_pmo
from pmotools.pmo_builder.panel_information_to_pmo import panel_info_table_to_pmo
from pmotools.pmo_builder.metatable_to_pmo import (
    library_sample_info_table_to_pmo,
    specimen_info_table_to_pmo,
)
# from pmotools.pmo_builder import demultiplexed_targets_to_pmo_dict


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
        df,
        panel_id,
        target_genome_info,
        target_name_col=field_mapping["target_name"],
        forward_primers_seq_col=field_mapping["forward_primer_seq"],
        reverse_primers_seq_col=field_mapping["reverse_primer_seq"],
        forward_primers_start_col=optional_fields.get("forward_primers_start"),
        forward_primers_end_col=optional_fields.get("forward_primers_end"),
        reverse_primers_start_col=optional_fields.get("reverse_primers_start"),
        reverse_primers_end_col=optional_fields.get("reverse_primers_end"),
        insert_start_col=optional_fields.get("insert_start"),
        insert_end_col=optional_fields.get("insert_end"),
        chrom_col=optional_fields.get("chrom_col"),
        strand_col=optional_fields.get("strand"),
        gene_name_col=optional_fields.get("gene_name"),
        target_attributes_col=optional_fields.get("target_attributes"),
        additional_target_info_cols=additional_target_info_cols,
    )
    return transformed_df


def transform_specimen_info(
    df, field_mapping, optional_field_mapping, additional_fields=None
):
    transformed_df = specimen_info_table_to_pmo(
        df,
        specimen_name_col=field_mapping["specimen_name"],
        specimen_taxon_id_col=field_mapping["specimen_taxon_id"],
        host_taxon_id_col=field_mapping["host_taxon_id"],
        collection_date_col=field_mapping["collection_date"],
        collection_country_col=field_mapping["collection_country"],
        project_name_col=field_mapping["project_name"],
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
        host_subject_id=optional_field_mapping.get("host_subject_id"),
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
        list_values_specimen_columns_delimiter=",",
    )
    return transformed_df


def transform_library_sample_info(
    df, field_mapping, optional_mapping, additional_fields=None
):
    transformed_df = library_sample_info_table_to_pmo(
        df,
        library_sample_name_col=field_mapping["library_sample_name"],
        sequencing_info_name_col=field_mapping["sequencing_info_name"],
        specimen_name_col=field_mapping["specimen_name"],
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
    return transformed_df


# def transform_demultiplexed_info(df, bioinfo_id, field_mapping,
#                                  optional_mapping, additional_hap_detected_cols=None):
#     """Reformat the DataFrame based on the provided field mapping."""
#     transformed_df = demultiplexed_targets_to_pmo_dict(
#         df,
#         bioinfo_id,
#         sampleID_col=field_mapping["sampleID"],
#         target_id_col=field_mapping['target_id'],
#         read_count_col=field_mapping['raw_read_count'],
#         additional_hap_detected_cols=additional_hap_detected_cols)
#     return transformed_df
