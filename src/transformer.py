from pmotools.json_convertors.microhaplotype_table_to_pmo_dict import microhaplotype_table_to_pmo_dict
from pmotools.json_convertors.panel_information_to_pmo_dict import panel_info_table_to_pmo_dict


def transform_mhap_info(df, bioinfo_id, field_mapping, additional_hap_detected_cols=None):
    """Reformat the DataFrame based on the provided field mapping."""
    transformed_df = microhaplotype_table_to_pmo_dict(
        df, bioinfo_id, sampleID_col=field_mapping["sampleID"], locus_col=field_mapping['locus'], mhap_col=field_mapping['asv'], reads_col=field_mapping['reads'], additional_hap_detected_cols=additional_hap_detected_cols)
    return transformed_df


def transform_panel_info(df, panel_id, field_mapping, target_genome_info, additional_target_info_cols=None):
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
