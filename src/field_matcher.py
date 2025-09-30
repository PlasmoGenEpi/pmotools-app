from fuzzywuzzy import process
from collections import Counter
import pandas as pd
import streamlit as st
from src.data_loader import load_csv


def fuzzy_match_fields(
    field_names,
    target_schema,
    alternate_schema_names=None,
    is_required: bool = True,
    match_threshold: int = 60,
):
    """
    Matches field names to the target schema using fuzzy matching, ensuring
    that each target schema field is only matched to one field name.

    Args:
        field_names (list): List of column names to be matched.
        target_schema (list): List of standard schema fields to match against.

    Returns:
        dict: A dictionary mapping each field name to the best-matched schema field.
        list: A list of unused field names that could not be matched.
    """
    # Initialize all targets with None to ensure full coverage in the table
    matches = {target: None for target in target_schema}
    # Track remaining available fields to enforce one-to-one mapping
    available_fields = set(field_names)

    # Error if not enough unique fields to match all targets
    if is_required and len(available_fields) < len(target_schema):
        st.error(
            "Not enough unique input fields to match all required schema fields. "
            f"Have {len(available_fields)} unique field(s) for {len(target_schema)} target(s)."
        )

    # For every target find the best matching unused field
    for target in target_schema:
        if not available_fields:
            # If no fields remain, required path already surfaced a global error above
            # For optional, we keep 'no match' as initialized
            continue

        remaining_fields = list(available_fields)
        best_match = process.extractOne(target, remaining_fields)

        if alternate_schema_names and target in alternate_schema_names:
            for alt_target in alternate_schema_names.get(target, []):
                alt_match = process.extractOne(alt_target, remaining_fields)
                if alt_match and best_match and alt_match[1] > best_match[1]:
                    best_match = alt_match

        if not best_match:
            # Leave as None
            continue

        best_match_field = best_match[0]
        best_score = best_match[1]

        if is_required:
            # Always take the best remaining field for required targets
            matches[target] = best_match_field
            available_fields.discard(best_match_field)
        else:
            # Only accept if above threshold; otherwise keep None
            if best_score >= match_threshold:
                matches[target] = best_match_field
                available_fields.discard(best_match_field)

    # Fields not used in matching
    unused_field_names = list(available_fields)
    return matches, unused_field_names


def no_duplicates(field_mapping):
    """
    Checks if there are any duplicate values in the dictionary.

    Args:
        field_mapping (dict): A dictionary mapping input field names to target schema fields.

    Returns:
        bool: True if no duplicates are found. Raises a ValueError if duplicates exist.
    """
    # Extract the values (target schema fields) from the dictionary
    counts = Counter(list(field_mapping.values()))
    duplicates = {item for item, count in counts.items() if count > 1}
    # Check for duplicates by comparing the length of the list to the length of the set
    duplicates = duplicates - set([None])
    if duplicates:
        st.error(
            f"These items are mapped to the same thing: {duplicates} You"
            " need to fix your mappings so that each field from your input file"
            " maps to a unique field name from the PMO format (or select"
            ' for "no match" if there is no good match) and try again.'
        )
        #        raise ValueError(
        #           f"Duplicate target schema fields found: {duplicates}")
        return False
    return True


def interactive_field_mapping(field_mapping, df_columns, is_required: bool = True):
    updated_mapping = {}

    # Add "no match" option to the available choices
    if is_required:
        options = df_columns
    else:
        options = ["no match"] + df_columns

    for field, suggested_match in field_mapping.items():
        # Use streamlit widgets to allow the user to select a match from df columns
        if isinstance(suggested_match, list):  # For multiple possible matches
            # Find the index in the options list
            try:
                index = options.index(suggested_match[0]) if suggested_match else 0
            except ValueError:
                index = 0  # Default to "no match" if not found

            selected = st.selectbox(
                f"Select match for {field}",
                options=options,
                index=index,
            )
        else:
            # Find the index in the options list
            try:
                index = options.index(suggested_match) if suggested_match else 0
            except ValueError:
                index = 0  # Default to "no match" if not found

            selected = st.selectbox(
                f"Modify match for {field}",
                options=options,
                index=index,
            )

        # Convert "no match" to None
        updated_mapping[field] = None if selected == "no match" else selected

    return updated_mapping


def field_mapping_json_to_table(mapping):
    data = [{"PMO Field": key, "Input Field": value} for key, value in mapping.items()]
    df = pd.DataFrame(data)
    return df


def fuzzy_field_matching_page_section(
    input_fields, target_schema, alternate_schema_names=None, is_required: bool = True
):
    st.subheader("Match Fields")
    field_mapping, unused_field_names = fuzzy_match_fields(
        input_fields, target_schema, alternate_schema_names, is_required=is_required
    )
    st.write("Suggested Field Mapping:")
    st.dataframe(field_mapping_json_to_table(field_mapping))
    return field_mapping, unused_field_names


def interactive_field_mapping_page_section(
    field_mapping,
    df_columns,
    toggle_name="Manually Alter Field Mapping",
    key_suffix: str = "",
    is_required: bool = True,
):
    unique_key = (
        f"interactive_field_mapping_{key_suffix}"
        if key_suffix
        else "interactive_field_mapping"
    )
    interactive_field_mapping_on = st.toggle(toggle_name, key=unique_key)
    if interactive_field_mapping_on:
        updated_mapping = interactive_field_mapping(
            field_mapping, df_columns, is_required=is_required
        )
        st.write("Updated Field Mapping:")
        st.dataframe(field_mapping_json_to_table(updated_mapping))
        no_duplicates(updated_mapping)

        # Calculate updated unused_field_names
        used_fields = {field for field in updated_mapping.values() if field is not None}
        updated_unused_field_names = [
            field for field in df_columns if field not in used_fields
        ]

        return updated_mapping, updated_unused_field_names
    return field_mapping, df_columns


def additional_fields_section(unused_field_names):
    """Show an Additional Fields section for unmatched input fields and allow selection."""
    selected_additional_fields = []
    if not unused_field_names:
        return selected_additional_fields

    st.subheader("Additional Fields")
    st.write(
        "The following fields from your input were not matched. Select any to include as additional fields in the final PMO file."
    )

    cols = st.columns(2) if len(unused_field_names) <= 6 else st.columns(3)
    for i, field in enumerate(unused_field_names):
        with cols[i % len(cols)]:
            include = st.checkbox(f"{field}", key=f"additional_{field}")
            if include:
                selected_additional_fields.append(field)

    if selected_additional_fields:
        st.success(
            f"Selected {len(selected_additional_fields)} additional field(s): {', '.join(selected_additional_fields)}"
        )

    return selected_additional_fields


def field_mapping(
    input_fields,
    target_schema,
    target_alternate_schema,
    key_suffix: str = "",
    is_required: bool = True,
):
    # Fuzzy field matching required arguments
    mapped_fields, unused_field_names = fuzzy_field_matching_page_section(
        input_fields, target_schema, target_alternate_schema, is_required=is_required
    )

    # Interactive field mapping
    mapped_fields, updated_unused_field_names = interactive_field_mapping_page_section(
        mapped_fields, input_fields, key_suffix=key_suffix, is_required=is_required
    )
    # Use updated unused_field_names if interactive mapping was used, otherwise use original
    final_unused_field_names = (
        updated_unused_field_names
        if updated_unused_field_names != input_fields
        else unused_field_names
    )

    return mapped_fields, final_unused_field_names


def load_data(
    target_schema,
    target_alternate_schema,
    optional_field_schema,
    optional_field_alternate_schema,
):
    # Load file
    st.subheader("Upload File")
    uploaded_file = st.file_uploader(
        "Upload a TSV file", type=["csv", "tsv", "xlsx", "xls", "txt"]
    )
    df, mapped_fields, selected_optional_fields, selected_additional_fields = (
        None,
        None,
        None,
        None,
    )
    if uploaded_file:
        df = load_csv(uploaded_file)
        interactive_preview = st.toggle("Preview File")
        if interactive_preview:
            st.write("Uploaded File Preview:")
            st.dataframe(df)

        # Required fields
        st.subheader("Required Fields")
        mapped_fields, unused_field_names = field_mapping(
            df.columns.tolist(),
            target_schema,
            target_alternate_schema,
            key_suffix="required",
            is_required=True,
        )
        # Optional fields
        st.subheader("Optional Fields")
        mapped_optional_fields, unused_field_names = field_mapping(
            unused_field_names,
            optional_field_schema,
            optional_field_alternate_schema,
            key_suffix="optional",
            is_required=False,
        )
        # Additional fields
        selected_additional_fields = additional_fields_section(unused_field_names)
        # For output, set selected_optional_fields to the optional mapping result
        selected_optional_fields = mapped_optional_fields

    return df, mapped_fields, selected_optional_fields, selected_additional_fields
