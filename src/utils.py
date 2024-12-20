import os


def save_to_csv(df, output_path):
    """Save a DataFrame to a CSV file."""
    df.to_csv(output_path, index=False)
    return output_path
