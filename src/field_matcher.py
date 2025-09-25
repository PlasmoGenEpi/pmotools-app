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


# def reverse_fuzzy_match_fields(field_names, target_schema, alternate_schema_names=None):
#     """
#     modeled after fuzzy_match_fields, except instead of finding the column that
#     best matches each argument (or its alternate) this version finds the best
#     argument to match against each column. In practice, because this version
#     is keyed by columns instead of arguments, this means that all arguments (and
#     their alternates) need to be loaded as a flattened list - any matched
#     alternates are then mapped back to their 'primary' argument match.
#     """
#     matches = {}

#     # Build lookup of all options -> canonical name
#     if alternate_schema_names:
#         all_target_options = {}
#         for primary, alternates in alternate_schema_names.items():
#             all_target_options[primary] = primary
#             for alt in alternates:
#                 all_target_options[alt] = primary
#     else:
#         all_target_options = {k: k for k in target_schema}

#     # Do fuzzy matching
#     for field_name in field_names:
#         best_match, score = process.extractOne(
#             field_name, all_target_options.keys())
#         matches[field_name] = all_target_options[best_match]

#     return matches


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
    duplicates = duplicates-set(['no match', None])
    if duplicates:
        st.error(f"These items are mapped to the same thing: {duplicates} You"
                 " need to fix your mappings so that each field from your input file"
                 " maps to a unique field name from the PMO format (or check the box"
                 ' for "no match" if there is no good match) and try again.')
#        raise ValueError(
 #           f"Duplicate target schema fields found: {duplicates}")
        return False
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


def fuzzy_field_matching_page_section(input_fields, target_schema, alternate_schema_names=None):
    st.subheader("Match Fields")
    field_mapping, unused_field_names = fuzzy_match_fields(
        input_fields, target_schema, alternate_schema_names
    )
    st.write("Suggested Field Mapping:")
    st.dataframe(field_mapping_json_to_table(field_mapping))
    return field_mapping, unused_field_names


def interactive_field_mapping_page_section(field_mapping, df_columns, toggle_name="Manually Alter Field Mapping"):
    interactive_field_mapping_on = st.toggle(
        toggle_name)
    if interactive_field_mapping_on:
        updated_mapping = interactive_field_mapping(
            field_mapping, df_columns)
        st.write("Updated Field Mapping:")
        st.dataframe(field_mapping_json_to_table(updated_mapping))
        no_duplicates(updated_mapping)
        return updated_mapping
    return field_mapping


def add_optional_fields(unused_field_names, optional_schema,
                        optional_alternate_schema):
    mapped_fields = {key: None for key in optional_schema}
    additional_fields = []

    if unused_field_names:  # and optional_schema:
        st.subheader("Add Optional Fields")
        # new_df = df[unused_field_names]

        # Fuzzy field matching optional arguments
        reverse_field_mapping = reverse_fuzzy_match_fields(
            unused_field_names, optional_schema, optional_alternate_schema)
        st.write('Some of the fields in your table may match to one of our'
                 ' suggested "optional fields".')
        if optional_schema:
            st.write(f'our "optional fields" are {optional_schema}')
        else:
            st.write('For this panel, we have no optional fields')
        st.write('Check the boxes of any fields you would like to include in'
                 ' the final PMO. You can also include fields that are not in our'
                 ' suggested optional fields.')
        checkbox_states = {}
        for user_column in reverse_field_mapping:
            pmo_argument = reverse_field_mapping[user_column]
            checkbox_states[user_column] = st.checkbox(label=f'{user_column}')
        st.subheader("Edit Selected Optional Field Mappings")
        st.write('You can edit these mappings or include them without mapping'
                 " them to any of the suggested fields.")
        st.write('Our suggested mappings are below, with your column name on'
                 ' the lefthand side and the suggested optional field name on the'
                 ' right.')
        selected_mapping = {}
        for user_column in checkbox_states:
            if checkbox_states[user_column]:
                selected_mapping[user_column] = reverse_field_mapping[user_column]
                pmo_argument = reverse_field_mapping[user_column]
                if checkbox_states[user_column]:
                    edit_column = st.toggle(
                        f"Edit {user_column} --> {pmo_argument} mapping")
                    no_map = None
                    if edit_column:
                        selected_mapping[user_column] = st.selectbox(
                            f"Select optional argument match for {user_column}",
                            options=optional_schema, index=optional_schema.index(
                                user_column) if user_column in optional_schema else 0)
                        no_map = st.checkbox(
                            label=f'{user_column} has no good "optional argument" match but I still want to include it in the final PMO')
                        if no_map:
                            selected_mapping[user_column] = 'no match'
                    if no_map or reverse_field_mapping[user_column] == 'no match':
                        additional_fields.append(user_column)
        if no_duplicates(selected_mapping):
            for user_column, pmo_argument in selected_mapping.items():
                if pmo_argument != 'no match':
                    mapped_fields[pmo_argument] = user_column
                    print('after no duplicates check, mapped fields is',
                          mapped_fields)
        else:
            print(
                'duplicates found, ending optional_func, mapped fields reported as error')
            return 'Error', 'Error'
    print('at end of optional_func, optional fields is now', mapped_fields)
    return mapped_fields, additional_fields


def field_mapping(input_fields, target_schema, target_alternate_schema):
    # Fuzzy field matching required arguments
    mapped_fields, unused_field_names = fuzzy_field_matching_page_section(
        input_fields, target_schema, target_alternate_schema)

    # Interactive field mapping
    mapped_fields = interactive_field_mapping_page_section(
        mapped_fields, input_fields)
    return mapped_fields, unused_field_names


def load_data(target_schema, target_alternate_schema, optional_field_schema,
              optional_field_alternate_schema):
    st.subheader("Upload File")
    uploaded_file = st.file_uploader("Upload a TSV file", type=[
                                     "csv", "tsv", "xlsx", "xls", "txt"])
    df, mapped_fields, selected_optional_fields, selected_additional_fields = None, None, None, None
    if uploaded_file:
        df = load_csv(uploaded_file)
        interactive_preview = st.toggle("Preview File")
        if interactive_preview:
            st.write("Uploaded File Preview:")
            st.dataframe(df)
        st.subheader("Required Fields")
        mapped_fields, unused_field_names = field_mapping(df.columns.tolist(), target_schema,
                                                          target_alternate_schema)
        # Add optional and additional fields
        st.subheader("Optional Fields")
        mapped_fields, unused_field_names = field_mapping(unused_field_names, optional_field_schema,
                                                          optional_field_alternate_schema)
        # selected_optional_fields, selected_additional_fields = add_optional_fields(
        #     unused_field_names, optional_field_schema, optional_field_alternate_schema)
        # field_mapping()
    return df, mapped_fields, selected_optional_fields, selected_additional_fields
