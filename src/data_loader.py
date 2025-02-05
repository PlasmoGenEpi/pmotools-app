import pandas as pd


def load_csv(file):
    """Load a CSV file into a pandas DataFrame."""
    try:
        if file.name.endswith((".csv", ".tsv", ".txt")):
            df = pd.read_csv(file, sep="\t")
        elif file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file)
        else:
            raise ValueError(
                "Unsupported file format. Please upload a CSV, TSV, or Excel file.")
        return df

    except Exception as e:
        raise ValueError(f"Failed to read CSV: {e}")
