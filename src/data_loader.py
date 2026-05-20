import pandas as pd
import gzip
import io


def load_csv(file):
    """Load a CSV file into a pandas DataFrame with automatic separator detection."""
    try:
        filename = file.name

        if filename.endswith((".csv", ".tsv", ".txt")):
            df = pd.read_csv(file, sep=None, engine="python")

        elif filename.endswith((".csv.gz", ".tsv.gz", ".txt.gz", ".gz", ".gzip")):
            with gzip.open(io.BytesIO(file.read()), "rt", encoding="utf-8") as f:
                df = pd.read_csv(f, sep=None, engine="python")

        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file)

        else:
            raise ValueError(
                "Unsupported file format. Please upload a CSV, TSV, or Excel file."
            )
        return df

    except Exception as e:
        raise ValueError(f"Failed to read CSV: {e}")
