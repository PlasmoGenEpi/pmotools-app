from fuzzywuzzy import process
from collections import Counter
import pandas as pd
import streamlit as st
from src.data_loader import load_csv


def fuzzy_match_fields(field_names, target_schema, alternate_schema_names=None):
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

    # For every target find the best matching field
    # TODO: Think about whether to allow multiple matches from a single field.
    for target in target_schema:
        best_match = process.extractOne(target, field_names)
        if alternate_schema_names:
            alt_targets = alternate_schema_names[target]
            for alt_target in alt_targets:
                alt_match = process.extractOne(alt_target, field_names)
                if alt_match[1] > best_match[1]:
                    best_match = alt_match
        best_match_field = best_match[0]
        matches[target] = best_match_field
    # Find unused field names
    unused_field_names = list(set(field_names)-set(matches.values()))
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
    if 'no match' in duplicates:
        duplicates.remove('no match')
    if duplicates:
        st.error(f"Duplicate target schema fields found: {duplicates}")
#        raise ValueError(
 #           f"Duplicate target schema fields found: {duplicates}")

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


def fuzzy_field_matching_page_section(df, target_schema, alternate_schema_names=None):
    st.subheader("Match Fields")
    field_mapping, unused_field_names = fuzzy_match_fields(
        df.columns.tolist(), target_schema, alternate_schema_names
    )
    st.write("Suggested Field Mapping:")
    st.dataframe(field_mapping_json_to_table(field_mapping))
    return field_mapping, unused_field_names


def interactive_field_mapping_page_section(field_mapping, df_columns, toggle_name="Manually Alter Field Mapping"):
    df_columns+=['no match']
    interactive_field_mapping_on = st.toggle(
        toggle_name)
    if interactive_field_mapping_on:
        updated_mapping = interactive_field_mapping(
            field_mapping, df_columns)
        st.write("Updated Field Mapping:")
        st.dataframe(field_mapping_json_to_table(updated_mapping))
        check_for_duplicates(updated_mapping)
        return updated_mapping
    return field_mapping

def add_optional_fields(df, unused_field_names, optional_schema,
    optional_alternate_schema):
    mapped_fields = {key:None for key in optional_schema}
    if unused_field_names and optional_schema:
        st.subheader("Add Optional Fields")
        new_df=df[unused_field_names]
        # Fuzzy field matching optional arguments
        mapped_fields, junk = fuzzy_field_matching_page_section(new_df,
            optional_schema, optional_alternate_schema)
        #Interactive field mapping optional arguments
        mapped_fields = interactive_field_mapping_page_section(
            mapped_fields, new_df.columns.tolist(), "Manually Alter Field Mapping of optional arguments")
    for key in mapped_fields:
        if mapped_fields[key]=='no match':
            mapped_fields[key]=None
    remaining_unused=list(set(unused_field_names)-set(mapped_fields.values()))
    return mapped_fields, remaining_unused

def add_additional_fields(unused_field_names):
    st.subheader("Add Additional Fields")
    selected_additional_fields = None
    if unused_field_names:
        optional_additional_fields = st.toggle("Add additional fields")
        if optional_additional_fields:
            checkbox_states = {}
            st.write("Select the extra columns you would like to include:")
            for item in unused_field_names:
                checkbox_states[item] = st.checkbox(label=item)
            selected_additional_fields = [
                key for key, value in checkbox_states.items() if value]
            st.write("You selected:", selected_additional_fields)
    return selected_additional_fields

def field_mapping(df, target_schema, target_alternate_schema):
    # Fuzzy field matching required arguments
    mapped_fields, unused_field_names = fuzzy_field_matching_page_section(
        df, target_schema, target_alternate_schema)

    # Interactive field mapping
    mapped_fields = interactive_field_mapping_page_section(
        mapped_fields, df.columns.tolist())
    return mapped_fields, unused_field_names

def load_data(target_schema, target_alternate_schema, optional_schema,
    optional_alternate_schema):
    st.subheader("Upload File")
    uploaded_file=st.file_uploader("Upload a TSV file", type=["csv", "tsv", "xlsx", "xls", "txt"])
    df, mapped_fields, selected_optional_fields, selected_additional_fields=None, None, None, None
    if uploaded_file:
        df = load_csv(uploaded_file)
        interactive_preview = st.toggle("Preview File")
        if interactive_preview:
            st.write("Uploaded File Preview:")
            st.dataframe(df)
        mapped_fields, unused_field_names = field_mapping(df, target_schema,
            target_alternate_schema)
        # Add optional fields
        selected_optional_fields, unused_field_names = add_optional_fields(df,
            unused_field_names, optional_schema, optional_alternate_schema)
        # Add additional fields
        selected_additional_fields = add_additional_fields(unused_field_names)
    return df, mapped_fields, selected_optional_fields, selected_additional_fields
