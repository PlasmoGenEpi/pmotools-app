import json


def save_to_csv(df, output_path):
    """Save a DataFrame to a CSV file."""
    df.to_csv(output_path, index=False)
    return output_path


def load_schema():
    # Load schema field names from JSON
    with open("conf/schema.json", "r") as file:
        schema_fields = json.load(file)
    return schema_fields


def parse_list_field(value):
    """
    Parse a string that looks like a list into an actual list.
    Splits on commas but respects quoted substrings (single or double quotes).
    Parses character by character, toggling in_quote when a quote is encountered.

    Examples:
        "[--illumina, '--qualThres 25,20']" -> ["--illumina", "--qualThres 25,20"]
        "--illumina, --paired" -> ["--illumina", "--paired"]
        "single_value" -> "single_value" (returned as-is if no list-like structure)
    """
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        stripped = stripped[1:-1].strip()
    elif "," not in stripped:
        return value

    tokens = []
    current = []
    in_quote = False
    quote_char = None

    for char in stripped:
        if char in ('"', "'"):
            if not in_quote:
                # entering a quoted section
                in_quote = True
                quote_char = char
                # don't append the quote char itself
            elif char == quote_char:
                # closing the quoted section
                in_quote = False
                quote_char = None
                # don't append the quote char itself
            else:
                # different quote char inside a quoted section — treat as literal
                current.append(char)
        elif char == "," and not in_quote:
            token = "".join(current).strip()
            if token:
                tokens.append(token)
            current = []
        else:
            current.append(char)

    # Don't forget the last token
    last = "".join(current).strip()
    if last:
        tokens.append(last)

    return tokens if len(tokens) > 1 else (tokens[0] if tokens else value)
