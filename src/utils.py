import json


def save_to_csv(df, output_path):
    """Save a DataFrame to a CSV file."""
    df.to_csv(output_path, index=False)
    return output_path


def load_schema():
    # Load schema field names from JSON
    with open('conf/schema.json', 'r') as file:
        schema_fields = json.load(file)
    return schema_fields
