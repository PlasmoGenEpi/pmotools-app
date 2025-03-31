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

def reverse_fuzzy_match_fields(field_names, target_schema, alternate_schema_names=None):
    """
    modeled after fuzzy_match_fields, except instead of finding the column that
    best matches each argument (or its alternate) this version finds the best
    argument to match against each column. In practice, because this version
    is keyed by columns instead of arguments, this means that all arguments (and
    their alternates) need to be loaded as a flattened list).
    """
    argument_dict={target:target for target in target_schema}
    argument_list=target_schema[:]
    matches={}
    for target in alternate_schema_names:
        for alternate in alternate_schema_names[target]:
            argument_dict[alternate]=target
            argument_list.append(alternate)
    for field_name in field_names:
        name, score = process.extractOne(field_name, argument_list)
        matches[field_name] = argument_dict[name] #lookup the non-alternate best-matching argument
    return matches


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
        reverse_field_mapping = reverse_fuzzy_match_fields(
        new_df.columns.tolist(), optional_schema, optional_alternate_schema)
#        data = [{"user_column": key, "PMO Argument": value}
#        for key, value in reverse_field_mapping.items()]
#        df = pd.DataFrame(data)
        st.write('Some of the fields in your table may match to one of our'
            ' suggested "optional fields".')
        st.write('Check the boxes of any fields you would like to include in'
            ' the final PMO.')
        st.write('You can edit these mappings or include them without mapping'
            " them to any of the suggested fields.")
        st.write('Our suggested mappings are below, with your column name on'
            ' the lefthand side and the suggested optional field name on the'
            ' right.')

#        st.dataframe(df)
        checkbox_states = {}
        for user_column in reverse_field_mapping:
            pmo_argument=reverse_field_mapping[user_column]
            checkbox_states[user_column] = st.checkbox(label=f'{user_column} --> {pmo_argument}')
        st.subheader("Edit Selected Optional Field Mappings")
        updated_mapping={}
        for user_column in checkbox_states:
            pmo_argument=reverse_field_mapping[user_column]
            if checkbox_states[user_column]:
                edit_column = st.toggle(f"Edit {user_column} --> {pmo_argument} mapping")
                if edit_column:
                    updated_mapping[user_column] = st.selectbox(
                    f"Select optional argument match for {user_column}",
                    options=optional_schema, index=optional_schema.index(
                    user_column) if user_column in optional_schema else 0)
                    no_map=st.checkbox(label=f'{user_column} has no good "optional argument" match but I still want to include it in the final PMO')

        #selected_additional_fields = [
        #    key for key, value in checkbox_states.items() if value]


        #Interactive field mapping optional arguments
#        mapped_fields = interactive_field_mapping_page_section(
#            mapped_fields, new_df.columns.tolist(), "Manually Alter Field Mapping of optional arguments")
#    for key in mapped_fields:
#        if mapped_fields[key]=='no match':
#            mapped_fields[key]=None
#    remaining_unused=list(set(unused_field_names)-set(mapped_fields.values()))
#    return mapped_fields, remaining_unused

def add_additional_fields(unused_field_names):
    selected_additional_fields = None
    if unused_field_names:
        st.subheader("Add Additional Fields")
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
        add_optional_fields(df, unused_field_names, optional_schema,
            optional_alternate_schema)
#        selected_optional_fields, unused_field_names = add_optional_fields(df,
#            unused_field_names, optional_schema, optional_alternate_schema)

        # Add additional fields
        #selected_additional_fields = add_additional_fields(unused_field_names)
    return df, mapped_fields, selected_optional_fields, selected_additional_fields
