from pmotools.json_convertors.microhaplotype_table_to_pmo_dict import microhaplotype_table_to_pmo_dict
from pmotools.json_convertors.panel_information_to_pmo_dict import panel_info_table_to_pmo_dict
from pmotools.json_convertors.metatable_to_json_meta import experiment_info_table_to_json, specimen_info_table_to_json
from pmotools.json_convertors.demultiplexed_targets_to_pmo_dict import demultiplexed_targets_to_pmo_dict


def transform_mhap_info(df, bioinfo_id, field_mapping, optional_mapping,
    additional_hap_detected_cols=None):
    """Reformat the DataFrame based on the provided field mapping."""
    transformed_df = microhaplotype_table_to_pmo_dict(
        df,
        bioinfo_id,
        sampleID_col=field_mapping["sampleID"],
        locus_col=field_mapping['target_id'],
        mhap_col=field_mapping['asv'],
        reads_col=field_mapping['reads'],
        additional_hap_detected_cols=additional_hap_detected_cols)
    return transformed_df


def transform_panel_info(df, panel_id, field_mapping, target_genome_info,
    additional_target_info_cols=None):
    """Reformat the DataFrame based on the provided field mapping."""
    transformed_df = panel_info_table_to_pmo_dict(
        df,
        panel_id,
        target_genome_info,
        target_id_col=field_mapping["target_id"],
        forward_primers_seq_col=field_mapping["forward_primers"],
        reverse_primers_seq_col=field_mapping["reverse_primers"],
        additional_target_info_cols=additional_target_info_cols)
    return transformed_df


def transform_specimen_info(df, field_mapping, optional_field_mapping,
    additional_fields=None):
    print('optional field mapping is', optional_field_mapping)
    transformed_df = specimen_info_table_to_json(
        df,
        specimen_id_col=field_mapping["specimen_id"],
        samp_taxon_id=field_mapping["samp_taxon_id"],
        collection_date=field_mapping["collection_date"],
        collection_country=field_mapping["collection_country"],
        collector=field_mapping["collector"],
        samp_store_loc=field_mapping["samp_store_loc"],
        samp_collect_device=field_mapping["samp_collect_device"],
        project_name=field_mapping["project_name"],
        alternate_identifiers=optional_field_mapping['alternate_identifiers'],
        geo_admin1=optional_field_mapping['geo_admin1'],
        geo_admin2=optional_field_mapping['geo_admin2'],
        geo_admin3=optional_field_mapping['geo_admin3'],
        host_taxon_id=optional_field_mapping['host_taxon_id'],
        individual_id=optional_field_mapping['individual_id'],
        lat_lon=optional_field_mapping['lat_lon'],
        parasite_density=optional_field_mapping['parasite_density'],
        plate_col=optional_field_mapping['plate_col'],
        plate_name=optional_field_mapping['plate_name'],
        plate_row=optional_field_mapping['plate_row'],
        sample_comments=optional_field_mapping['sample_comments'],
        additional_specimen_cols=additional_fields
    )
    return transformed_df


def transform_experiment_info(df, field_mapping, optional_mapping,
    additional_fields=None):
    transformed_df = experiment_info_table_to_json(
        df,
        experiment_sample_id_col=field_mapping["experiment_sample_id"],
        sequencing_info_id=field_mapping["sequencing_info_id"],
        specimen_id=field_mapping["specimen_id"],
        panel_id=field_mapping["panel_id"],
        accession=optional_mapping["accession"],
        plate_col=optional_mapping["plate_col"],
        plate_name=optional_mapping["plate_name"],
        plate_row=optional_mapping["plate_row"],
        additional_experiment_cols=additional_fields
    )
    return transformed_df

def transform_demultiplexed_info(df, bioinfo_id, field_mapping,
    optional_mapping, additional_hap_detected_cols=None):
    """Reformat the DataFrame based on the provided field mapping."""
    transformed_df = demultiplexed_targets_to_pmo_dict(
        df,
        bioinfo_id,
        sampleID_col=field_mapping["sampleID"],
        target_id_col=field_mapping['target_id'],
        read_count_col=field_mapping['raw_read_count'],
        additional_hap_detected_cols=additional_hap_detected_cols)
    return transformed_df
