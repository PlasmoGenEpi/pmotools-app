from fuzzywuzzy import process
from collections import Counter
import pandas as pd
import streamlit as st


def fuzzy_match_fields(field_names, target_schema):
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
    matches = {}
    unused_field_names = []  # To store any unused field names

    for field in field_names:
        # TODO: change this so it's not dependent on order. Maximise across scores.
        best_match = process.extractOne(field, target_schema)
        best_match_field = best_match[0]

        # Check if the best match has already been used
        if best_match_field not in matches.keys():
            matches[best_match_field] = field
        else:
            unused_field_names.append(field)

    return matches, unused_field_names


def check_for_duplicates(field_mapping):
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
    if duplicates:
        raise ValueError(
            f"Duplicate target schema fields found: {duplicates}")

    return True


def interactive_field_mapping(field_mapping, df_columns):
    updated_mapping = {}

    for field, suggested_match in field_mapping.items():
        # Use streamlit widgets to allow the user to select a match from df columns
        if isinstance(suggested_match, list):  # For multiple possible matches
            updated_mapping[field] = st.selectbox(
                f"Select match for {field}",
                options=df_columns,
                index=df_columns.index(
                    suggested_match[0]) if suggested_match else 0
            )
        else:
            updated_mapping[field] = st.selectbox(
                f"Modify match for {field}",
                options=df_columns,
                index=df_columns.index(
                    suggested_match) if suggested_match else 0
            )

    return updated_mapping


def field_mapping_json_to_table(mapping):
    data = [{"PMO Field": key, "Input Field": value}
            for key, value in mapping.items()]
    df = pd.DataFrame(data)
    return df


def fuzzy_field_matching_page_section(df, target_schema):
    st.subheader("Match Fields")
    field_mapping, unused_field_names = fuzzy_match_fields(
        df.columns.tolist(), target_schema
    )
    st.write("Suggested Field Mapping:")
    st.dataframe(field_mapping_json_to_table(field_mapping))
    return field_mapping, unused_field_names


def interactive_field_mapping_page_section(field_mapping, df_columns):
    interactive_field_mapping_on = st.toggle(
        "Manually Alter Field Mapping")
    if interactive_field_mapping_on:
        updated_mapping = interactive_field_mapping(
            field_mapping, df_columns)
        st.write("Updated Field Mapping:")
        st.dataframe(field_mapping_json_to_table(updated_mapping))
        check_for_duplicates(updated_mapping)
        return updated_mapping
    return field_mapping
