import pandas as pd
import io


def load_csv(file):
    """Load a CSV file into a pandas DataFrame."""
    try:
        df = pd.read_csv(file, sep='\t')
        return df
    except Exception as e:
        raise ValueError(f"Failed to read CSV: {e}")
